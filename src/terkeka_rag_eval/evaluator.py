from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

from .metrics import ndcg_at_k, recall_at_k, reciprocal_rank
from .models import DocumentChunk, EvalCase
from .retrieval import retrieve


def load_chunks(path: str | Path) -> list[DocumentChunk]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return [DocumentChunk(**row) for row in rows]


def load_eval_cases(path: str | Path) -> list[EvalCase]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvalCase(**row) for row in rows]


def evaluate(chunks: Sequence[DocumentChunk], cases: Iterable[EvalCase], k: int = 3) -> dict:
    per_case = []
    for case in cases:
        results = retrieve(case.question, chunks, k=k)
        ids = [r.chunk_id for r in results]
        row = {
            "query_id": case.query_id,
            f"recall@{k}": recall_at_k(ids, case.relevant_chunk_ids, k),
            "mrr": reciprocal_rank(ids, case.relevant_chunk_ids),
            f"ndcg@{k}": ndcg_at_k(ids, case.relevance, k),
            "retrieved_ids": ids,
            "expected_ids": case.relevant_chunk_ids,
        }
        per_case.append(row)

    if not per_case:
        return {"summary": {}, "cases": []}

    summary = {
        "queries": len(per_case),
        f"mean_recall@{k}": mean(r[f"recall@{k}"] for r in per_case),
        "mrr": mean(r["mrr"] for r in per_case),
        f"mean_ndcg@{k}": mean(r[f"ndcg@{k}"] for r in per_case),
    }
    return {"summary": summary, "cases": per_case}
