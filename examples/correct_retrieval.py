from pathlib import Path

from terkeka_rag_eval.evaluator import load_chunks
from terkeka_rag_eval.retrieval import answer_from_top_chunk, retrieve

ROOT = Path(__file__).resolve().parents[1]
chunks = load_chunks(ROOT / "data/documents/corpus.json")
question = "What is the cancellation notice period?"
results = retrieve(question, chunks, k=3)

print("QUESTION:", question)
print("\nRETRIEVED:")
for r in results:
    print(f"- {r.chunk_id} score={r.score:.2f}: {r.text}")
print("\nSIMULATED ANSWER:")
print(answer_from_top_chunk(question, results))
