from unittest.mock import MagicMock


def test_estimation_metric_accurate():
    gold = MagicMock()
    gold.actual_hours = 100

    pred = MagicMock()
    pred.estimated_hours = 105
    pred.reasoning = "Project requires 5 sprints: backend 60h, frontend 30h, tests 15h."
    pred.confidence = 0.7

    from gepa.dspy_modules.metrics import estimation_metric
    score = estimation_metric(gold, pred)
    assert 0.8 < score <= 1.0


def test_estimation_metric_bad_estimate():
    gold = MagicMock()
    gold.actual_hours = 100

    pred = MagicMock()
    pred.estimated_hours = 200  # 100% error
    pred.reasoning = "Ok."       # too short
    pred.confidence = 0.99       # overconfident

    from gepa.dspy_modules.metrics import estimation_metric
    score = estimation_metric(gold, pred)
    assert score < 0.5


def test_estimation_metric_returns_float():
    gold = MagicMock()
    gold.actual_hours = 200

    pred = MagicMock()
    pred.estimated_hours = 180
    pred.reasoning = "Standard web project."
    pred.confidence = 0.6

    from gepa.dspy_modules.metrics import estimation_metric
    score = estimation_metric(gold, pred)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_feedback_text():
    gold = MagicMock()
    gold.actual_hours = 100

    pred = MagicMock()
    pred.estimated_hours = 150
    pred.reasoning = "Web project."
    pred.confidence = 0.5

    from gepa.dspy_modules.metrics import estimation_metric_with_feedback
    score, feedback = estimation_metric_with_feedback(gold, pred)
    assert isinstance(score, float)
    assert isinstance(feedback, str)
    assert len(feedback) > 0
