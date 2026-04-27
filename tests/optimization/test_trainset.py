import json
import tempfile
from pathlib import Path


def test_load_trainset_returns_dspy_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        example = {
            "opis_projektu": "Portal webowy",
            "rzeczywiste_godziny": 200,
            "typ_projektu": "nowy",
        }
        (Path(tmpdir) / "ex1.json").write_text(json.dumps(example))

        from gepa.optimization.trainset import load_trainset
        examples = load_trainset(tmpdir)

        assert len(examples) == 1
        assert examples[0].rzeczywiste_godziny == 200
        assert examples[0].opis_projektu == "Portal webowy"


def test_load_trainset_skips_invalid():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Plik bez wymaganych pól
        (Path(tmpdir) / "invalid.json").write_text(json.dumps({"foo": "bar"}))
        # Poprawny plik
        (Path(tmpdir) / "valid.json").write_text(json.dumps({
            "opis_projektu": "System X", "rzeczywiste_godziny": 100
        }))

        from gepa.optimization.trainset import load_trainset
        examples = load_trainset(tmpdir)
        assert len(examples) == 1


def test_count_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 4 valid examples
        for i in range(4):
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps({
                "opis_projektu": f"Projekt {i}",
                "rzeczywiste_godziny": 100 + i,
            }))
        # 1 invalid example (missing required fields) — should not be counted
        (Path(tmpdir) / "invalid.json").write_text(json.dumps({"x": 99}))

        from gepa.optimization.trainset import count_examples
        assert count_examples(tmpdir) == 4
