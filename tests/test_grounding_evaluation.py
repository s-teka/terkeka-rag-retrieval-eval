from terkeka_rag_eval.grounding_evaluation import evaluate_grounding
from terkeka_rag_eval.models import DocumentChunk

PLAN_ALPHA = DocumentChunk(
    chunk_id="plan-alpha-cancel-01",
    title="Plan Alpha — Cancellation",
    text="Plan Alpha requires 30 days notice before cancellation takes effect.",
    metadata={},
)
PLAN_BETA = DocumentChunk(
    chunk_id="plan-beta-cancel-01",
    title="Plan Beta — Cancellation",
    text="Plan Beta requires 14 days notice before cancellation takes effect.",
    metadata={},
)


def test_grounding_pass_when_evidence_contains_expected_fact():
    result = evaluate_grounding("30 days", [PLAN_ALPHA])
    assert result.passed is True
    assert result.answer_supported_by_context is True


def test_grounding_fail_when_evidence_is_the_wrong_chunk():
    """Article 02 section 8 example: wrong evidence does not support the
    expected fact, even though a generated answer might independently
    happen to match it."""
    result = evaluate_grounding("30 days", [PLAN_BETA])
    assert result.passed is False


def test_grounding_fail_when_no_evidence_supplied():
    result = evaluate_grounding("30 days", [])
    assert result.passed is False


def test_grounding_checks_expected_answer_not_generated_answer():
    """Grounding answers 'was the correct fact present in context', not
    'does the generated answer text appear anywhere' -- it is evaluated
    against expected_answer regardless of what was generated."""
    result = evaluate_grounding("30 days", [PLAN_ALPHA])
    assert result.passed is True
