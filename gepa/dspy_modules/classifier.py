import dspy

PROJECT_TYPES = ["legacy", "new", "ai", "migration"]


class ProjectTypeClassification(dspy.Signature):
    """Classify the IT project type based on its description."""

    project_description: str = dspy.InputField(desc="IT project description")
    project_type: str = dspy.OutputField(
        desc=(
            "Project type — ONE word: "
            "legacy (modernization/maintenance of existing system), "
            "new (brand new system from scratch), "
            "ai (ML/AI/LLM project), "
            "migration (cloud or platform migration)"
        )
    )


def create_classifier() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(ProjectTypeClassification)


def normalize_type(raw: str) -> str:
    cleaned = raw.lower().strip()
    for typ in PROJECT_TYPES:
        if typ in cleaned:
            return typ
    return "new"
