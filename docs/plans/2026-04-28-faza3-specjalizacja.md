# Faza 3 — Specjalizacja per Typ Projektu: Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Dodanie klasyfikacji i specjalizacji per typ projektu (legacy/nowy/ai/migracja), per-type DSPy estimators z LangGraph routing, counter-based auto-trigger co 100 wycen oraz opcjonalna autentykacja API.

**Architecture:** Nowy `classify_node` w LangGraph wykrywa typ projektu → `estimation_node` wybiera dedykowany estimator z dict per typ → każdy typ akumuluje własne dane treningowe → `_increment_estimate_count()` triggeruje re-optymalizację co 100 wycen zamiast liczyć korekty. API key auth jako FastAPI dependency (opt-in).

**Tech Stack:** DSPy 2.6.27, LangGraph 1.x, FastAPI, Streamlit, Python 3.12

---

## Task 1: Klasyfikator DSPy — wykrywanie typu projektu

**Files:**
- Create: `gepa/dspy_modules/classifier.py`
- Create: `tests/dspy_modules/test_classifier.py`

**Step 1: Napisz failing testy**

```python
# tests/dspy_modules/test_classifier.py
def test_normalize_type_known():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("legacy") == "legacy"
    assert normalize_type("LEGACY system") == "legacy"
    assert normalize_type("ai") == "ai"
    assert normalize_type("machine learning") == "nowy"  # fallback


def test_normalize_type_unknown_returns_nowy():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("randomxyz") == "nowy"


def test_typy_projektow_list():
    from gepa.dspy_modules.classifier import TYPY_PROJEKTOW
    assert set(TYPY_PROJEKTOW) == {"legacy", "nowy", "ai", "migracja"}


def test_create_classifier_returns_chainofthought():
    import dspy
    from unittest.mock import patch
    with patch("dspy.settings") as _:
        from gepa.dspy_modules.classifier import create_classifier
        clf = create_classifier()
        assert isinstance(clf, dspy.ChainOfThought)
```

**Step 2: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/dspy_modules/test_classifier.py -v
```

Oczekiwane: FAIL — "cannot import name 'normalize_type'"

**Step 3: Utwórz `gepa/dspy_modules/classifier.py`**

```python
import dspy

TYPY_PROJEKTOW = ["legacy", "nowy", "ai", "migracja"]


class KlasyfikacjaTypu(dspy.Signature):
    """Sklasyfikuj typ projektu IT na podstawie jego opisu."""

    opis_projektu: str = dspy.InputField(
        desc="Opis projektu IT"
    )
    typ_projektu: str = dspy.OutputField(
        desc=(
            "Typ projektu — JEDNO słowo: "
            "legacy (modernizacja/utrzymanie starego systemu), "
            "nowy (nowy system od zera), "
            "ai (projekt z ML/AI/LLM), "
            "migracja (przeniesienie do chmury lub nowej platformy)"
        )
    )


def create_classifier() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(KlasyfikacjaTypu)


def normalize_type(raw: str) -> str:
    cleaned = raw.lower().strip()
    for typ in TYPY_PROJEKTOW:
        if typ in cleaned:
            return typ
    return "nowy"
```

**Step 4: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/dspy_modules/test_classifier.py -v
```

**Step 5: Commit**

```bash
git add gepa/dspy_modules/classifier.py tests/dspy_modules/test_classifier.py
git commit -m "feat: DSPy classifier for project type detection"
```

---

## Task 2: EstimationState + typ_projektu w API

**Files:**
- Modify: `gepa/graph/state.py`
- Modify: `gepa/api.py` (initial_state + response)
- Modify: `tests/graph/test_workflow.py` (update state fixture)
- Modify: `tests/test_api.py` (update mock return value)

**Step 1: Zaktualizuj `gepa/graph/state.py`**

Zastąp całą zawartość:

```python
from typing import TypedDict


class EstimationState(TypedDict):
    session_id: str
    klient: str
    opis_projektu: str
    typ_projektu: str
    historia_klienta: str
    wzorce_ryzyk: str
    szacunek_godzin: int | None
    uzasadnienie: str | None
    pewnosc: float | None
    korekta_pm: int | None
    komentarz_pm: str | None
    zatwierdzone: bool
```

