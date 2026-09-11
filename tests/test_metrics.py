import pytest

from terkeka_rag_eval.metrics import ndcg_at_k, recall_at_k, reciprocal_rank


def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], ["b"], 2) == 1.0
    assert recall_at_k(["a", "b", "c"], ["c"], 2) == 0.0


def test_reciprocal_rank():
    assert reciprocal_rank(["a", "b", "c"], ["b"]) == 0.5
    assert reciprocal_rank(["a", "b"], ["x"]) == 0.0


def test_ndcg_at_k_perfect_is_one():
    score = ndcg_at_k(["a", "b"], {"a": 3, "b": 2}, 2)
    assert score == pytest.approx(1.0)


def test_ndcg_at_k_penalizes_bad_order():
    perfect = ndcg_at_k(["a", "b"], {"a": 3, "b": 2}, 2)
    reversed_score = ndcg_at_k(["b", "a"], {"a": 3, "b": 2}, 2)
    assert reversed_score < perfect
