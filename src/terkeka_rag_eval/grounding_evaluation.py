from __future__ import annotations

from typing import Sequence

from .answer_evaluation import normalize_text
from .models import DocumentChunk, GroundingEvaluation


def evaluate_grounding(
    expected_answer: str, retrieved_chunks: Sequence[DocumentChunk]
) -> GroundingEvaluation:
    """Deterministic textual-support check.

    Answers the question: "is the fact needed to produce the *correct*
    answer actually present in the text of the chunks that were retrieved?"

    This is deliberately independent of what the generator's answer text
    says. A generated answer can be textually correct (matches
    `expected_answer`) while the retrieved context does not contain that
    fact at all -- that gap is exactly what this function is meant to
    surface. See docs/answer-vs-retrieval.md.

    Grounding is evaluated by exact-text containment, not by chunk-ID
    overlap with the labeled relevant set (that is retrieval evaluation,
    see rag_contract.evaluate_retrieval). The two checks usually agree, but
    they can diverge -- e.g. a labeled-relevant chunk that paraphrases the
    fact instead of stating it verbatim -- which is why they are kept as
    separate evaluations instead of one.
    """
    haystack = normalize_text(" ".join(chunk.text for chunk in retrieved_chunks))
    needle = normalize_text(expected_answer)
    supported = bool(needle) and needle in haystack
    return GroundingEvaluation(passed=supported, answer_supported_by_context=supported)