**Step 2: Zaktualizuj `tests/graph/test_workflow.py`**

W `test_estimation_state_fields` dodaj `"typ_projektu": "nowy"` do słownika state:

```python
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
```

**Step 3: Zaktualizuj `tests/test_api.py`**

W `test_estimate_endpoint_returns_required_fields` dodaj `"typ_projektu": "nowy"` do mock ainvoke return value:

```python
mock_compiled.ainvoke = AsyncMock(return_value={
    "szacunek_godzin": 120,
    "uzasadnienie": "Test uzasadnienia.",
    "pewnosc": 0.75,
    "typ_projektu": "nowy",
    "session_id": "test-001",
    "klient": "Klient TEST",
    "opis_projektu": "Portal webowy",
    "historia_klienta": "",
    "wzorce_ryzyk": "",
    "korekta_pm": None,
    "komentarz_pm": None,
    "zatwierdzone": False,
})
```

Oraz dodaj asercję w tym teście:
```python
assert "typ_projektu" in data
```

**Step 4: Zaktualizuj `gepa/api.py` — initial_state i response**

W funkcji `estimate`, w `initial_state` dodaj `"typ_projektu": ""`:

```python
initial_state = {
    "session_id": thread_id,
    "klient": req.klient,
    "opis_projektu": req.opis_projektu,
    "typ_projektu": "",
    "historia_klienta": "",
    "wzorce_ryzyk": "",
    "szacunek_godzin": None,
    "uzasadnienie": None,
    "pewnosc": None,
    "korekta_pm": None,
    "komentarz_pm": None,
    "zatwierdzone": False,
}
```

W return z `/estimate` dodaj `"typ_projektu": result.get("typ_projektu", "nowy")`:

```python
return {
    "session_id": thread_id,
    "szacunek_godzin": result["szacunek_godzin"],
    "uzasadnienie": result["uzasadnienie"],
    "pewnosc": result["pewnosc"],
    "typ_projektu": result.get("typ_projektu", "nowy"),
}
```

**Step 5: Uruchom testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -20
```

Oczekiwane: wszystkie PASS

**Step 6: Commit**

```bash
git add gepa/graph/state.py gepa/api.py tests/graph/test_workflow.py tests/test_api.py
git commit -m "feat: add typ_projektu to EstimationState and API response"
```

---

## Task 3: classify_node i per-type estimators w LangGraph

**Files:**
- Modify: `gepa/graph/workflow.py`
- Modify: `tests/graph/test_workflow.py`
- Create: `tests/graph/test_routing.py`

**Step 1: Napisz failing testy**

```python
# tests/graph/test_routing.py
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
```

**Step 2: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/graph/test_routing.py -v
```

**Step 3: Zaktualizuj `gepa/graph/workflow.py`**

Zastąp całą zawartość:

