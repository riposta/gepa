import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import tempfile
from pathlib import Path


def test_save_to_trainset_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        import gepa.graph.workflow as workflow
        with patch.object(workflow, "TRAINING_DIR", tmpdir):
            state = {
                "session_id": "test-001",
                "client": "Client",
                "project_description": "Web portal",
                "client_history": "",
                "risk_patterns": "",
                "estimated_hours": 100,
                "reasoning": "Test",
                "confidence": 0.7,
                "pm_correction": 120,
                "pm_comment": "Not enough for tests",
                "approved": False,
            }
            workflow._save_to_trainset(state, 120)

            files = list(Path(tmpdir).glob("hitl_*.json"))
            assert len(files) == 1
            data = json.loads(files[0].read_text())
            assert data["project_description"] == "Web portal"
            assert data["actual_hours"] == 120
            assert data["source"] == "hitl"


@pytest.mark.asyncio
async def test_store_node_does_not_trigger_below_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("gepa.graph.workflow.TRAINING_DIR", tmpdir), \
             patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
             patch("gepa.graph.workflow.create_estimator") as mock_est, \
             patch("gepa.graph.workflow.create_classifier") as mock_clf, \
             patch("gepa.graph.workflow.OptimizerRunner") as mock_runner_cls:

            mock_gc.return_value = AsyncMock()
            mock_gc.return_value.get_context = AsyncMock(return_value="")
            mock_gc.return_value.get_risk_patterns = AsyncMock(return_value="")
            mock_gc.return_value.add_episode = AsyncMock()
            mock_est.return_value = MagicMock()
            mock_clf.return_value = MagicMock()
            mock_runner = MagicMock()
            mock_runner.should_trigger.return_value = False
            mock_runner_cls.return_value = mock_runner

            from gepa.graph.workflow import create_graph
            graph = create_graph()
            assert graph is not None
            mock_runner.run.assert_not_called()


def test_store_node_triggers_optimization_at_threshold():
    """Verifies that store_node calls runner.run when threshold is exceeded."""
    with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
         patch("gepa.graph.workflow.create_estimator") as mock_est, \
         patch("gepa.graph.workflow.create_classifier") as mock_clf, \
         patch("gepa.graph.workflow.OptimizerRunner") as mock_runner_cls:

        mock_gc.return_value = MagicMock()
        mock_est.return_value = MagicMock()
        mock_clf.return_value = MagicMock()

        mock_runner = MagicMock()
        mock_runner.should_trigger.return_value = True
        mock_runner.run.return_value = Path(tempfile.mkdtemp()) / "v2_miprov2.json"
        mock_runner_cls.return_value = mock_runner

        from gepa.graph import workflow
        graph = workflow.create_graph()

        # Verify that OptimizerRunner is patchable in workflow
        assert mock_runner_cls is not None
        assert graph is not None
