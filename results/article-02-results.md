# Article 02 Experimental Results

**Terkeka owns the explanation. This repository owns the experiment.**

## Experiment purpose

Demonstrate, with deterministic and reproducible fixtures, that a correct final answer does not prove that retrieval worked correctly. Four controlled cases isolate retrieval, grounding, and answer correctness as independent evaluation dimensions; an evidence-ablation experiment then varies only the retrieved evidence for the same question.

All fixtures are synthetic (`experiments/answer_vs_retrieval/`) and no external LLM, API key, or network access is used -- `generated_answer` values are explicitly labeled deterministic/simulated fixtures, not live model output.

## Four controlled cases

| Case | Retrieval | Grounding | Answer | Overall | Failure Mode |
|------|-----------|-----------|--------|---------|--------------|
| article02-case-a | PASS | PASS | PASS | PASS | HEALTHY_RAG |
| article02-case-b | PASS | PASS | FAIL | FAIL | GENERATION_FAILURE |
| article02-case-c | FAIL | FAIL | FAIL | FAIL | RETRIEVAL_FAILURE |
| article02-case-d | FAIL | FAIL | PASS | FAIL | CORRECT_ANSWER_WRONG_EVIDENCE |

Case D (`article02-case-d`) is the primary Article 02 experiment. An answer-only evaluator would score it a success because the generated answer matches the expected answer. The retrieval-aware contract correctly rejects it: the retrieved evidence was the wrong plan's cancellation policy, so `overall.pass = false` with `failure_mode = CORRECT_ANSWER_WRONG_EVIDENCE`.

## Evidence-ablation experiment

Same question and same deterministic `generated_answer` fixture (`"30 days"`) under three evidence conditions:

| Evidence | Retrieval | Grounding | Answer | Failure Mode |
|----------|-----------|-----------|--------|--------------|
| correct_evidence | PASS | PASS | PASS | HEALTHY_RAG |
| wrong_evidence | FAIL | FAIL | PASS | CORRECT_ANSWER_WRONG_EVIDENCE |
| no_evidence | FAIL | FAIL | PASS | INSUFFICIENT_EVIDENCE |

## Key observation

The `generated_answer` fixture is identical (`"30 days"`) across all three evidence conditions, yet `answer.pass` is `true` in every row. Answer correctness alone does not distinguish correct evidence from wrong evidence from no evidence at all -- only the retrieval and grounding checks do.

## Interpretation

Comparing the `correct_evidence` row to the `no_evidence` row shows the same question producing the same correct answer with and without retrieved evidence. This does **not** prove retrieval is globally unnecessary -- it demonstrates only that, for this test case, answer correctness does not by itself prove retrieval was effective or even used.

## Limitations

- This experiment uses deterministic synthetic fixtures, not live model output.
- It does not measure real LLM accuracy or claim to benchmark any model.
- It does not claim every correct answer after bad retrieval came from pretrained/prior knowledge -- that is simulated here, not measured.
- Real RAG systems may contain redundant evidence across multiple chunks.
- Multiple chunks can legitimately support the same answer.
- Real grounding evaluation can require human or model-based judgment; this repository uses exact-text containment instead, which is conservative and can itself miss valid paraphrased support (see the UNSUPPORTED_CORRECT_ANSWER case in tests/test_rag_contract.py).
- LLM-as-judge approaches introduce their own evaluation uncertainty and are intentionally not used here.
- The repository isolates these concepts for educational reproducibility, not as a production RAG evaluation system.

## Reproduction command

```bash
terkeka-rag-eval article02 --json results/article-02-results.json --markdown results/article-02-results.md
```
