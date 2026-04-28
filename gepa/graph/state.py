from typing import TypedDict


class EstimationState(TypedDict):
    session_id: str
    client: str
    project_description: str
    project_type: str
    client_history: str
    risk_patterns: str
    estimated_hours: int | None
    reasoning: str | None
    confidence: float | None
    pm_correction: int | None
    pm_comment: str | None
    approved: bool
