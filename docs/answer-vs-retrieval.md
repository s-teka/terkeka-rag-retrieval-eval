# Answer vs. Retrieval

Companion documentation for Terkeka Article 02 — *Why Answer Accuracy Is Not
Retrieval Accuracy*. See [`experiments/answer_vs_retrieval/`](../experiments/answer_vs_retrieval/)
for the runnable experiment this document describes.

## The pipeline, and where each evaluation attaches

```text
Question
  |
  v
Retriever
  |
  v
Retrieved Evidence ----> Retrieval Evaluation
  |                       (did the retriever surface the
  |                        labeled-relevant chunk?)
  v
Generator
  |
  v
Generated Answer ------> Answer Evaluation
       |                  (does the generated answer match
       |                   the expected answer?)
       |
       +----------------> Grounding Evaluation
                           (does the retrieved evidence text
                            actually contain the fact needed
                            to answer correctly?)
```

Then:

```text
Retrieval AND Grounding AND Answer
                 |
                 v
        Overall RAG Contract
```

## Why three separate checks

- **Retrieval evaluation** (`terkeka_rag_eval.rag_contract.evaluate_retrieval`)
  answers: was any labeled-relevant chunk actually retrieved? It reuses the
  same relevance labels as Article 01's Recall@K.
- **Grounding evaluation** (`terkeka_rag_eval.grounding_evaluation.evaluate_grounding`)
  answers a different question: does the *text* of what was actually
  retrieved contain the fact needed to produce the correct answer? A
  labeled-relevant chunk and a textually-verifiable supporting fact usually
  agree, but they are not the same check — see the `UNSUPPORTED_CORRECT_ANSWER`
  case in `tests/test_rag_contract.py` for where they diverge (a labeled
  chunk that paraphrases the fact instead of stating it verbatim).
- **Answer evaluation** (`terkeka_rag_eval.answer_evaluation.evaluate_answer`)
  answers only: does the generated answer match the expected answer? This
  is the check an answer-only evaluator would stop at — and exactly the
  check that cannot, by itself, tell you whether retrieval worked.

## Retrieval evaluation vs. aggregate IR metrics

Keep these two concepts distinct:

- **Aggregate IR metrics** (`terkeka_rag_eval.metrics`: Recall@K, MRR,
  NDCG@K) summarize retrieval quality across a labeled dataset. This is
  what Article 01 and `terkeka-rag-eval evaluate` measure.
- **Per-case diagnostic retrieval_pass** (`rag_contract.evaluate_retrieval`)
  is a boolean pass/fail for a single case, used to gate the Article 02
  contract. It reuses `recall_at_k` internally, but answers "did this one
  case pass?" rather than "how good is retrieval on average?"

Article 02 adds diagnostic, per-case evaluation. It does not replace or
change Recall@K/MRR/NDCG@K.

## The headline case

`article02-case-d`: the retrieved evidence is the wrong plan's policy, but
the generated answer still matches the expected answer (e.g. from prior
knowledge, or by chance). `answer.pass = true`. An answer-only evaluator
stops there and reports success. `retrieval.pass = false` and
`grounding.pass = false`, so the retrieval-aware contract reports
`overall.pass = false` with `failure_mode = CORRECT_ANSWER_WRONG_EVIDENCE`.

See [`docs/retrieval-aware-evaluation-contract.md`](retrieval-aware-evaluation-contract.md)
for the full classification rules and [`results/article-02-results.md`](../results/article-02-results.md)
for the measured output of all four cases and the evidence-ablation
experiment.
