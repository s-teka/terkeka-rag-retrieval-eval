# Contributing

This is a teaching-oriented companion repository. The goal is to stay small, reproducible,
and honest about what the results do and don't show.

## Workflow

1. Fork the repository and create a feature branch (`git checkout -b my-change`).
2. Keep pull requests small and focused on one change.
3. Open a PR against `main` describing what changed and why.

## Expectations for changes

1. Keep examples small and reproducible.
2. Add or update labeled evaluation cases (`data/eval_dataset.json`) intentionally when
   retrieval behavior changes — don't let the dataset drift out of sync with the code.
3. Add tests for any new or changed metric or retriever
   (`tests/test_metrics.py`, `tests/test_retrieval.py`).
4. Do not publish fabricated benchmark claims.
5. Document data provenance and licensing for any non-synthetic dataset. Evaluation cases
   added to this repository should be synthetic (fictional policies/products) or properly
   licensed — do not add copyrighted or proprietary text.
6. Keep measured results separate from opinions or hypotheses.
7. Never silently hand-edit `results/baseline-results.json` or `results/baseline-results.md`.
   If a code or dataset change affects retrieval behavior, regenerate them by actually
   running the evaluator:

   ```bash
   terkeka-rag-eval evaluate -k 3 --json results/baseline-results.json
   ```

   and update the Markdown table to match.
8. Document any non-obvious assumptions (e.g. relevance grading, tie-breaking behavior)
   in code comments or docs rather than leaving them implicit.
9. Never commit secrets, API keys, or credentials. This project requires none to run.
