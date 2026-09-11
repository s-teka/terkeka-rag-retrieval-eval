from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, List, Sequence

from .models import DocumentChunk, RetrievalResult

_WORD = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(text)]


def keyword_score(query: str, chunk: DocumentChunk) -> float:
    """A deliberately simple deterministic lexical scoring function.

    It gives higher weight to repeated query terms and a small title bonus.
    The simplicity makes retrieval failures easy to inspect in an article/demo.
    """
    q = Counter(tokenize(query))
    body = Counter(tokenize(chunk.text))
    title = Counter(tokenize(chunk.title))

    score = 0.0
    for token, q_count in q.items():
        score += q_count * body[token]
        score += 0.35 * q_count * title[token]
    return score


def retrieve(query: str, chunks: Sequence[DocumentChunk], k: int = 3) -> List[RetrievalResult]:
    ranked = sorted(
        chunks,
        key=lambda c: (-keyword_score(query, c), c.chunk_id),
    )
    return [
        RetrievalResult(
            chunk_id=c.chunk_id,
            score=keyword_score(query, c),
            title=c.title,
            text=c.text,
        )
        for c in ranked[:k]
    ]


def retrieve_with_forced_wrong_chunk(
    query: str,
    chunks: Sequence[DocumentChunk],
    wrong_chunk_id: str,
    k: int = 3,
) -> List[RetrievalResult]:
    """Demonstration helper that places a known-wrong chunk first.

    This is not a production retriever. It exists only to reproduce the article's
    central failure mode in a deterministic, inspectable way.
    """
    base = retrieve(query, chunks, k=max(k, len(chunks)))
    wrong = next(r for r in base if r.chunk_id == wrong_chunk_id)
    others = [r for r in base if r.chunk_id != wrong_chunk_id]
    return [wrong] + others[: max(0, k - 1)]


def answer_from_top_chunk(question: str, results: Iterable[RetrievalResult]) -> str:
    """Tiny answer simulator used only to visualize evidence dependence."""
    top = next(iter(results), None)
    if top is None:
        return "I do not have enough evidence to answer."
    return (
        f"Based on the retrieved evidence, the answer is: {top.text} "
        f"[source={top.chunk_id}]"
    )
