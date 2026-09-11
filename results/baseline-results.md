# Baseline Results

Starter baseline for the deterministic lexical retriever.

Run:

```bash
terkeka-rag-eval evaluate -k 3
```

The included toy dataset is intentionally small. The purpose is not to claim a benchmark; it is to demonstrate the evaluation workflow and create a regression-testable baseline.

Expected qualitative outcome:

- Most direct queries retrieve the labeled chunk at rank 1.
- Similar terms such as *notice*, *period*, *response* or *days* can create ranking ambiguity as the corpus grows.
- The `wrong_retrieval.py` example intentionally forces the wrong top chunk to show how a fluent answer can still be grounded incorrectly.

Before publishing any measured numbers in a Terkeka article, regenerate this file from the repository version used for the article and document the environment and dataset version.
