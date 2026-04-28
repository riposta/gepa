from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import json


def test_faza2_imports():
    from gepa.dspy_modules.metrics import metryka_wyceny, metryka_wyceny_z_feedbackiem
    from gepa.optimization.optimizer import OptimizerRunner
    from gepa.monitoring.mlflow_tracker import OptimizationTracker
    from gepa.monitoring.langfuse_config import configure_langfuse
    assert True


def test_metryka_i_feedback_integracja():
    from gepa.dspy_modules.metrics import metryka_wyceny, metryka_wyceny_z_feedbackiem
    from unittest.mock import MagicMock

    gold = MagicMock()
    gold.rzeczywiste_godziny = 100
    pred = MagicMock()
    pred.szacunek_godzin = 90
    pred.uzasadnienie = "Backend 50h, frontend 30h, testy 20h."
    pred.pewnosc = 0.7

    score = metryka_wyceny(gold, pred)
    score2, feedback = metryka_wyceny_z_feedbackiem(gold, pred)

    assert 0.0 <= score <= 1.0
    assert score == score2
    assert isinstance(feedback, str)


def test_optimizer_runner_no_trigger_without_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        assert not runner.should_trigger(tmpdir)
        assert runner.get_latest_program() is None


def test_api_model_endpoints_exist():
    with patch("gepa.graph.workflow.create_graph") as mock_graph, \
         patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("dspy.configure"):
        mock_graph.return_value = MagicMock()
        from gepa.api import app
        import gepa.api as api_module
        api_module._graph = MagicMock()

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/model/info")
        assert resp.status_code == 200
