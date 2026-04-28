import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

import gepa.api


def test_estimate_endpoint_returns_required_fields():
    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(return_value={
        "estimated_hours": 120,
        "reasoning": "Test reasoning.",
        "confidence": 0.75,
        "session_id": "test-001",
        "client": "Test Client",
        "project_description": "Web portal",
        "project_type": "new",
        "client_history": "",
        "risk_patterns": "",
        "pm_correction": None,
        "pm_comment": None,
        "approved": False,
    })

    with patch.object(gepa.api, "_graph", mock_compiled):
        client = TestClient(gepa.api.app)
        response = client.post("/estimate", json={
            "client": "Test Client",
            "project_description": "Web portal",
        })
        assert response.status_code == 200
        data = response.json()
        assert "estimated_hours" in data
        assert "session_id" in data
        assert "reasoning" in data
        assert "confidence" in data
        assert "project_type" in data


def test_approve_endpoint_returns_status():
    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(return_value={"approved": True})
    mock_compiled.aupdate_state = AsyncMock()

    with patch.object(gepa.api, "_graph", mock_compiled):
        client = TestClient(gepa.api.app)
        response = client.post("/approve", json={
            "session_id": "test-001",
            "approved": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
