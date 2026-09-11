from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluator import evaluate, load_chunks, load_eval_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a small labeled RAG retrieval dataset.")
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("evaluate", help="Run retrieval evaluation")
    ev.add_argument("--corpus", default="data/documents/corpus.json")
    ev.add_argument("--eval", dest="eval_path", default="data/eval_dataset.json")
    ev.add_argument("-k", type=int, default=3)
    ev.add_argument("--json", dest="json_out", default=None)
    args = parser.parse_args()

    if args.command == "evaluate":
        report = evaluate(load_chunks(args.corpus), load_eval_cases(args.eval_path), k=args.k)
        text = json.dumps(report, indent=2)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
