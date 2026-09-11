from __future__ import annotations

import math
from typing import Mapping, Sequence


def recall_at_k(retrieved_ids: Sequence[str], relevant_ids: Sequence[str], k: int) -> float:
    relevant = set(relevant_ids)
    if not relevant:
        return 0.0
    found = relevant.intersection(retrieved_ids[:k])
    return len(found) / len(relevant)


def reciprocal_rank(retrieved_ids: Sequence[str], relevant_ids: Sequence[str]) -> float:
    relevant = set(relevant_ids)
    for idx, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / idx
    return 0.0


def _dcg(grades: Sequence[int]) -> float:
    total = 0.0
    for idx, grade in enumerate(grades, start=1):
        total += (2**grade - 1) / math.log2(idx + 1)
    return total


def ndcg_at_k(retrieved_ids: Sequence[str], relevance: Mapping[str, int], k: int) -> float:
    actual_grades = [int(relevance.get(chunk_id, 0)) for chunk_id in retrieved_ids[:k]]
    ideal_grades = sorted((int(v) for v in relevance.values()), reverse=True)[:k]
    ideal = _dcg(ideal_grades)
    if ideal == 0:
        return 0.0
    return _dcg(actual_grades) / ideal