```python
import uuid
import json as _json
import logging
import os
from pathlib import Path
import dspy
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from gepa.graph.state import EstimationState
from gepa.memory.graphiti_client import GraphitiClient
from gepa.dspy_modules.estimator import create_estimator
from gepa.dspy_modules.classifier import create_classifier, normalize_type, TYPY_PROJEKTOW
from gepa.optimization.optimizer import OptimizerRunner

logger = logging.getLogger(__name__)

TRAINING_DIR = os.environ.get("TRAINING_DIR", "gepa/data/training")
ESTIMATES_FILE = os.environ.get("ESTIMATES_FILE", "gepa/data/estimates_count.json")
GEPA_TRIGGER_EVERY = int(os.environ.get("GEPA_TRIGGER_EVERY", "100"))


def _save_to_trainset(state: EstimationState, rzeczywiste_godziny: int) -> None:
    entry = {
        "opis_projektu": state["opis_projektu"],
        "rzeczywiste_godziny": rzeczywiste_godziny,
        "typ_projektu": state.get("typ_projektu", "nowy"),
        "historia_klienta": state.get("historia_klienta", ""),
        "wzorce_ryzyk": state.get("wzorce_ryzyk", ""),
        "komentarz_pm": state.get("komentarz_pm", ""),
        "zrodlo": "hitl",
    }
    path = Path(TRAINING_DIR) / f"hitl_{uuid.uuid4().hex[:8]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json.dumps(entry, ensure_ascii=False, indent=2))


def _increment_estimate_count() -> int:
    path = Path(ESTIMATES_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        count = _json.loads(path.read_text())["count"] if path.exists() else 0
    except Exception:
        count = 0
    count += 1
    path.write_text(_json.dumps({"count": count}, ensure_ascii=False))
    return count


def create_graph(checkpointer=None, graphiti_client=None, estimator=None, estimators=None):
    graphiti = graphiti_client or GraphitiClient()
    classifier = create_classifier()

    if estimators is None:
        if estimator is not None:
            estimators = {typ: estimator for typ in TYPY_PROJEKTOW}
        else:
            estimators = {typ: create_estimator() for typ in TYPY_PROJEKTOW}

    async def intake_node(state: EstimationState) -> dict:
        if not state.get("session_id"):
            return {"session_id": str(uuid.uuid4())}
        return {}

    async def classify_node(state: EstimationState) -> dict:
        result = classifier(opis_projektu=state["opis_projektu"])
        return {"typ_projektu": normalize_type(result.typ_projektu)}

    async def context_node(state: EstimationState) -> dict:
        typ = state.get("typ_projektu", "nowy")
        historia = await graphiti.get_context(
            state["klient"], state["opis_projektu"], typ
        )
        wzorce = await graphiti.get_risk_patterns(state["opis_projektu"])
        return {"historia_klienta": historia, "wzorce_ryzyk": wzorce}

    async def estimation_node(state: EstimationState) -> dict:
        typ = state.get("typ_projektu", "nowy")
        est = estimators.get(typ) or estimators.get("nowy") or list(estimators.values())[0]
        result = est(
            opis_projektu=state["opis_projektu"],
            historia_klienta=state["historia_klienta"],
            wzorce_ryzyk=state["wzorce_ryzyk"],
        )
        return {
            "szacunek_godzin": result.szacunek_godzin,
            "uzasadnienie": result.uzasadnienie,
            "pewnosc": result.pewnosc,
        }

    async def store_node(state: EstimationState) -> dict:
        godziny = state.get("korekta_pm") or state["szacunek_godzin"]
        typ = state.get("typ_projektu", "nowy")
        content = (
            f"Projekt: {state['opis_projektu']}\n"
            f"Typ: {typ}\n"
            f"Klient: {state['klient']}\n"
            f"Szacunek agenta: {state['szacunek_godzin']} godz.\n"
            f"Rzeczywiste (PM): {godziny} godz.\n"
            f"Komentarz PM: {state.get('komentarz_pm', '')}"
        )
        await graphiti.add_episode(state["session_id"], content)

        if state.get("korekta_pm"):
            _save_to_trainset(state, godziny)

        count = _increment_estimate_count()
        if count % GEPA_TRIGGER_EVERY == 0:
            runner = OptimizerRunner()
            try:
                est = estimators.get("nowy") or list(estimators.values())[0]
                runner.run(student=est, training_dir=TRAINING_DIR)
            except Exception:
                logger.exception("[GEPA] Optymalizacja nie powiodła się")

        return {"zatwierdzone": True}

    builder = StateGraph(EstimationState)
    builder.add_node("intake", intake_node)
    builder.add_node("classify", classify_node)
    builder.add_node("context", context_node)
    builder.add_node("estimation", estimation_node)
    builder.add_node("store", store_node)

    builder.set_entry_point("intake")
    builder.add_edge("intake", "classify")
    builder.add_edge("classify", "context")
    builder.add_edge("context", "estimation")
    builder.add_edge("estimation", "store")
    builder.add_edge("store", END)

    cp = checkpointer or MemorySaver()
    return builder.compile(checkpointer=cp, interrupt_before=["store"])
```

**Step 4: Zaktualizuj `tests/graph/test_workflow.py`**

W `test_workflow_has_required_nodes` dodaj patch dla `create_classifier` i asercję dla węzła "classify":

```python
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
```

