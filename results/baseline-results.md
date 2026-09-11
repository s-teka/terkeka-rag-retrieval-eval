# Baseline Results

**Generated:** 2026-09-11
**Retriever:** deterministic keyword-overlap retriever (`src/terkeka_rag_eval/retrieval.py`)
**Configuration:** `top_k = 3`
**Evaluation cases:** 8 (`data/eval_dataset.json`)
**Corpus:** 8 chunks (`data/documents/corpus.json`)

Regenerate with:

```bash
terkeka-rag-eval evaluate -k 3 --json results/baseline-results.json
```

> These are toy baseline results from the included example dataset and deterministic retriever. They are intended to demonstrate the evaluation methodology, not benchmark production RAG systems.

## Aggregate metrics

| Metric      | Score  |
|-------------|--------|
| Mean Recall@3 | 1.000 |
| MRR           | 0.938 |
| Mean NDCG@3   | 0.964 |

## Per-query results

| Query ID     | Recall@3 | MRR  | NDCG@3 | Top retrieved chunk    | Expected chunk(s)                          |
|--------------|----------|------|--------|-------------------------|---------------------------------------------|
| policy-001   | 1.000    | 1.00 | 1.000  | policy-cancel-01        | policy-cancel-01                             |
| policy-002   | 1.000    | 1.00 | 1.000  | policy-renew-01         | policy-renew-01                              |
| billing-001  | 1.000    | 1.00 | 1.000  | billing-refund-01       | billing-refund-01                            |
| security-001 | 1.000    | 1.00 | 1.000  | security-retention-01   | security-retention-01                        |
| security-002 | 1.000    | 1.00 | 1.000  | security-session-01     | security-session-01                          |
| support-001  | 1.000    | 1.00 | 1.000  | support-critical-01     | support-critical-01                          |
| policy-003   | 1.000    | 1.00 | 1.000  | policy-renew-01         | policy-cancel-01, policy-renew-01 (multi)    |
| support-002  | 1.000    | 0.50 | 0.710  | support-critical-01     | support-standard-01 (distractor top-ranked)  |

## Reading the `support-002` result

`support-002` is included deliberately. The question asks about a "lower priority, **non**-critical incident," but the deterministic lexical retriever has no notion of negation, so it still ranks `support-critical-01` (the Priority 1 chunk) above the actually relevant `support-standard-01` (the Priority 3 chunk) because the word "critical" appears in the question.

- **Recall@3 stays 1.0** — the correct chunk is still in the top 3.
- **MRR drops to 0.5** and **NDCG@3 drops to 0.71** — the correct chunk is not ranked first.

This is the retrieval-evaluation methodology working as intended: a single pass/fail "did it find something" check would miss this, but rank-sensitive metrics surface it. It is also the mechanism behind the article's core failure mode — see [`examples/wrong_retrieval.py`](../examples/wrong_retrieval.py) for what happens when an answer generator is handed this kind of misranked evidence.

## Notes

- Most direct queries retrieve the labeled chunk at rank 1.
- Repeated terms such as *notice*, *days*, *minutes*, and *critical* across unrelated policies create ranking ambiguity as the corpus grows — this is expected behavior for a simple keyword-overlap retriever, not a bug.
- Before publishing any measured numbers in a Terkeka article, regenerate this file from the repository version used for the article and document the environment and dataset version.
