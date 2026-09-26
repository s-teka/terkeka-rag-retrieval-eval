from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    title: str
    text: str
    metadata: Dict[str, str]


@dataclass(frozen=True)
class EvalCase:
    query_id: str
    question: str
    relevant_chunk_ids: List[str]
    relevance: Dict[str, int]
    expected_facts: List[str]


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: str
    score: float
    title: str
    text: str


# --- Article 02: answer accuracy vs. retrieval accuracy -----------------
#
# These models support a *diagnostic*, per-case evaluation contract that is
# distinct from the aggregate IR metrics above (Recall@K / MRR / NDCG@K).
# See docs/retrieval-aware-evaluation-contract.md for the full rationale.


class FailureMode(str, Enum):
    """Explicit taxonomy of retrieval-aware RAG evaluation outcomes.

    See rag_contract.classify_failure_mode for the precedence rules that
    map (retrieval, grounding, answer, evidence_present) to exactly one
    of these labels.
    """

    HEALTHY_RAG = "HEALTHY_RAG"
    RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"
    GENERATION_FAILURE = "GENERATION_FAILURE"
    GROUNDING_FAILURE = "GROUNDING_FAILURE"
    CORRECT_ANSWER_WRONG_EVIDENCE = "CORRECT_ANSWER_WRONG_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED_CORRECT_ANSWER = "UNSUPPORTED_CORRECT_ANSWER"


@dataclass(frozen=True)
class EvaluationCase:
    """A single controlled Article 02 fixture.

    `retrieved_chunk_ids` and `generated_answer` are fixed inputs for the
    experiment rather than the output of a live retriever/LLM call, so that
    each of the four controlled cases (and each evidence-ablation condition)
    is deterministic and reproducible offline.
    """

    case_id: str
    question: str
    retrieved_chunk_ids: List[str]
    relevant_chunk_ids: List[str]
    expected_answer: str
    generated_answer: str
    expected_failure_mode: str


@dataclass(frozen=True)
class RetrievalEvaluation:
    passed: bool
    relevant_evidence_found: bool
    relevant_chunk_ids: List[str]
    retrieved_chunk_ids: List[str]


@dataclass(frozen=True)
class GroundingEvaluation:
    passed: bool
    answer_supported_by_context: bool


@dataclass(frozen=True)
class AnswerEvaluation:
    passed: bool
    expected_answer: str
    generated_answer: str


@dataclass(frozen=True)
class RAGEvaluationResult:
    case_id: str
    retrieval: RetrievalEvaluation
    grounding: GroundingEvaluation
    answer: AnswerEvaluation
    overall_pass: bool
    failure_mode: str
