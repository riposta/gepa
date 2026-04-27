import json
from pathlib import Path
import dspy


def load_trainset(training_dir: str) -> list[dspy.Example]:
    examples = []
    for f in Path(training_dir).glob("*.json"):
        data = json.loads(f.read_text())
        if "opis_projektu" not in data or "rzeczywiste_godziny" not in data:
            continue
        ex = dspy.Example(
            opis_projektu=data["opis_projektu"],
            historia_klienta=data.get("historia_klienta", "Brak historii."),
            wzorce_ryzyk=data.get("wzorce_ryzyk", "Brak wzorców."),
            rzeczywiste_godziny=data["rzeczywiste_godziny"],
        ).with_inputs("opis_projektu", "historia_klienta", "wzorce_ryzyk")
        examples.append(ex)
    return examples


def count_examples(training_dir: str) -> int:
    return len(load_trainset(training_dir))
