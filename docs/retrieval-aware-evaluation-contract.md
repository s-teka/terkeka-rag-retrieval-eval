# Retrieval-Aware Evaluation Contract

Companion documentation for Terkeka Article 02. Implementation:
[`src/terkeka_rag_eval/rag_contract.py`](../src/terkeka_rag_eval/rag_contract.py).

## Contract definition

```text
overall_pass = retrieval.passed AND grounding.passed AND answer.passed
```

This is a **logical AND**, not a weighted average or a score threshold.

## Why not a weighted average

A weighted average (e.g. `0.5 * answer + 0.3 * retrieval + 0.2 * grounding`)
lets a strong score on one component paper over a hard failure on another.
Article 02's entire point is that a correct answer must not be able to hide
a broken retriever — a weighted average would defeat that purpose by
construction, no matter how the weights are chosen. The contract uses AND
specifically so that any single failed component fails the whole case, with
no numeric threshold to tune around.

## Why answer correctness cannot compensate for retrieval or grounding failure

If `overall_pass` were `answer.passed` alone (or weighted mostly toward it),
`article02-case-d` — wrong evidence, correct answer — would report success.
That is precisely the failure mode this repository exists to make visible:
an apparently healthy RAG pipeline whose evidence path is actually broken,
undetectable until it hits a question the model cannot answer from prior
knowledge alone. See [`docs/answer-vs-retrieval.md`](answer-vs-retrieval.md).

## Classification rules

`classify_failure_mode` in `rag_contract.py` takes
`(retrieval_passed, grounding_passed, answer_passed, evidence_present)` and
returns exactly one `FailureMode`. The rules are evaluated in order — each
one only applies once every prior rule has been ruled out — so every
possible combination resolves to exactly one label:

| # | retrieval | grounding | answer | evidence present | → failure_mode |
|---|-----------|-----------|--------|-------------------|----------------|
| 1 | PASS | PASS | PASS | — | `HEALTHY_RAG` |
| 2 | FAIL | — | any | no | `INSUFFICIENT_EVIDENCE` |
| 3 | FAIL | — | PASS | yes (wrong evidence) | `CORRECT_ANSWER_WRONG_EVIDENCE` |
| 4 | FAIL | — | FAIL | yes (wrong evidence) | `RETRIEVAL_FAILURE` |
| 5 | PASS | FAIL | PASS | — | `UNSUPPORTED_CORRECT_ANSWER` |
| 6 | PASS | PASS | FAIL | — | `GENERATION_FAILURE` |
| 7 | PASS | FAIL | FAIL | — | `GROUNDING_FAILURE` |

Rows 2–4 split retrieval failure by whether *any* evidence was retrieved at
all (`INSUFFICIENT_EVIDENCE`) versus whether the *wrong* evidence was
retrieved (`RETRIEVAL_FAILURE` / `CORRECT_ANSWER_WRONG_EVIDENCE`) — a
generator that received nothing to work with is a different failure than
one that received the wrong chunk.

Rows 5–7 (`UNSUPPORTED_CORRECT_ANSWER`, `GROUNDING_FAILURE`) only occur when
retrieval passed (a labeled-relevant chunk was retrieved) but the
independent, stricter text-containment grounding check could not verify the
fact inside it — for example, a relevant chunk that paraphrases the answer
instead of stating it verbatim. See `tests/test_rag_contract.py` for
concrete fixtures exercising every row.

## Limitations

- Grounding here is exact-text containment, not semantic entailment. It can
  produce false negatives on legitimate paraphrases (`UNSUPPORTED_CORRECT_ANSWER`,
  `GROUNDING_FAILURE`) — a real system may need human or model-based
  judgment for grounding, which introduces its own uncertainty.
- Answer evaluation is exact-match after conservative normalization, not
  semantic equivalence. It intentionally does not use an LLM-as-judge.
- `retrieved_chunk_ids` and `generated_answer` are fixed experiment inputs
  in these fixtures, not the live output of a retriever or LLM call — the
  goal is to demonstrate the evaluation mechanics deterministically, not to
  benchmark a real system.
- Real RAG systems may have multiple chunks that legitimately support the
  same answer; this contract's grounding check does not distinguish
  "coincidentally contains the right words" from "was the actual basis for
  the answer."

See [`results/article-02-results.md`](../results/article-02-results.md) ·
[`Limitations`](../results/article-02-results.md#limitations) section for
the full list carried through to the experiment results.
