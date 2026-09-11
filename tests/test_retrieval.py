import json
from pathlib import Path

from terkeka_rag_eval.evaluator import evaluate, load_chunks, load_eval_cases
from terkeka_rag_eval.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[1]


def test_cancellation_query_finds_expected_chunk():
    chunks = load_chunks(ROOT / "data/documents/corpus.json")
    results = retrieve("What is the cancellation notice period?", chunks, k=3)
    assert results[0].chunk_id == "policy-cancel-01"


def test_baseline_eval_has_all_queries():
    chunks = load_chunks(ROOT / "data/documents/corpus.json")
    cases = load_eval_cases(ROOT / "data/eval_dataset.json")
    report = evaluate(chunks, cases, k=3)
    assert report["summary"]["queries"] == len(cases)
    assert 0.0 <= report["summary"]["mean_recall@3"] <= 1.0
    assert 0.0 <= report["summary"]["mrr"] <= 1.0
    assert 0.0 <= report["summary"]["mean_ndcg@3"] <= 1.0
