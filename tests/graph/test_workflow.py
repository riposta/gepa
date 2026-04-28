import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_workflow_has_required_nodes():
    with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
         patch("gepa.graph.workflow.create_estimator") as mock_est:
        mock_gc.return_value = AsyncMock()
        mock_est.return_value = MagicMock()

        from gepa.graph.workflow import create_graph
        graph = create_graph()
        assert "intake" in graph.nodes
        assert "context" in graph.nodes
        assert "estimation" in graph.nodes
        assert "store" in graph.nodes


def test_estimation_state_fields():
    from gepa.graph.state import EstimationState
    state: EstimationState = {
        "session_id": "test-001",
        "klient": "Klient ABC",
        "opis_projektu": "Nowy portal",
        "typ_projektu": "nowy",
        "historia_klienta": "",
        "wzorce_ryzyk": "",
        "szacunek_godzin": None,
        "uzasadnienie": None,
        "pewnosc": None,
        "korekta_pm": None,
        "komentarz_pm": None,
        "zatwierdzone": False,
    }
    assert state["zatwierdzone"] is False
    assert state["typ_projektu"] == "nowy"
