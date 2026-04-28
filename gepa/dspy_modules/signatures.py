import dspy


class ITEstimation(dspy.Signature):
    """Estimate IT project effort in man-hours based on description and history."""

    project_description: str = dspy.InputField(desc="Full description of the IT project requirements")
    client_history: str = dspy.InputField(desc="Client's project history from Graphiti (or 'No history.')")
    risk_patterns: str = dspy.InputField(desc="Learned risk patterns from Graphiti (or 'No patterns.')")

    estimated_hours: int = dspy.OutputField(desc="Estimated man-hours (integer)")
    reasoning: str = dspy.OutputField(desc="Detailed explanation of estimation methodology broken down by components")
    confidence: float = dspy.OutputField(desc="Estimation confidence from 0.0 (none) to 1.0 (full)")
