# tests/test_api_auth.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import gepa.api


def test_estimate_no_auth_when_api_key_empty():
    """Jeśli api_key w settings jest puste — brak wymagania klucza."""
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "szacunek_godzin": 100, "uzasadnienie": "ok", "pewnosc": 0.7,
        "typ_projektu": "nowy", "session_id": "s1",
        "klient": "K", "opis_projektu": "o", "historia_klienta": "",
        "wzorce_ryzyk": "", "korekta_pm": None, "komentarz_pm": None,
        "zatwierdzone": False,
    })
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = ""
        client = TestClient(gepa.api.app)
        resp = client.post("/estimate", json={"klient": "K", "opis_projektu": "o"})
        assert resp.status_code == 200


def test_estimate_returns_401_with_wrong_key():
    """Jeśli api_key ustawiony — zły klucz daje 401."""
    mock_graph = MagicMock()
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = "secret123"
        client = TestClient(gepa.api.app)
        resp = client.post(
            "/estimate",
            json={"klient": "K", "opis_projektu": "o"},
            headers={"X-API-Key": "wrongkey"},
        )
        assert resp.status_code == 401


def test_estimate_passes_with_correct_key():
    """Poprawny klucz — 200."""
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "szacunek_godzin": 100, "uzasadnienie": "ok", "pewnosc": 0.7,
        "typ_projektu": "nowy", "session_id": "s1",
        "klient": "K", "opis_projektu": "o", "historia_klienta": "",
        "wzorce_ryzyk": "", "korekta_pm": None, "komentarz_pm": None,
        "zatwierdzone": False,
    })
    with patch.object(gepa.api, "_graph", mock_graph), \
         patch("gepa.api_auth.settings") as mock_settings:
        mock_settings.api_key = "secret123"
        client = TestClient(gepa.api.app)
        resp = client.post(
            "/estimate",
            json={"klient": "K", "opis_projektu": "o"},
            headers={"X-API-Key": "secret123"},
        )
        assert resp.status_code == 200
