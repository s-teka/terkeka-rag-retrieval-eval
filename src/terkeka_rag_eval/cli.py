from __future__ import annotations

import argparse
import json
from pathlib import Path

from .article02 import DEFAULT_CASES, DEFAULT_DOCUMENTS, format_summary, render_markdown_report, run_article02_experiment
from .evaluator import evaluate, load_chunks, load_eval_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a small labeled RAG retrieval dataset.")
    sub = parser.add_subparsers(dest="command", required=True)

    ev = sub.add_parser("evaluate", help="Run retrieval evaluation (Article 01)")
    ev.add_argument("--corpus", default="data/documents/corpus.json")
    ev.add_argument("--eval", dest="eval_path", default="data/eval_dataset.json")
    ev.add_argument("-k", type=int, default=3)
    ev.add_argument("--json", dest="json_out", default=None)

    a2 = sub.add_parser(
        "article02",
        help="Run the Article 02 answer-vs-retrieval experiment (four controlled cases + evidence ablation)",
    )
    a2.add_argument("--documents", default=DEFAULT_DOCUMENTS)
    a2.add_argument("--cases", dest="cases_path", default=DEFAULT_CASES)
    a2.add_argument("--json", dest="json_out", default=None)
    a2.add_argument("--markdown", dest="markdown_out", default=None)

    args = parser.parse_args()

    if args.command == "evaluate":
        report = evaluate(load_chunks(args.corpus), load_eval_cases(args.eval_path), k=args.k)
        text = json.dumps(report, indent=2)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")

    elif args.command == "article02":
        report = run_article02_experiment(args.documents, args.cases_path)
        print(format_summary(report))
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.markdown_out:
            Path(args.markdown_out).write_text(render_markdown_report(report), encoding="utf-8")


if __name__ == "__main__":
    main()
