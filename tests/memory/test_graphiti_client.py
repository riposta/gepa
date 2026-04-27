import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_get_context_returns_string_on_empty():
    with patch("gepa.memory.graphiti_client.Graphiti") as mock_graphiti_cls:
        mock_instance = AsyncMock()
        mock_instance.search.return_value = []
        mock_graphiti_cls.return_value = mock_instance

        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient.__new__(GraphitiClient)
        client.graphiti = mock_instance

        result = await client.get_context("nieznany klient", "nowy projekt")
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_get_risk_patterns_returns_string_on_empty():
    with patch("gepa.memory.graphiti_client.Graphiti") as mock_graphiti_cls:
        mock_instance = AsyncMock()
        mock_instance.search.return_value = []
        mock_graphiti_cls.return_value = mock_instance

        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient.__new__(GraphitiClient)
        client.graphiti = mock_instance

        result = await client.get_risk_patterns("projekt legacy Java")
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_add_episode_calls_graphiti():
    with patch("gepa.memory.graphiti_client.Graphiti") as mock_graphiti_cls:
        mock_instance = AsyncMock()
        mock_graphiti_cls.return_value = mock_instance

        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient.__new__(GraphitiClient)
        client.graphiti = mock_instance

        await client.add_episode(
            session_id="test_session",
            content="Projekt X: 120 godzin, szacunek 110 godzin.",
        )
        mock_instance.add_episode.assert_called_once()
