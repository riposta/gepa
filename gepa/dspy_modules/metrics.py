def estimation_metric(gold, pred, trace=None) -> float:
    actual = getattr(gold, "actual_hours", 0) or 0
    estimate = getattr(pred, "estimated_hours", 0) or 0
    reasoning = getattr(pred, "reasoning", "") or ""
    confidence = getattr(pred, "confidence", 0.5) or 0.5

    # Accuracy (50%)
    if actual == 0:
        accuracy = 0.0
    else:
        error = abs(estimate - actual) / actual
        accuracy = max(0.0, 1.0 - error)

    # Reasoning (30%) — length as quality proxy
    reasoning_score = min(1.0, len(reasoning) / 150)

    # Confidence calibration (20%)
    if confidence < 0.2 or confidence > 0.95:
        calibration = 0.3
    elif 0.3 <= confidence <= 0.85:
        calibration = 1.0
    else:
        calibration = 0.7

    return round(
        0.5 * accuracy + 0.3 * reasoning_score + 0.2 * calibration,
        4,
    )


def estimation_metric_with_feedback(gold, pred, trace=None) -> tuple[float, str]:
    score = estimation_metric(gold, pred, trace)

    actual = getattr(gold, "actual_hours", 0) or 0
    estimate = getattr(pred, "estimated_hours", 0) or 0
    reasoning = getattr(pred, "reasoning", "") or ""
    confidence = getattr(pred, "confidence", 0.5) or 0.5

    feedback_parts = []

    if actual > 0:
        error = (estimate - actual) / actual
        if error > 0.3:
            feedback_parts.append(
                f"Estimate too high by {error:.0%} — check for duplicate tasks."
            )
        elif error < -0.3:
            feedback_parts.append(
                f"Estimate too low by {abs(error):.0%} — include risk buffer and testing time."
            )

    if len(reasoning) < 80:
        feedback_parts.append(
            "Reasoning too short — add breakdown by components (backend/frontend/tests)."
        )

    if confidence > 0.95:
        feedback_parts.append(
            "Confidence too high — for new projects keep confidence below 0.9."
        )
    elif confidence < 0.2:
        feedback_parts.append(
            "Confidence too low — if you have historical data, raise confidence."
        )

    feedback = " ".join(feedback_parts) if feedback_parts else "Estimate within normal range."
    return score, feedback
