from __future__ import annotations

from typing import Dict, Sequence

from .answer_evaluation import evaluate_answer
from .grounding_evaluation import evaluate_grounding
from .metrics import recall_at_k
from .models import (
    DocumentChunk,
    EvaluationCase,
    FailureMode,
    RAGEvaluationResult,
    RetrievalEvaluation,
)


def evaluate_retrieval(
    retrieved_chunk_ids: Sequence[str], relevant_chunk_ids: Sequence[str]
) -> RetrievalEvaluation:
    """Per-case retrieval diagnostic: was *any* labeled-relevant chunk retrieved?

    This reuses the same labeled-relevance infrastructure as the Article 01
    aggregate metrics (`recall_at_k`), but answers a different question.
    Recall@K/MRR/NDCG@K (see metrics.py, evaluator.py) summarize retrieval
    quality *across* a dataset. `evaluate_retrieval` is a boolean pass/fail
    for a *single* case, used to gate the Article 02 contract below. Neither
    replaces the other.
    """
    found = recall_at_k(list(retrieved_chunk_ids), list(relevant_chunk_ids), k=len(retrieved_chunk_ids)) > 0
    return RetrievalEvaluation(
        passed=found,
        relevant_evidence_found=found,
        relevant_chunk_ids=list(relevant_chunk_ids),
        retrieved_chunk_ids=list(retrieved_chunk_ids),
    )


def classify_failure_mode(
    retrieval_passed: bool,
    grounding_passed: bool,
    answer_passed: bool,
    evidence_present: bool,
) -> FailureMode:
    """Map a (retrieval, grounding, answer, evidence_present) state to exactly
    one failure mode. Order matters -- each branch below is evaluated only
    after every prior branch has been ruled out, so every one of the 8
    possible (retrieval, grounding, answer) states resolves to exactly one
    label (with the retrieval-failed states further split by whether any
    evidence was retrieved at all):

    1. retrieval PASS, grounding PASS, answer PASS
       -> HEALTHY_RAG
    2. retrieval FAIL, no evidence retrieved at all, answer PASS or FAIL
       -> INSUFFICIENT_EVIDENCE
       (there was nothing to ground an answer in, regardless of what the
       generator produced)
    3. retrieval FAIL, wrong (non-empty) evidence retrieved, answer PASS
       -> CORRECT_ANSWER_WRONG_EVIDENCE
       (the headline Article 02 case: an answer-only evaluator would call
       this a success; the evidence path was still broken)
    4. retrieval FAIL, wrong (non-empty) evidence retrieved, answer FAIL
       -> RETRIEVAL_FAILURE
    5. retrieval PASS, grounding FAIL, answer PASS
       -> UNSUPPORTED_CORRECT_ANSWER
       (the labeled-relevant chunk was retrieved, but the exact-text
       grounding check could not verify the fact inside it -- e.g. a
       paraphrase -- even though the final answer is correct)
    6. retrieval PASS, grounding PASS, answer FAIL
       -> GENERATION_FAILURE
       (correct evidence was retrieved and does contain the needed fact,
       but the generator still produced the wrong final answer)
    7. retrieval PASS, grounding FAIL, answer FAIL
       -> GROUNDING_FAILURE

    A correct answer can never upgrade the result to HEALTHY_RAG or to
    overall_pass=True unless retrieval AND grounding also passed (see
    evaluate_rag_case). Rules 2 and 3 are exactly why: both have
    answer_passed=True but are classified as failures.
    """
    if retrieval_passed and grounding_passed and answer_passed:
        return FailureMode.HEALTHY_RAG

    if not retrieval_passed:
        if not evidence_present:
            return FailureMode.INSUFFICIENT_EVIDENCE
        if answer_passed:
            return FailureMode.CORRECT_ANSWER_WRONG_EVIDENCE
        return FailureMode.RETRIEVAL_FAILURE

    # retrieval_passed is True from here on.
    if grounding_passed:
        return FailureMode.GENERATION_FAILURE
    if answer_passed:
        return FailureMode.UNSUPPORTED_CORRECT_ANSWER
    return FailureMode.GROUNDING_FAILURE


def evaluate_rag_case(
    case: EvaluationCase, corpus: Dict[str, DocumentChunk]
) -> RAGEvaluationResult:
    """The core Article 02 contract:

        overall_pass = retrieval.passed AND grounding.passed AND answer.passed

    Intentionally not a weighted average. A correct answer must not be able
    to compensate for failed retrieval or failed grounding -- that
    compensation is precisely the failure mode this repository exists to
    make visible. See docs/retrieval-aware-evaluation-contract.md.
    """
    retrieval = evaluate_retrieval(case.retrieved_chunk_ids, case.relevant_chunk_ids)
    retrieved_chunks = [
        corpus[chunk_id] for chunk_id in case.retrieved_chunk_ids if chunk_id in corpus
    ]
    grounding = evaluate_grounding(case.expected_answer, retrieved_chunks)
    answer = evaluate_answer(case.expected_answer, case.generated_answer)

    overall_pass = retrieval.passed and grounding.passed and answer.passed
    failure_mode = classify_failure_mode(
        retrieval_passed=retrieval.passed,
        grounding_passed=grounding.passed,
        answer_passed=answer.passed,
        evidence_present=bool(case.retrieved_chunk_ids),
    )

    return RAGEvaluationResult(
        case_id=case.case_id,
        retrieval=retrieval,
        grounding=grounding,
        answer=answer,
        overall_pass=overall_pass,
        failure_mode=failure_mode.value,
    )
