import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_workflow_has_required_nodes():
    with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
         patch("gepa.graph.workflow.create_estimator") as mock_est, \
         patch("gepa.graph.workflow.create_classifier") as mock_clf:
        mock_gc.return_value = AsyncMock()
        mock_est.return_value = MagicMock()
        mock_clf.return_value = MagicMock()

        from gepa.graph.workflow import create_graph
        graph = create_graph()
        assert "intake" in graph.nodes
        assert "classify" in graph.nodes
        assert "context" in graph.nodes
        assert "estimation" in graph.nodes
        assert "store" in graph.nodes


def test_estimation_state_fields():
    from gepa.graph.state import EstimationState
    state: EstimationState = {
        "session_id": "test-001",
        "client": "Client ABC",
        "project_description": "New portal",
        "project_type": "new",
        "client_history": "",
        "risk_patterns": "",
        "estimated_hours": None,
        "reasoning": None,
        "confidence": None,
        "pm_correction": None,
        "pm_comment": None,
        "approved": False,
    }
    assert state["approved"] is False
    assert state["project_type"] == "new"
