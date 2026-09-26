from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Sequence

from .evaluator import load_chunks
from .models import DocumentChunk, EvaluationCase, RAGEvaluationResult
from .rag_contract import evaluate_rag_case

DEFAULT_DOCUMENTS = "experiments/answer_vs_retrieval/documents.json"
DEFAULT_CASES = "experiments/answer_vs_retrieval/cases.json"


def load_experiment_corpus(path: str | Path = DEFAULT_DOCUMENTS) -> Dict[str, DocumentChunk]:
    return {chunk.chunk_id: chunk for chunk in load_chunks(path)}


def _case_from_row(case_id: str, row: dict) -> EvaluationCase:
    return EvaluationCase(
        case_id=case_id,
        question=row["question"],
        retrieved_chunk_ids=list(row["retrieved_chunk_ids"]),
        relevant_chunk_ids=list(row["relevant_chunk_ids"]),
        expected_answer=row["expected_answer"],
        generated_answer=row["generated_answer"],
        expected_failure_mode=row["expected_failure_mode"],
    )


def load_controlled_cases(path: str | Path = DEFAULT_CASES) -> List[EvaluationCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [_case_from_row(row["case_id"], row) for row in payload["cases"]]


def load_evidence_ablation_cases(path: str | Path = DEFAULT_CASES) -> List[EvaluationCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        _case_from_row(f"article02-ablation-{row['condition']}", row)
        for row in payload["evidence_ablation"]
    ]


def run_cases(
    cases: Sequence[EvaluationCase], corpus: Dict[str, DocumentChunk]
) -> List[RAGEvaluationResult]:
    return [evaluate_rag_case(case, corpus) for case in cases]


def result_to_dict(result: RAGEvaluationResult) -> dict:
    return {
        "case_id": result.case_id,
        "retrieval": {"pass": result.retrieval.passed},
        "grounding": {"pass": result.grounding.passed},
        "answer": {"pass": result.answer.passed},
        "overall": {"pass": result.overall_pass, "failure_mode": result.failure_mode},
    }


def run_article02_experiment(
    documents_path: str | Path = DEFAULT_DOCUMENTS,
    cases_path: str | Path = DEFAULT_CASES,
) -> dict:
    """Load fixtures, run the four controlled cases and the evidence-ablation
    experiment, and return a plain-dict report suitable for JSON output."""
    corpus = load_experiment_corpus(documents_path)
    controlled = run_cases(load_controlled_cases(cases_path), corpus)
    ablation = run_cases(load_evidence_ablation_cases(cases_path), corpus)
    return {
        "four_controlled_cases": [result_to_dict(r) for r in controlled],
        "evidence_ablation": [result_to_dict(r) for r in ablation],
    }


def _pf(value: bool) -> str:
    return "PASS" if value else "FAIL"


def _table(rows: Sequence[dict], first_column: str) -> List[str]:
    width = max([len(first_column)] + [len(row["case_id"]) for row in rows]) + 2
    lines = [f"{first_column:<{width}}{'Retrieval':<12}{'Grounding':<12}{'Answer':<10}{'Overall':<10}Failure Mode"]
    for row in rows:
        lines.append(
            f"{row['case_id']:<{width}}"
            f"{_pf(row['retrieval']['pass']):<12}"
            f"{_pf(row['grounding']['pass']):<12}"
            f"{_pf(row['answer']['pass']):<10}"
            f"{_pf(row['overall']['pass']):<10}"
            f"{row['overall']['failure_mode']}"
        )
    return lines


def format_summary(report: dict) -> str:
    lines: List[str] = ["Article 02 -- Answer Accuracy vs Retrieval Accuracy", ""]
    lines.append("Four controlled cases:")
    lines.extend(_table(report["four_controlled_cases"], "Case"))
    lines.append("")
    lines.append("Evidence ablation:")
    lines.extend(_table(report["evidence_ablation"], "Condition"))
    return "\n".join(lines)


def render_markdown_report(report: dict) -> str:
    lines: List[str] = []
    lines.append("# Article 02 Experimental Results")
    lines.append("")
    lines.append(
        "**Terkeka owns the explanation. This repository owns the experiment.**"
    )
    lines.append("")
    lines.append("## Experiment purpose")
    lines.append("")
    lines.append(
        "Demonstrate, with deterministic and reproducible fixtures, that a correct "
        "final answer does not prove that retrieval worked correctly. Four "
        "controlled cases isolate retrieval, grounding, and answer correctness as "
        "independent evaluation dimensions; an evidence-ablation experiment then "
        "varies only the retrieved evidence for the same question."
    )
    lines.append("")
    lines.append(
        "All fixtures are synthetic (`experiments/answer_vs_retrieval/`) and no "
        "external LLM, API key, or network access is used -- `generated_answer` "
        "values are explicitly labeled deterministic/simulated fixtures, not live "
        "model output."
    )
    lines.append("")
    lines.append("## Four controlled cases")
    lines.append("")
    lines.append("| Case | Retrieval | Grounding | Answer | Overall | Failure Mode |")
    lines.append("|------|-----------|-----------|--------|---------|--------------|")
    for row in report["four_controlled_cases"]:
        lines.append(
            f"| {row['case_id']} "
            f"| {_pf(row['retrieval']['pass'])} "
            f"| {_pf(row['grounding']['pass'])} "
            f"| {_pf(row['answer']['pass'])} "
            f"| {_pf(row['overall']['pass'])} "
            f"| {row['overall']['failure_mode']} |"
        )
    lines.append("")
    lines.append(
        "Case D (`article02-case-d`) is the primary Article 02 experiment. An "
        "answer-only evaluator would score it a success because the generated "
        "answer matches the expected answer. The retrieval-aware contract "
        "correctly rejects it: the retrieved evidence was the wrong plan's "
        "cancellation policy, so `overall.pass = false` with "
        "`failure_mode = CORRECT_ANSWER_WRONG_EVIDENCE`."
    )
    lines.append("")
    lines.append("## Evidence-ablation experiment")
    lines.append("")
    lines.append(
        "Same question and same deterministic `generated_answer` fixture "
        "(`\"30 days\"`) under three evidence conditions:"
    )
    lines.append("")
    lines.append("| Evidence | Retrieval | Grounding | Answer | Failure Mode |")
    lines.append("|----------|-----------|-----------|--------|--------------|")
    for row in report["evidence_ablation"]:
        condition = row["case_id"].removeprefix("article02-ablation-")
        lines.append(
            f"| {condition} "
            f"| {_pf(row['retrieval']['pass'])} "
            f"| {_pf(row['grounding']['pass'])} "
            f"| {_pf(row['answer']['pass'])} "
            f"| {row['overall']['failure_mode']} |"
        )
    lines.append("")
    lines.append("## Key observation")
    lines.append("")
    lines.append(
        "The `generated_answer` fixture is identical (`\"30 days\"`) across all "
        "three evidence conditions, yet `answer.pass` is `true` in every row. "
        "Answer correctness alone does not distinguish correct evidence from "
        "wrong evidence from no evidence at all -- only the retrieval and "
        "grounding checks do."
    )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Comparing the `correct_evidence` row to the `no_evidence` row shows the "
        "same question producing the same correct answer with and without "
        "retrieved evidence. This does **not** prove retrieval is globally "
        "unnecessary -- it demonstrates only that, for this test case, answer "
        "correctness does not by itself prove retrieval was effective or even "
        "used."
    )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    for item in [
        "This experiment uses deterministic synthetic fixtures, not live model output.",
        "It does not measure real LLM accuracy or claim to benchmark any model.",
        "It does not claim every correct answer after bad retrieval came from pretrained/prior knowledge -- that is simulated here, not measured.",
        "Real RAG systems may contain redundant evidence across multiple chunks.",
        "Multiple chunks can legitimately support the same answer.",
        "Real grounding evaluation can require human or model-based judgment; this repository uses exact-text containment instead, which is conservative and can itself miss valid paraphrased support (see the UNSUPPORTED_CORRECT_ANSWER case in tests/test_rag_contract.py).",
        "LLM-as-judge approaches introduce their own evaluation uncertainty and are intentionally not used here.",
        "The repository isolates these concepts for educational reproducibility, not as a production RAG evaluation system.",
    ]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Reproduction command")
    lines.append("")
    lines.append("```bash")
    lines.append(
        "terkeka-rag-eval article02 "
        "--json results/article-02-results.json "
        "--markdown results/article-02-results.md"
    )
    lines.append("```")
    lines.append("")
    return "\n".join(lines)
