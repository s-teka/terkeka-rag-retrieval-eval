# Answer vs. Retrieval — Article 02 Experiment

Companion experiment for Terkeka Article 02 — *Why Answer Accuracy Is Not
Retrieval Accuracy*.

**Terkeka owns the explanation. This repository owns the experiment.**

## What this experiment demonstrates

A correct final answer does not prove that a RAG pipeline retrieved the
correct evidence. This experiment isolates three independently evaluable
concerns for the same question:

- **Retrieval** — was the labeled-relevant evidence chunk actually retrieved?
- **Grounding** — does the retrieved evidence text actually contain the fact
  needed to answer correctly?
- **Answer** — does the generated answer match the expected answer?

and combines them with a retrieval-aware contract that does **not** let a
correct answer compensate for failed retrieval or failed grounding. See
[`docs/retrieval-aware-evaluation-contract.md`](../../docs/retrieval-aware-evaluation-contract.md).

## Files

- [`documents.json`](documents.json) — a tiny synthetic corpus (4 chunks)
  about fictional plans/products, loaded with the same
  `terkeka_rag_eval.evaluator.load_chunks` used by Article 01.
- [`cases.json`](cases.json) — the four controlled cases plus the
  evidence-ablation fixtures.
- [`expected_results.json`](expected_results.json) — the expected
  retrieval/grounding/answer/overall outcome and failure mode for every
  case, asserted against in `tests/test_article_02_experiment.py`.

## Dataset notice

All documents, questions, expected answers, and `generated_answer` fixtures
in this experiment are synthetic (fictional "Plan Alpha", "Plan Beta",
"Product Orion", "Service Nova"). They are not derived from any production
system, proprietary dataset, confidential information, or internal business
process. `generated_answer` values are explicitly labeled deterministic
fixtures, not live output from an LLM.

## The four controlled cases

| Case | Retrieved evidence | Generated answer | Retrieval | Grounding | Answer | Overall | Failure mode |
|------|--------------------|-------------------|-----------|-----------|--------|---------|---------------|
| A — `article02-case-a` | Plan Alpha (correct) | "30 days" (correct) | PASS | PASS | PASS | PASS | `HEALTHY_RAG` |
| B — `article02-case-b` | Plan Alpha (correct) | "14 days" (wrong) | PASS | PASS | FAIL | FAIL | `GENERATION_FAILURE` |
| C — `article02-case-c` | Product Orion (wrong, unrelated) | "90 days" (wrong) | FAIL | FAIL | FAIL | FAIL | `RETRIEVAL_FAILURE` |
| D — `article02-case-d` | Plan Beta (wrong plan) | "30 days" (correct) | FAIL | FAIL | PASS | FAIL | `CORRECT_ANSWER_WRONG_EVIDENCE` |

**Case D is the primary Article 02 experiment.** An answer-only evaluator
would score it a success — the generated answer matches the expected
answer exactly. The retrieval-aware contract rejects it, because the
evidence actually retrieved was Plan Beta's cancellation policy, not Plan
Alpha's.

## Evidence-ablation experiment

The same question and the same deterministic `generated_answer` fixture
(`"30 days"`) run under three evidence conditions. See
[`examples/evidence_ablation.py`](../../examples/evidence_ablation.py) and
[`results/article-02-results.md`](../../results/article-02-results.md) for
the actual measured output.

## Reproduce

```bash
terkeka-rag-eval article02
terkeka-rag-eval article02 --json results/article-02-results.json --markdown results/article-02-results.md
python examples/answer_vs_retrieval.py
python examples/evidence_ablation.py
pytest tests/test_article_02_experiment.py tests/test_rag_contract.py -v
```
