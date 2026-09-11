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


def test_lexical_overlap_can_misrank_a_semantically_similar_distractor():
    """Documents a known limitation of the naive lexical retriever.

    The query negates "critical" ("non-critical incident") but the retriever
    has no notion of negation, so the critical-incident chunk still ranks
    above the actually-relevant standard-incident chunk. Recall@3 still
    succeeds (the right chunk is in the top 3), but it is not top-ranked,
    which is exactly the kind of retrieval risk this repository evaluates
    for instead of only checking whether an answer sounds right.
    """
    chunks = load_chunks(ROOT / "data/documents/corpus.json")
    cases = load_eval_cases(ROOT / "data/eval_dataset.json")
    case = next(c for c in cases if c.query_id == "support-002")

    results = retrieve(case.question, chunks, k=3)
    ranked_ids = [r.chunk_id for r in results]

    assert ranked_ids[0] == "support-critical-01"
    assert "support-standard-01" in ranked_ids
    assert ranked_ids.index("support-standard-01") > 0
