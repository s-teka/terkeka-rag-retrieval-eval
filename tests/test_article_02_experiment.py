import json
from pathlib import Path

from terkeka_rag_eval.article02 import (
    load_controlled_cases,
    load_evidence_ablation_cases,
    load_experiment_corpus,
    run_article02_experiment,
    run_cases,
)
from terkeka_rag_eval.models import FailureMode

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "experiments" / "answer_vs_retrieval"

EXPECTED = json.loads((EXPERIMENT_DIR / "expected_results.json").read_text(encoding="utf-8"))


def test_four_controlled_cases_match_expected_results():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = load_controlled_cases(EXPERIMENT_DIR / "cases.json")
    assert {c.case_id for c in cases} == set(EXPECTED["cases"].keys())

    for result in run_cases(cases, corpus):
        expected = EXPECTED["cases"][result.case_id]
        assert result.retrieval.passed == expected["retrieval_pass"], result.case_id
        assert result.grounding.passed == expected["grounding_pass"], result.case_id
        assert result.answer.passed == expected["answer_pass"], result.case_id
        assert result.overall_pass == expected["overall_pass"], result.case_id
        assert result.failure_mode == expected["failure_mode"], result.case_id


def test_case_a_is_healthy_rag():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = {c.case_id: c for c in load_controlled_cases(EXPERIMENT_DIR / "cases.json")}
    result = run_cases([cases["article02-case-a"]], corpus)[0]
    assert result.overall_pass is True
    assert result.failure_mode == FailureMode.HEALTHY_RAG.value


def test_case_b_is_generation_failure():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = {c.case_id: c for c in load_controlled_cases(EXPERIMENT_DIR / "cases.json")}
    result = run_cases([cases["article02-case-b"]], corpus)[0]
    assert result.retrieval.passed is True
    assert result.overall_pass is False
    assert result.failure_mode == FailureMode.GENERATION_FAILURE.value


def test_case_c_is_retrieval_failure():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = {c.case_id: c for c in load_controlled_cases(EXPERIMENT_DIR / "cases.json")}
    result = run_cases([cases["article02-case-c"]], corpus)[0]
    assert result.retrieval.passed is False
    assert result.answer.passed is False
    assert result.overall_pass is False
    assert result.failure_mode == FailureMode.RETRIEVAL_FAILURE.value


def test_case_d_is_correct_answer_wrong_evidence():
    """The primary Article 02 experiment.

    An answer-only evaluator would call this case a success: the generated
    answer ("30 days") exactly matches the expected answer. But the
    retrieved evidence is Plan Beta's cancellation policy, not Plan Alpha's
    -- the evidence path is broken even though the answer looks right. The
    retrieval-aware contract must reject it.
    """
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = {c.case_id: c for c in load_controlled_cases(EXPERIMENT_DIR / "cases.json")}
    result = run_cases([cases["article02-case-d"]], corpus)[0]

    assert result.answer.passed is True, "the generated answer must look correct"
    assert result.retrieval.passed is False, "but the correct evidence was never retrieved"
    assert result.grounding.passed is False, "and the retrieved evidence does not support the answer"
    assert result.overall_pass is False, "a correct answer must not compensate for broken retrieval"
    assert result.failure_mode == FailureMode.CORRECT_ANSWER_WRONG_EVIDENCE.value


def test_evidence_ablation_matches_expected_results():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = load_evidence_ablation_cases(EXPERIMENT_DIR / "cases.json")

    for result in run_cases(cases, corpus):
        expected = EXPECTED["evidence_ablation"][result.case_id]
        assert result.retrieval.passed == expected["retrieval_pass"], result.case_id
        assert result.grounding.passed == expected["grounding_pass"], result.case_id
        assert result.answer.passed == expected["answer_pass"], result.case_id
        assert result.overall_pass == expected["overall_pass"], result.case_id
        assert result.failure_mode == expected["failure_mode"], result.case_id


def test_evidence_ablation_answer_is_constant_across_conditions():
    """The generated_answer fixture is identical across all three evidence
    conditions -- this is what makes the ablation experiment meaningful:
    answer correctness alone cannot distinguish the three conditions."""
    cases = load_evidence_ablation_cases(EXPERIMENT_DIR / "cases.json")
    generated_answers = {c.generated_answer for c in cases}
    assert generated_answers == {"30 days"}


def test_no_evidence_condition_is_insufficient_evidence():
    corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
    cases = {c.case_id: c for c in load_evidence_ablation_cases(EXPERIMENT_DIR / "cases.json")}
    result = run_cases([cases["article02-ablation-no_evidence"]], corpus)[0]
    assert result.retrieval.retrieved_chunk_ids == []
    assert result.overall_pass is False
    assert result.failure_mode == FailureMode.INSUFFICIENT_EVIDENCE.value


def test_run_article02_experiment_is_deterministic_across_runs():
    first = run_article02_experiment(EXPERIMENT_DIR / "documents.json", EXPERIMENT_DIR / "cases.json")
    second = run_article02_experiment(EXPERIMENT_DIR / "documents.json", EXPERIMENT_DIR / "cases.json")
    assert first == second


def test_run_article02_experiment_report_shape():
    report = run_article02_experiment(EXPERIMENT_DIR / "documents.json", EXPERIMENT_DIR / "cases.json")
    assert len(report["four_controlled_cases"]) == 4
    assert len(report["evidence_ablation"]) == 3
    for row in report["four_controlled_cases"] + report["evidence_ablation"]:
        assert set(row.keys()) == {"case_id", "retrieval", "grounding", "answer", "overall"}
