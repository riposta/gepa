import json
import tempfile
from pathlib import Path


def test_load_trainset_returns_dspy_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        example = {
            "project_description": "Web portal",
            "actual_hours": 200,
            "project_type": "new",
        }
        (Path(tmpdir) / "ex1.json").write_text(json.dumps(example))

        from gepa.optimization.trainset import load_trainset
        examples = load_trainset(tmpdir)

        assert len(examples) == 1
        assert examples[0].actual_hours == 200
        assert examples[0].project_description == "Web portal"


def test_load_trainset_skips_invalid():
    with tempfile.TemporaryDirectory() as tmpdir:
        # File without required fields
        (Path(tmpdir) / "invalid.json").write_text(json.dumps({"foo": "bar"}))
        # Valid file
        (Path(tmpdir) / "valid.json").write_text(json.dumps({
            "project_description": "System X", "actual_hours": 100
        }))

        from gepa.optimization.trainset import load_trainset
        examples = load_trainset(tmpdir)
        assert len(examples) == 1


def test_count_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 4 valid examples
        for i in range(4):
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps({
                "project_description": f"Project {i}",
                "actual_hours": 100 + i,
            }))
        # 1 invalid example (missing required fields) — should not be counted
        (Path(tmpdir) / "invalid.json").write_text(json.dumps({"x": 99}))

        from gepa.optimization.trainset import count_examples
        assert count_examples(tmpdir) == 4
