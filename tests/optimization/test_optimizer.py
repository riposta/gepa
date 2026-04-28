import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import json


def test_optimizer_runner_creates_instance():
    from gepa.optimization.optimizer import OptimizerRunner
    runner = OptimizerRunner(programs_dir="/tmp/test_programs")
    assert runner is not None
    assert runner.programs_dir == Path("/tmp/test_programs")


def test_get_latest_program_returns_none_when_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        result = runner.get_latest_program()
        assert result is None


def test_get_latest_program_returns_highest_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "v1_baseline.json").write_text("{}")
        (p / "v2_optimized.json").write_text("{}")
        (p / "v3_optimized.json").write_text("{}")

        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        result = runner.get_latest_program()
        assert result is not None
        assert "v3" in str(result)


def test_next_version_baseline():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        assert runner.next_version() == "v2"


def test_next_version_increments():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "v3_miprov2.json").write_text("{}")

        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        assert runner.next_version() == "v4"


def test_should_trigger_false_below_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        assert runner.should_trigger(training_dir=tmpdir) is False


def test_should_trigger_true_above_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(60):
            ex = {"project_description": f"Project {i}", "actual_hours": 100 + i}
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps(ex))

        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        assert runner.should_trigger(training_dir=tmpdir) is True