**Step 5: Uruchom testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -25
```

UWAGA: Test `test_store_node_does_not_trigger_below_threshold` może wymagać aktualizacji jeśli patches się zmieniły — sprawdź i napraw jeśli fail.

**Step 6: Commit**

```bash
git add gepa/graph/workflow.py tests/graph/test_workflow.py tests/graph/test_routing.py
git commit -m "feat: classify_node, per-type estimators, counter-based auto-trigger"
```

---

## Task 4: Graphiti — kontekst per typ projektu

**Files:**
- Modify: `gepa/memory/graphiti_client.py`
- Modify: `tests/memory/test_graphiti_client.py` (jeśli istnieje) lub utwórz

**Step 1: Sprawdź czy istnieje `tests/memory/test_graphiti_client.py`**

```bash
ls /Users/adamdabrowski/PycharmProjects/GEPA/tests/memory/ 2>/dev/null || echo "brak katalogu"
```

**Step 2: Napisz failing testy**

Utwórz `tests/memory/__init__.py` (jeśli brak) i `tests/memory/test_graphiti_client.py`:

```python
# tests/memory/test_graphiti_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_graphiti_client_get_context_accepts_typ():
    with patch("gepa.memory.graphiti_client.Graphiti") as mock_g:
        mock_g.return_value.search = AsyncMock(return_value=[])
        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient()
        import asyncio
        result = asyncio.run(client.get_context("KlientABC", "portal", "legacy"))
        assert isinstance(result, str)


def test_graphiti_client_get_context_includes_type_in_query():
    with patch("gepa.memory.graphiti_client.Graphiti") as mock_g:
        search_mock = AsyncMock(return_value=[])
        mock_g.return_value.search = search_mock
        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient()
        import asyncio
        asyncio.run(client.get_context("KlientX", "opis", "ai"))
        call_args = search_mock.call_args[0][0]
        assert "ai" in call_args.lower()
```

**Step 3: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/memory/test_graphiti_client.py -v
```

**Step 4: Zaktualizuj `gepa/memory/graphiti_client.py`**

Zmień sygnaturę `get_context` — dodaj parametr `typ_projektu`:

```python
async def get_context(self, klient: str, opis_projektu: str, typ_projektu: str = "nowy") -> str:
    results = await self.graphiti.search(
        f"historia projektów {typ_projektu} klienta {klient}: {opis_projektu}"
    )
    if not results:
        return "Brak historii klienta w bazie wiedzy."
    return "\n".join(r.fact for r in results[:5])
```

**Step 5: Uruchom testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -20
```

**Step 6: Commit**

```bash
git add gepa/memory/graphiti_client.py tests/memory/__init__.py tests/memory/test_graphiti_client.py
git commit -m "feat: type-aware Graphiti context search"
```

---

## Task 5: REST API key auth (opt-in)

**Files:**
- Modify: `gepa/config/settings.py`
- Create: `gepa/api_auth.py`
- Modify: `gepa/api.py`
- Create: `tests/test_api_auth.py`

**Step 1: Napisz failing testy**

```python
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
```

**Step 2: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/test_api_auth.py -v
```

**Step 3: Zaktualizuj `gepa/config/settings.py` — dodaj api_key**

W klasie Settings dodaj po `mlflow_tracking_uri`:
```python
api_key: str = ""
```

**Step 4: Utwórz `gepa/api_auth.py`**

```python
from fastapi import Header, HTTPException, status
from gepa.config.settings import settings


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy klucz API.",
        )
```

**Step 5: Zaktualizuj `gepa/api.py` — dodaj dependency do POST endpoints**

Dodaj import na górze:
```python
from gepa.api_auth import verify_api_key
from fastapi import Depends
```

Zaktualizuj dekoratory POST:
```python
@app.post("/estimate", dependencies=[Depends(verify_api_key)])
async def estimate(req: EstimateRequest):
    ...

@app.post("/approve", dependencies=[Depends(verify_api_key)])
async def approve(req: ApproveRequest):
    ...

@app.post("/model/reload", dependencies=[Depends(verify_api_key)])
async def model_reload():
    ...
```

