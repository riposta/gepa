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
                "klient": "Klient",
                "opis_projektu": "Portal webowy",
                "historia_klienta": "",
                "wzorce_ryzyk": "",
                "szacunek_godzin": 100,
                "uzasadnienie": "Test",
                "pewnosc": 0.7,
                "korekta_pm": 120,
                "komentarz_pm": "Za mało na testy",
                "zatwierdzone": False,
            }
            workflow._save_to_trainset(state, 120)

            files = list(Path(tmpdir).glob("hitl_*.json"))
            assert len(files) == 1
            data = json.loads(files[0].read_text())
            assert data["opis_projektu"] == "Portal webowy"
            assert data["rzeczywiste_godziny"] == 120
            assert data["zrodlo"] == "hitl"


@pytest.mark.asyncio
async def test_store_node_does_not_trigger_below_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("gepa.graph.workflow.TRAINING_DIR", tmpdir), \
             patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
             patch("gepa.graph.workflow.create_estimator") as mock_est, \
             patch("gepa.graph.workflow.OptimizerRunner") as mock_runner_cls:

            mock_gc.return_value = AsyncMock()
            mock_gc.return_value.get_context = AsyncMock(return_value="")
            mock_gc.return_value.get_risk_patterns = AsyncMock(return_value="")
            mock_gc.return_value.add_episode = AsyncMock()
            mock_est.return_value = MagicMock()
            mock_runner = MagicMock()
            mock_runner.should_trigger.return_value = False
            mock_runner_cls.return_value = mock_runner

            from gepa.graph.workflow import create_graph
            graph = create_graph()
            assert graph is not None
            mock_runner.run.assert_not_called()
