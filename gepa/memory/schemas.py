from pydantic import BaseModel


class ITProject(BaseModel):
    name: str
    technologies: list[str]
    type: str  # "new" | "legacy" | "migration" | "ai"
    estimated_budget_hours: float | None = None
    actual_budget_hours: float | None = None
    deviation_percent: float | None = None


class Client(BaseModel):
    name: str
    industry: str
    estimation_preferences: str = "detailed"


class RiskPattern(BaseModel):
    description: str
    typical_overhead_percent: float
    when_occurs: str
