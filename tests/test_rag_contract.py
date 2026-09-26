from terkeka_rag_eval.models import DocumentChunk, EvaluationCase, FailureMode
from terkeka_rag_eval.rag_contract import (
    classify_failure_mode,
    evaluate_rag_case,
    evaluate_retrieval,
)

PLAN_ALPHA = DocumentChunk(
    chunk_id="plan-alpha-cancel-01",
    title="Plan Alpha — Cancellation",
    text="Plan Alpha requires 30 days notice before cancellation takes effect.",
    metadata={},
)
PLAN_BETA = DocumentChunk(
    chunk_id="plan-beta-cancel-01",
    title="Plan Beta — Cancellation",
    text="Plan Beta requires 14 days notice before cancellation takes effect.",
    metadata={},
)
# Deliberately paraphrased instead of stating "30 days" verbatim, to exercise
# the case where retrieval's labeled-relevant chunk does not satisfy the
# stricter exact-text grounding check.
PLAN_GAMMA = DocumentChunk(
    chunk_id="plan-gamma-cancel-01",
    title="Plan Gamma — Cancellation",
    text="Plan Gamma agreements terminate with one calendar month notice.",
    metadata={},
)

CORPUS = {c.chunk_id: c for c in [PLAN_ALPHA, PLAN_BETA, PLAN_GAMMA]}


def make_case(**overrides) -> EvaluationCase:
    defaults = dict(
        case_id="test-case",
        question="What is the cancellation notice period?",
        retrieved_chunk_ids=["plan-alpha-cancel-01"],
        relevant_chunk_ids=["plan-alpha-cancel-01"],
        expected_answer="30 days",
        generated_answer="30 days",
        expected_failure_mode="HEALTHY_RAG",
    )
    defaults.update(overrides)
    return EvaluationCase(**defaults)


# --- retrieval evaluation -------------------------------------------------


def test_retrieval_pass_when_relevant_chunk_retrieved():
    result = evaluate_retrieval(["plan-alpha-cancel-01", "plan-beta-cancel-01"], ["plan-alpha-cancel-01"])
    assert result.passed is True


def test_retrieval_fail_when_relevant_chunk_missing():
    result = evaluate_retrieval(["plan-beta-cancel-01"], ["plan-alpha-cancel-01"])
    assert result.passed is False


def test_retrieval_fail_when_nothing_retrieved():
    result = evaluate_retrieval([], ["plan-alpha-cancel-01"])
    assert result.passed is False


# --- failure-mode classification precedence (all 8 states) ---------------


def test_classify_healthy_rag():
    assert (
        classify_failure_mode(retrieval_passed=True, grounding_passed=True, answer_passed=True, evidence_present=True)
        == FailureMode.HEALTHY_RAG
    )


def test_classify_generation_failure():
    assert (
        classify_failure_mode(retrieval_passed=True, grounding_passed=True, answer_passed=False, evidence_present=True)
        == FailureMode.GENERATION_FAILURE
    )


def test_classify_unsupported_correct_answer():
    assert (
        classify_failure_mode(retrieval_passed=True, grounding_passed=False, answer_passed=True, evidence_present=True)
        == FailureMode.UNSUPPORTED_CORRECT_ANSWER
    )


def test_classify_grounding_failure():
    assert (
        classify_failure_mode(retrieval_passed=True, grounding_passed=False, answer_passed=False, evidence_present=True)
        == FailureMode.GROUNDING_FAILURE
    )


def test_classify_correct_answer_wrong_evidence():
    assert (
        classify_failure_mode(retrieval_passed=False, grounding_passed=False, answer_passed=True, evidence_present=True)
        == FailureMode.CORRECT_ANSWER_WRONG_EVIDENCE
    )


def test_classify_retrieval_failure():
    assert (
        classify_failure_mode(retrieval_passed=False, grounding_passed=False, answer_passed=False, evidence_present=True)
        == FailureMode.RETRIEVAL_FAILURE
    )


def test_classify_insufficient_evidence_with_correct_answer():
    assert (
        classify_failure_mode(retrieval_passed=False, grounding_passed=False, answer_passed=True, evidence_present=False)
        == FailureMode.INSUFFICIENT_EVIDENCE
    )


def test_classify_insufficient_evidence_with_wrong_answer():
    assert (
        classify_failure_mode(retrieval_passed=False, grounding_passed=False, answer_passed=False, evidence_present=False)
        == FailureMode.INSUFFICIENT_EVIDENCE
    )


# --- overall contract: correct answer cannot compensate for failures -----


def test_correct_answer_cannot_override_retrieval_failure():
    case = make_case(
        retrieved_chunk_ids=["plan-beta-cancel-01"],
        generated_answer="30 days",
    )
    result = evaluate_rag_case(case, CORPUS)
    assert result.answer.passed is True
    assert result.retrieval.passed is False
    assert result.overall_pass is False
    assert result.failure_mode == FailureMode.CORRECT_ANSWER_WRONG_EVIDENCE.value


def test_correct_answer_cannot_override_grounding_failure():
    case = make_case(
        retrieved_chunk_ids=["plan-gamma-cancel-01"],
        relevant_chunk_ids=["plan-gamma-cancel-01"],
        generated_answer="30 days",
    )
    result = evaluate_rag_case(case, CORPUS)
    assert result.answer.passed is True
    assert result.retrieval.passed is True
    assert result.grounding.passed is False
    assert result.overall_pass is False
    assert result.failure_mode == FailureMode.UNSUPPORTED_CORRECT_ANSWER.value


def test_overall_contract_requires_all_three_components():
    healthy = evaluate_rag_case(make_case(), CORPUS)
    assert healthy.overall_pass is True

    for overrides in (
        {"generated_answer": "14 days"},
        {"retrieved_chunk_ids": ["plan-beta-cancel-01"]},
        {
            "retrieved_chunk_ids": ["plan-gamma-cancel-01"],
            "relevant_chunk_ids": ["plan-gamma-cancel-01"],
        },
    ):
        broken = evaluate_rag_case(make_case(**overrides), CORPUS)
        assert broken.overall_pass is False


# --- deterministic repeated execution --------------------------------------


def test_evaluate_rag_case_is_deterministic():
    case = make_case()
    first = evaluate_rag_case(case, CORPUS)
    second = evaluate_rag_case(case, CORPUS)
    assert first == second
