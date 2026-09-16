from terkeka_rag_eval.answer_evaluation import evaluate_answer, normalize_text


def test_answer_pass_on_exact_match():
    result = evaluate_answer("30 days", "30 days")
    assert result.passed is True


def test_answer_pass_is_case_and_whitespace_insensitive():
    result = evaluate_answer("30 days", "  30   Days  ")
    assert result.passed is True


def test_answer_fail_on_mismatch():
    result = evaluate_answer("30 days", "14 days")
    assert result.passed is False


def test_answer_evaluation_preserves_original_text():
    result = evaluate_answer("30 days", "14 days")
    assert result.expected_answer == "30 days"
    assert result.generated_answer == "14 days"


def test_normalize_text_collapses_whitespace_and_case():
    assert normalize_text("  Thirty   Days ") == "thirty days"
