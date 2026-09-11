from __future__ import annotations

from dataclasses import dataclass
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