**Step 6: Uruchom testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -25
```

**Step 7: Commit**

```bash
git add gepa/config/settings.py gepa/api_auth.py gepa/api.py tests/test_api_auth.py
git commit -m "feat: optional API key auth via X-API-Key header"
```

---

## Task 6: Streamlit — wyświetl typ projektu

**Files:**
- Modify: `gepa/app.py`

**Step 1: Zaktualizuj sekcję "review" w `gepa/app.py`**

W bloku `elif st.session_state.phase == "review":` — zmień metryki (obecne 3 kolumny) na 4 kolumny, dodając typ projektu:

Znajdź:
```python
col1, col2, col3 = st.columns(3)
col1.metric("Szacunek (godz.)", r["szacunek_godzin"])
col2.metric("Pewność", f"{r['pewnosc']:.0%}")
col3.metric("Sesja", r["session_id"][:8] + "...")
```

Zamień na:
```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Szacunek (godz.)", r["szacunek_godzin"])
col2.metric("Pewność", f"{r['pewnosc']:.0%}")
col3.metric("Typ projektu", r.get("typ_projektu", "nowy").upper())
col4.metric("Sesja", r["session_id"][:8] + "...")
```

**Step 2: Weryfikacja składni**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/python -m py_compile gepa/app.py && echo "OK"
```

**Step 3: Commit**

```bash
git add gepa/app.py
git commit -m "feat: show project type in Streamlit estimate results"
```

---

## Task 7: E2E smoke test Fazy 3 i wszystkie testy

**Files:**
- Create: `tests/test_faza3_smoke.py`

**Step 1: Utwórz `tests/test_faza3_smoke.py`**

```python
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import tempfile
import json


def test_faza3_imports():
    from gepa.dspy_modules.classifier import create_classifier, normalize_type, TYPY_PROJEKTOW
    from gepa.api_auth import verify_api_key
    assert len(TYPY_PROJEKTOW) == 4


def test_normalize_type_all_types():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("legacy") == "legacy"
    assert normalize_type("nowy portal") == "nowy"
    assert normalize_type("ai projekt") == "ai"
    assert normalize_type("migracja chmura") == "migracja"
    assert normalize_type("nieznany") == "nowy"


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
        assert "estimation" in graph.nodes


def test_estimate_counter_increments():
    with tempfile.TemporaryDirectory() as tmpdir:
        import os
        counter_file = Path(tmpdir) / "estimates_count.json"
        import gepa.graph.workflow as wf
        with patch.object(wf, "ESTIMATES_FILE", str(counter_file)):
            c1 = wf._increment_estimate_count()
            c2 = wf._increment_estimate_count()
            assert c2 == c1 + 1
            assert counter_file.exists()


def test_api_responds_with_typ_projektu():
    import gepa.api as api_module
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "szacunek_godzin": 80, "uzasadnienie": "ok", "pewnosc": 0.6,
        "typ_projektu": "ai", "session_id": "s2",
        "klient": "K", "opis_projektu": "ML system", "historia_klienta": "",
        "wzorce_ryzyk": "", "korekta_pm": None, "komentarz_pm": None,
        "zatwierdzone": False,
    })
    from fastapi.testclient import TestClient
    with patch.object(api_module, "_graph", mock_graph):
        client = TestClient(api_module.app)
        resp = client.post("/estimate", json={"klient": "K", "opis_projektu": "ML system"})
        assert resp.status_code == 200
        assert resp.json()["typ_projektu"] == "ai"
```

**Step 2: Uruchom WSZYSTKIE testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -30
```

Oczekiwane: wszystkie PASS. Jeśli jakiś test failuje — zbadaj i napraw.

**Step 3: Commit końcowy Fazy 3**

```bash
git add tests/test_faza3_smoke.py
git commit -m "feat: Faza 3 complete — per-type estimation, routing, API auth"
```

---

## Podsumowanie Fazy 3

Po ukończeniu tej fazy:
- Klasyfikator DSPy wykrywa typ projektu (legacy/nowy/ai/migracja)
- LangGraph: intake → **classify** → context → estimation → store
- Per-type estimators w create_graph (dict[str, dspy.Module])
- Counter-based auto-trigger co 100 wycen (GEPA_TRIGGER_EVERY)
- Kontekst Graphiti uwzględnia typ projektu w zapytaniu
- REST API z opcjonalną autentykacją klucza (X-API-Key)
- Streamlit wyświetla typ projektu w wynikach wyceny

**Podmiana estimatora per typ:** gdy zbudujesz 50+ przykładów dla konkretnego typu, uruchom `OptimizerRunner` osobno dla każdego, ładuj wynikowy .json do odpowiedniego estimatora w dict.

**Następny krok: Faza 4** — per-type optimization pipeline, A/B evaluation, produkcyjny deployment.
