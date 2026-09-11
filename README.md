# Terkeka RAG Retrieval Evaluation

Reproducible retrieval-evaluation examples for Terkeka Article 01 — *When RAG Sounds Right but Retrieves Wrong*.

**Terkeka owns the explanation. This repository owns the experiment.**

## Companion Article

**When RAG Sounds Right but Retrieves Wrong**

Canonical article: https://terkeka.com/articles/when-rag-sounds-right-but-retrieves-wrong/

> This repository is a companion implementation for a Terkeka engineering article. The article explains the engineering problem and reasoning; this repository provides the reproducible dataset, code, metrics, tests, and results.

## The Problem

A fluent or apparently correct answer does not prove that a RAG pipeline retrieved the correct evidence. A large language model can sound confident while being grounded in the wrong chunk — or in no real evidence at all.

**Failure path:**

```mermaid
flowchart LR
    Q[Question] --> R[Retriever]
    R --> W[Wrong Chunk]
    W --> L[LLM / Answer Generator]
    L --> A[Confident Wrong Answer]
```

**Success path:**

```mermaid
flowchart LR
    Q2[Question] --> R2[Retriever]
    R2 --> C[Correct Chunk]
    C --> L2[LLM / Answer Generator]
    L2 --> G[Grounded Answer]
```

Both paths can produce a fluent-sounding answer. Only retrieval evaluation tells you which path you were actually on.

## Why Retrieval Evaluation Matters

RAG quality is not one thing — it is several separable concerns:

- **Retrieval quality** — did the retriever surface the right evidence?
- **Grounding quality** — does the generated answer actually rely on that evidence?
- **Reasoning quality** — did the model reason correctly over the evidence it was given?
- **Answer quality** — does the final answer read as correct to a human reviewer?

**Answer accuracy is not retrieval accuracy.** A model's prior knowledge can produce a correct-sounding answer even when the retriever handed it the wrong chunk — or nothing useful at all. That's the dangerous case: wrong retrieval plus an apparently correct answer, which masks a broken retriever until it fails on a question the model can't answer from prior knowledge alone.

This repository isolates the first concern — retrieval quality — and evaluates it independently, against labeled evidence, before any answer is generated.

## What This Repository Evaluates

- Whether the correct document chunk(s) were identified for a given question
- **Recall@K** — did the top K results contain the relevant evidence?
- **MRR** — how early did the first relevant result appear?
- **NDCG@K** — how good was the ranking order of relevant results?
- Correct-vs-wrong retrieval behavior, including a real case where a semantically similar distractor outranks the correct chunk
- Regression testing over a small labeled dataset

## Repository Structure

```text
terkeka-rag-retrieval-eval/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── documents/corpus.json
│   └── eval_dataset.json
├── src/terkeka_rag_eval/
│   ├── __init__.py
│   ├── cli.py
│   ├── evaluator.py
│   ├── metrics.py
│   ├── models.py
│   └── retrieval.py
├── examples/
│   ├── correct_retrieval.py
│   └── wrong_retrieval.py
├── tests/
│   ├── test_metrics.py
│   └── test_retrieval.py
├── docs/
│   ├── architecture.md
│   └── evaluation-methodology.md
├── diagrams/
│   └── rag-retrieval-failure.mmd
└── results/
    ├── baseline-results.md
    └── baseline-results.json
```

## Quick Start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

