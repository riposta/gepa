import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

import gepa.api


def test_estimate_endpoint_returns_required_fields():
    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(return_value={
        "szacunek_godzin": 120,
        "uzasadnienie": "Test uzasadnienia.",
        "pewnosc": 0.75,
        "session_id": "test-001",
        "klient": "Klient TEST",
        "opis_projektu": "Portal webowy",
        "typ_projektu": "nowy",
        "historia_klienta": "",
        "wzorce_ryzyk": "",
        "korekta_pm": None,
        "komentarz_pm": None,
        "zatwierdzone": False,
    })

    with patch.object(gepa.api, "_graph", mock_compiled):
        client = TestClient(gepa.api.app)
        response = client.post("/estimate", json={
            "klient": "Klient TEST",
            "opis_projektu": "Portal webowy",
        })
        assert response.status_code == 200
        data = response.json()
        assert "szacunek_godzin" in data
        assert "session_id" in data
        assert "uzasadnienie" in data
        assert "pewnosc" in data
        assert "typ_projektu" in data


def test_approve_endpoint_returns_status():
    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(return_value={"zatwierdzone": True})
    mock_compiled.aupdate_state = AsyncMock()

    with patch.object(gepa.api, "_graph", mock_compiled):
        client = TestClient(gepa.api.app)
        response = client.post("/approve", json={
            "session_id": "test-001",
            "zatwierdzone": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
