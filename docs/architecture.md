# Architecture

## Learning flow

```text
                   ┌─────────────────────┐
                   │ Labeled Eval Cases  │
                   │ question + expected │
                   │ evidence IDs        │
                   └──────────┬──────────┘
                              │
                              v
┌────────────┐      ┌─────────────────────┐      ┌───────────────────┐
│ Documents  │ ───> │ Retriever           │ ───> │ Ranked Chunk IDs  │
└────────────┘      └─────────────────────┘      └─────────┬─────────┘
                                                          │
                           ┌───────────────────────────────┘
                           v
                  ┌───────────────────────┐
                  │ Retrieval Evaluator   │
                  │ Recall@K / MRR / NDCG │
                  └───────────────────────┘
```

## Failure mode demonstrated

```text
Question → Retriever → Wrong Chunk → Answer Generator → Confident Wrong Answer
```

The critical design choice is that retrieval is scored against labeled evidence **before** answer quality is considered.

## Production evolution

A production-grade successor could replace the lexical retriever with adapters for:

- BM25
- vector search
- hybrid retrieval
- reranking
- metadata filtering
- managed knowledge-base retrieval

The evaluator contract can remain the same as long as each retriever returns ranked chunk identifiers.
