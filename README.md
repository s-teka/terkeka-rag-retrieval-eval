# Terkeka RAG Retrieval Eval — Starter Repository v1

Companion repository for the Terkeka article **“When RAG Sounds Right but Retrieves Wrong.”**

The goal is to make a subtle RAG failure reproducible:

```text
Question → Retriever → Wrong Chunk → LLM → Confident Wrong Answer
```

and contrast it with:

```text
Question → Retriever → Correct Chunk → LLM → Grounded Answer
```

This repository deliberately keeps the first version small and deterministic. It focuses on **retrieval evaluation** rather than model-provider integration so engineers can see whether the evidence pipeline is working before adding an LLM.

## What is included

- A small synthetic document corpus
- A labeled retrieval evaluation dataset
- Deterministic keyword-based retrieval
- Recall@K, MRR and NDCG@K implementations
- A simple answer simulator to show how wrong evidence can produce a fluent wrong answer
- Automated tests
- Baseline evaluation results
- GitHub Actions CI

## Repository structure

```text
terkeka-rag-retrieval-eval/
├── README.md
├── LICENSE
├── pyproject.toml
├── data/
│   ├── documents/corpus.json
│   └── eval_dataset.json
├── docs/
│   ├── architecture.md
│   └── evaluation-methodology.md
├── diagrams/
│   └── rag-retrieval-failure.mmd
├── examples/
│   ├── correct_retrieval.py
│   └── wrong_retrieval.py
├── results/
│   └── baseline-results.md
├── src/terkeka_rag_eval/
│   ├── __init__.py
│   ├── cli.py
│   ├── evaluator.py
│   ├── metrics.py
│   ├── models.py
│   └── retrieval.py
└── tests/
    ├── test_metrics.py
    └── test_retrieval.py
```

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest
terkeka-rag-eval evaluate
```

Run the two examples:

```bash
python examples/correct_retrieval.py
python examples/wrong_retrieval.py
```

## Evaluation dataset contract

Each evaluation case names the expected evidence directly:

```json
{
  "query_id": "policy-001",
  "question": "What is the cancellation notice period?",
  "relevant_chunk_ids": ["policy-cancel-01"],
  "relevance": {"policy-cancel-01": 3},
  "expected_facts": ["Cancellation requires 30 days notice."]
}
```

That lets retrieval quality be measured independently from answer fluency.

## Metrics

### Recall@K
Did at least one expected relevant chunk appear in the top K retrieved chunks?

### MRR
How early did the first relevant chunk appear?

### NDCG@K
How well did the ranking order match graded relevance judgments?

## Core engineering lesson

A correct-looking answer is not proof of correct retrieval. Evaluate retrieval against labeled evidence before asking whether the final answer sounds right.

## Suggested next iterations

1. Add BM25, vector and hybrid retrievers.
2. Add reranking.
3. Add chunking experiments.
4. Add metadata-filter regression cases.
5. Add groundedness and citation evaluation.
6. Add a provider adapter for Bedrock or another LLM.
7. Add CI release thresholds for Recall@K/MRR/NDCG.

## License

MIT. See [LICENSE](LICENSE).
