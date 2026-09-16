"""Article 02: run the four controlled cases and print the diagnosis for each.

`generated_answer` in experiments/answer_vs_retrieval/cases.json is an
explicitly labeled deterministic/simulated fixture, not a live LLM call --
this script demonstrates evaluation mechanics, not model behavior.
"""

from pathlib import Path

from terkeka_rag_eval.article02 import load_controlled_cases, load_experiment_corpus, run_cases

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = ROOT / "experiments" / "answer_vs_retrieval"

corpus = load_experiment_corpus(EXPERIMENT_DIR / "documents.json")
cases = load_controlled_cases(EXPERIMENT_DIR / "cases.json")

for case, result in zip(cases, run_cases(cases, corpus)):
    print(f"\n=== {result.case_id} ===")
    print(f"question:          {case.question}")
    print(f"retrieved_chunks:  {case.retrieved_chunk_ids}")
    print(f"relevant_chunks:   {case.relevant_chunk_ids}")
    print(f"expected_answer:   {case.expected_answer}")
    print(f"generated_answer:  {case.generated_answer}  (simulated fixture)")
    print(f"retrieval.pass:    {result.retrieval.passed}")
    print(f"grounding.pass:    {result.grounding.passed}")
    print(f"answer.pass:       {result.answer.passed}")
    print(f"overall.pass:      {result.overall_pass}")
    print(f"failure_mode:      {result.failure_mode}")

print(
    "\nNOTE: article02-case-d has a correct answer but overall.pass=False. "
    "An answer-only evaluator would have called it a success."
)
