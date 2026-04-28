# tests/test_api_auth.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import SecretStr
import gepa.api


def test_estimate_no_auth_when_api_key_empty():
    """If api_key in settings is empty — no key required."""
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "estimated_hours": 100, "reasoning": "ok", "confidence": 0.7,
        "project_type": "new", "session_id": "s1",
        "client": "K", "project_description": "o", "client_history": "",
        "risk_patterns": "", "pm_correction": None, "pm_comment": None,
        "approved": False,
    })
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = SecretStr("")
        client = TestClient(gepa.api.app)
        resp = client.post("/estimate", json={"client": "K", "project_description": "o"})
        assert resp.status_code == 200


def test_estimate_returns_401_with_wrong_key():
    """If api_key is set — wrong key returns 401."""
    mock_graph = MagicMock()
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = SecretStr("secret123")
        client = TestClient(gepa.api.app)
        resp = client.post(
            "/estimate",
            json={"client": "K", "project_description": "o"},
            headers={"X-API-Key": "wrongkey"},
        )
        assert resp.status_code == 401


def test_estimate_passes_with_correct_key():
    """Correct key — 200."""
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "estimated_hours": 100, "reasoning": "ok", "confidence": 0.7,
        "project_type": "new", "session_id": "s1",
        "client": "K", "project_description": "o", "client_history": "",
        "risk_patterns": "", "pm_correction": None, "pm_comment": None,
        "approved": False,
    })
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = SecretStr("secret123")
        client = TestClient(gepa.api.app)
        resp = client.post(
            "/estimate",
            json={"client": "K", "project_description": "o"},
            headers={"X-API-Key": "secret123"},
        )
        assert resp.status_code == 200
