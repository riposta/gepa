import pytest
from unittest.mock import patch, MagicMock


def test_estimator_returns_required_fields():
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(
            estimated_hours=120,
            reasoning="Project requires 3 sprints.",
            confidence=0.75,
        )
        mock_cot.return_value = mock_instance

        from gepa.dspy_modules.estimator import create_estimator
        estimator = create_estimator()
        result = estimator(
            project_description="REST API in Django",
            client_history="No history.",
            risk_patterns="No patterns.",
        )

        assert hasattr(result, "estimated_hours")
        assert hasattr(result, "reasoning")
        assert hasattr(result, "confidence")


def test_estimation_signature_has_correct_fields():
    from gepa.dspy_modules.signatures import ITEstimation
    import dspy
    # Check that signature has required input and output fields
    annotations = ITEstimation.__annotations__ if hasattr(ITEstimation, '__annotations__') else {}
    assert "project_description" in annotations or "project_description" in str(ITEstimation)
    assert "estimated_hours" in annotations or "estimated_hours" in str(ITEstimation)
