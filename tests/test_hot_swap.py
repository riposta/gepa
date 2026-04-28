from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path


def test_get_latest_program_none_when_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        assert runner.get_latest_program() is None


def test_api_model_info_endpoint_exists():
    with patch("gepa.graph.workflow.create_graph") as mock_graph, \
         patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("dspy.configure"):
        mock_graph.return_value = MagicMock()
        import gepa.api as api_module
        api_module._graph = MagicMock()

        from gepa.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "program_version" in data
        assert "program_path" in data


def test_api_model_reload_endpoint_exists():
    with patch("gepa.graph.workflow.create_graph") as mock_graph, \
         patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("dspy.configure"):
        mock_graph.return_value = MagicMock()
        import gepa.api as api_module
        api_module._graph = MagicMock()
        api_module._graphiti_client = MagicMock()

        from gepa.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.post("/model/reload")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


def test_create_graph_accepts_estimator_param():
    with patch("gepa.graph.workflow.GraphitiClient"), \
         patch("gepa.graph.workflow.create_estimator") as mock_est:
        mock_est.return_value = MagicMock()
        from gepa.graph.workflow import create_graph
        custom_estimator = MagicMock()
        graph = create_graph(estimator=custom_estimator)
        assert graph is not None
        # Domyślny create_estimator nie był wywołany
        mock_est.assert_not_called()
