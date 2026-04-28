# tests/test_faza3_smoke.py
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import tempfile
import json


def test_faza3_imports():
    from gepa.dspy_modules.classifier import create_classifier, normalize_type, PROJECT_TYPES
    from gepa.api_auth import verify_api_key
    assert len(PROJECT_TYPES) == 4


def test_normalize_type_all_types():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("legacy") == "legacy"
    assert normalize_type("new portal") == "new"
    assert normalize_type("ai project") == "ai"
    assert normalize_type("migration cloud") == "migration"
    assert normalize_type("unknown") == "new"


def test_workflow_has_classify_node():
    with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
         patch("gepa.graph.workflow.create_estimator") as mock_est, \
         patch("gepa.graph.workflow.create_classifier") as mock_clf:
        mock_gc.return_value = AsyncMock()
        mock_est.return_value = MagicMock()
        mock_clf.return_value = MagicMock()

        from gepa.graph.workflow import create_graph
        graph = create_graph()
        assert "classify" in graph.nodes
        assert "estimation" in graph.nodes


def test_estimate_counter_increments():
    with tempfile.TemporaryDirectory() as tmpdir:
        counter_file = Path(tmpdir) / "estimates_count.json"
        import gepa.graph.workflow as wf
        with patch.object(wf, "ESTIMATES_FILE", str(counter_file)):
            c1 = wf._increment_estimate_count()
            c2 = wf._increment_estimate_count()
            assert c2 == c1 + 1
            assert counter_file.exists()


def test_api_responds_with_project_type():
    import gepa.api as api_module
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "estimated_hours": 80, "reasoning": "ok", "confidence": 0.6,
        "project_type": "ai", "session_id": "s2",
        "client": "K", "project_description": "ML system", "client_history": "",
        "risk_patterns": "", "pm_correction": None, "pm_comment": None,
        "approved": False,
    })
    from fastapi.testclient import TestClient
    with patch.object(api_module, "_graph", mock_graph):
        client = TestClient(api_module.app)
        resp = client.post("/estimate", json={"client": "K", "project_description": "ML system"})
        assert resp.status_code == 200
        assert resp.json()["project_type"] == "ai"
