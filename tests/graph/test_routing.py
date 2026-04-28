import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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


def test_create_graph_accepts_estimators_dict():
    with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
         patch("gepa.graph.workflow.create_classifier") as mock_clf:
        mock_gc.return_value = AsyncMock()
        mock_clf.return_value = MagicMock()

        estimators = {
            "legacy": MagicMock(),
            "nowy": MagicMock(),
            "ai": MagicMock(),
            "migracja": MagicMock(),
        }
        from gepa.graph.workflow import create_graph
        graph = create_graph(estimators=estimators)
        assert graph is not None
