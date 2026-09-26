"""Article 02: evidence-ablation experiment.

Runs the same question with the same deterministic `generated_answer`
fixture ("30 days") under three evidence conditions -- correct evidence,
wrong evidence, and no evidence -- and prints the resulting diagnosis for
each. It demonstrates how to check whether retrieval actually contributed
to a correct answer; it is not a claim about how any real LLM behaves.
"""

from pathlib import Path

from terkeka_rag_eval.article02 import (
    load_evidence_ablation_cases,
    load_experiment_corpus,
    run_cases,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "experiments" / "answer_vs_retrieval"

corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
cases = load_evidence_ablation_cases(EXPERIMENT_DIR / "cases.json")
results = run_cases(cases, corpus)

print(f"{'Evidence':<18}{'Retrieval':<12}{'Grounding':<12}{'Answer':<10}Failure Mode")
for case, result in zip(cases, results):
    condition = case.case_id.removeprefix("article02-ablation-")
    pf = lambda v: "PASS" if v else "FAIL"  # noqa: E731
    print(
        f"{condition:<18}"
        f"{pf(result.retrieval.passed):<12}"
        f"{pf(result.grounding.passed):<12}"
        f"{pf(result.answer.passed):<10}"
        f"{result.failure_mode}"
    )

print(
    "\nAll three rows share the same generated_answer fixture (\"30 days\"), "
    "so answer.pass is True in every row. Only retrieval/grounding "
    "distinguish correct evidence from wrong or missing evidence.\n"
    "This does NOT prove retrieval is globally unnecessary -- it shows only "
    "that answer correctness for this test case does not prove retrieval "
    "was effective."
)