pytest
terkeka-rag-eval evaluate
```

`terkeka-rag-eval evaluate` is the CLI entry point defined in [`src/terkeka_rag_eval/cli.py`](src/terkeka_rag_eval/cli.py). It loads the corpus and labeled dataset, runs retrieval, and prints a JSON report. Useful flags:

```bash
terkeka-rag-eval evaluate -k 3 --json results/latest.json
```

## Run the Examples

```bash
python examples/correct_retrieval.py
python examples/wrong_retrieval.py
```

- **`correct_retrieval.py`** runs the deterministic retriever normally and shows it ranking the correct chunk first, followed by a simulated grounded answer.
- **`wrong_retrieval.py`** forces a known-wrong chunk to the top of the ranking (via `retrieve_with_forced_wrong_chunk`) and shows that the same answer simulator still produces a fluent-sounding answer — demonstrating that answer appearance cannot be used as proof of retrieval correctness. No external LLM is called; the "answer" is a deterministic template over the top retrieved chunk.

## Evaluation Dataset

Each evaluation case is a labeled retrieval example, not a production dataset:

### Dataset Notice

All documents, queries, relevance labels, and evaluation examples in this repository are synthetic and were created solely for demonstrating retrieval and RAG evaluation techniques.

They are not derived from any production system, proprietary dataset, confidential information, or internal business process.

```json
{
  "query_id": "policy-001",
  "question": "What is the cancellation notice period?",
  "relevant_chunk_ids": ["policy-cancel-01"],
  "relevance": {"policy-cancel-01": 3},
  "expected_facts": ["Cancellation requires 30 days notice."]
}
```

`relevant_chunk_ids` is the binary relevant set used for Recall@K and MRR. `relevance` is a graded-relevance map used for NDCG@K — it can also score a topically related but incorrect chunk (a distractor) above zero without treating it as a correct answer. The dataset (`data/eval_dataset.json`) deliberately includes:

1. **Obvious correct retrieval** — direct questions with one unambiguous relevant chunk.
2. **A semantically similar distractor** — `support-002` asks about a "non-critical" incident; the retriever has no notion of negation and ranks the "critical" incident chunk first.
3. **A real wrong-retrieval risk** — the same `support-002` case: Recall@3 still succeeds (the right chunk is in the top 3), but MRR and NDCG@3 drop because it isn't ranked first.
4. **Multiple relevant chunks** — `policy-003` has two chunks that both answer the question.
5. **Ranking quality** — `support-002` again, since it is specifically a ranking-order failure, not a missing-evidence failure.

See [`results/baseline-results.md`](results/baseline-results.md) for the actual measured outcome of each case.

## Metrics

### Recall@K
Did the retriever find relevant evidence in the top K results? A binary hit/miss signal per relevant chunk, aggregated over the query.

### MRR
How early did the first relevant result appear? `1 / rank` of the first relevant chunk, `0` if none was found. Penalizes a correct chunk being buried behind irrelevant ones.

### NDCG@K
How good was the ranked ordering of relevant results, using graded relevance? Rewards putting more relevant chunks earlier, and can distinguish "correct but poorly ranked" from "correct and well ranked" — which Recall@K alone cannot.

Implementations: [`src/terkeka_rag_eval/metrics.py`](src/terkeka_rag_eval/metrics.py). Unit tests, including edge cases (no relevant results, K exceeding result length, divide-by-zero guards): [`tests/test_metrics.py`](tests/test_metrics.py).

## Baseline Results

> Toy baseline results from the included deterministic example corpus. These are not production benchmark claims.

Generated by actually running the evaluator against `data/eval_dataset.json` (8 cases, `top_k = 3`):

| Metric        | Score |
|---------------|-------|
| Mean Recall@3 | 1.000 |
| MRR           | 0.938 |
| Mean NDCG@3   | 0.964 |

MRR and NDCG@3 are below 1.0 specifically because of the `support-002` distractor case described above — the aggregate numbers reflect a real, reproducible ranking imperfection rather than a manufactured example. Full per-query results and commentary: [`results/baseline-results.md`](results/baseline-results.md) / [`results/baseline-results.json`](results/baseline-results.json).

## Architecture

```mermaid
flowchart LR
    Q[Question] --> R[Retriever]
    R --> C[Retrieved Chunks]
    C --> E[Retrieval Evaluator]
    C --> A[Answer Generator]
    A --> G[Answer / Grounding Evaluation]
    D[Labeled Evaluation Dataset] --> E
```

Retrieval evaluation (`C → E`) runs independently of answer generation (`C → A → G`). This is the core architectural principle: retrieval evaluation must not depend on whether the final answer merely *looks* correct. Both branches consume the same retrieved chunks, but only one of them is compared against labeled ground truth. See [`docs/architecture.md`](docs/architecture.md) for more detail.

## CI/CD

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every pull request and on pushes to `main`. It installs the project, runs `pytest`, and runs the evaluator against the labeled dataset, uploading the JSON report as a build artifact. It requires no secrets and no cloud credentials.

**Future goal (not yet implemented):** retrieval evaluation can become a regression gate for changes to chunking, embeddings, metadata filters, retrieval algorithms, reranking, or knowledge-base contents — failing CI if Recall@K/MRR/NDCG@K drop below an accepted baseline. See [`docs/evaluation-methodology.md`](docs/evaluation-methodology.md) for an example threshold policy.

## Educational Scope

v1 intentionally uses a deterministic, keyword-overlap retriever (see [`src/terkeka_rag_eval/retrieval.py`](src/terkeka_rag_eval/retrieval.py)) so readers can understand the evaluation mechanics without needing cloud credentials, API keys, a vector database, or a paid LLM API. It is explicitly **not** a production retrieval implementation — it exists to make retrieval evaluation reproducible in a few minutes on a laptop.

## Roadmap

### v1 — Retrieval Evaluation Foundation (this repository)
- Deterministic keyword-overlap retrieval
- Labeled evaluation dataset
- Recall@K, MRR, NDCG@K
- Correct/wrong retrieval demonstrations
- Automated tests
- CI

### v2 — Retrieval Strategy Comparison *(planned, not implemented)*
- BM25
- Embedding-based retrieval
- Hybrid retrieval
- Reranking
- Retrieval strategy comparison

### v3 — Production Evaluation *(planned, not implemented)*
- Larger, versioned datasets
- Experiment tracking
- Retrieval regression gates in CI
- Observability
- CI/CD thresholds

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

## About Terkeka

Terkeka is an engineering knowledge platform focused on AI, GenAI, RAG, evaluation, agentic systems, cloud architecture, and software engineering.

**Engineering Knowledge, Shared Forward.**
