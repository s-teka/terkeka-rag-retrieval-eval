from __future__ import annotations

import re

from .models import AnswerEvaluation

_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Conservative normalization: trim, lowercase, collapse whitespace.

    Deliberately does not do fuzzy/semantic matching. Article 02's controlled
    experiment needs deterministic, inspectable pass/fail behavior; a fuzzy
    grader would obscure exactly which case produced which result.
    """
    return _WHITESPACE.sub(" ", text.strip().lower())


def evaluate_answer(expected_answer: str, generated_answer: str) -> AnswerEvaluation:
    """Deterministic answer-correctness check against a fixed expected answer.

    Real-world natural-language answer grading often needs a human or an
    LLM-as-judge. This repository intentionally avoids that here so the
    controlled experiment stays reproducible without external services.
    """
    passed = normalize_text(expected_answer) == normalize_text(generated_answer)
    return AnswerEvaluation(
        passed=passed,
        expected_answer=expected_answer,
        generated_answer=generated_answer,
    )
