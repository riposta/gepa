import json
from pathlib import Path
import dspy


def load_trainset(training_dir: str) -> list[dspy.Example]:
    examples = []
    for f in Path(training_dir).glob("*.json"):
        data = json.loads(f.read_text())
        if "project_description" not in data or "actual_hours" not in data:
            continue
        ex = dspy.Example(
            project_description=data["project_description"],
            client_history=data.get("client_history", "No history."),
            risk_patterns=data.get("risk_patterns", "No patterns."),
            actual_hours=data["actual_hours"],
        ).with_inputs("project_description", "client_history", "risk_patterns")
        examples.append(ex)
    return examples


def count_examples(training_dir: str) -> int:
    return len(load_trainset(training_dir))
