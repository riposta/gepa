# Faza 1 — Fundament: Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Zbudowanie działającego agenta wyceny projektów IT z pamięcią Graphiti, HITL w Streamlit i LangGraph orchestracją — bez GEPA optymalizacji (zbieramy dane do Fazy 2).

**Architecture:** LangGraph graf (5 węzłów + HITL interrupt) orkiestruje przepływ od zebrania opisu projektu, przez pobranie kontekstu z Graphiti, wygenerowanie wyceny przez DSPy ChainOfThought, zatwierdzenie przez PM, aż po zapis wyniku z korektą. FastAPI jest cienkim bridge'em między Streamlit a LangGraph.

**Tech Stack:** Python 3.12, DSPy 2.x, LangGraph 0.2+, Graphiti-core, LiteLLM, FastAPI, Streamlit, Pydantic 2.x, pytest

---

## Task 1: Setup projektu — pyproject.toml i struktura katalogów

**Files:**
- Create: `pyproject.toml`
- Create: `gepa/__init__.py`
- Create: `gepa/config/settings.py`
- Create: `tests/__init__.py`
- Create: `.env.example`

**Step 1: Utwórz strukturę katalogów**

```bash
mkdir -p gepa/{config,graph,dspy_modules/programs,memory,optimization,data/training}
mkdir -p tests/{graph,dspy_modules,memory,optimization}
touch gepa/__init__.py gepa/config/__init__.py gepa/graph/__init__.py
touch gepa/dspy_modules/__init__.py gepa/memory/__init__.py gepa/optimization/__init__.py
touch tests/__init__.py tests/graph/__init__.py tests/dspy_modules/__init__.py
touch tests/memory/__init__.py tests/optimization/__init__.py
```

**Step 2: Utwórz `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "gepa"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "dspy-ai>=2.6",
    "langgraph>=0.2",
    "langchain-core>=0.3",
    "graphiti-core>=0.3",
    "litellm>=1.40",
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "streamlit>=1.35",
    "pydantic>=2.7",
    "pydantic-settings>=2.3",
    "httpx>=0.27",
    "python-dotenv>=1.0",
    "mlflow>=2.14",
    "langfuse>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.14",
    "ruff>=0.4",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 3: Utwórz `gepa/config/settings.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_model: str = "openai/gpt-4o-mini"
    llm_api_base: str = ""
    llm_api_key: str = ""

    graphiti_neo4j_uri: str = "bolt://localhost:7687"
    graphiti_neo4j_user: str = "neo4j"
    graphiti_neo4j_password: str = "password"

    gepa_trigger_threshold: int = 50
    programs_dir: str = "gepa/dspy_modules/programs"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    mlflow_tracking_uri: str = "mlruns"


settings = Settings()
```

**Step 4: Utwórz `.env.example`**

```bash
LLM_MODEL=openai/gpt-4o-mini
LLM_API_BASE=
LLM_API_KEY=sk-...

GRAPHITI_NEO4J_URI=bolt://localhost:7687
GRAPHITI_NEO4J_USER=neo4j
GRAPHITI_NEO4J_PASSWORD=password

GEPA_TRIGGER_THRESHOLD=50
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

**Step 5: Zainstaluj zależności**

```bash
pip install -e ".[dev]"
```

**Step 6: Napisz test sprawdzający import settings**

```python
# tests/test_settings.py
def test_settings_defaults():
    from gepa.config.settings import settings
    assert settings.gepa_trigger_threshold == 50
    assert settings.programs_dir == "gepa/dspy_modules/programs"
```

**Step 7: Uruchom test**

```bash
pytest tests/test_settings.py -v
```
Oczekiwane: PASS

**Step 8: Commit**

```bash
git init
git add pyproject.toml gepa/ tests/ .env.example
git commit -m "feat: project scaffold with settings and dependencies"
```

---

## Task 2: DSPy Signature i moduł estymacji

**Files:**
- Create: `gepa/dspy_modules/signatures.py`
- Create: `gepa/dspy_modules/estimator.py`
- Create: `tests/dspy_modules/test_estimator.py`

**Step 1: Napisz failing test**

```python
# tests/dspy_modules/test_estimator.py
import pytest
from unittest.mock import patch, MagicMock


def test_estimator_returns_required_fields():
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(
            szacunek_godzin=120,
            uzasadnienie="Projekt wymaga 3 sprintów.",
            pewnosc=0.75,
        )
        mock_cot.return_value = mock_instance

        from gepa.dspy_modules.estimator import create_estimator
        estimator = create_estimator()
        result = estimator(
            opis_projektu="REST API w Django",
            historia_klienta="Brak historii.",
            wzorce_ryzyk="Brak wzorców.",
        )

        assert hasattr(result, "szacunek_godzin")
        assert hasattr(result, "uzasadnienie")
        assert hasattr(result, "pewnosc")
```

**Step 2: Uruchom test — upewnij się że FAIL**

```bash
pytest tests/dspy_modules/test_estimator.py -v
```
Oczekiwane: FAIL — "cannot import name 'create_estimator'"

**Step 3: Utwórz `gepa/dspy_modules/signatures.py`**

```python
import dspy


class WycenaIT(dspy.Signature):
    """Wycena projektu IT w roboczogodzinach na podstawie opisu i historii."""

    opis_projektu: str = dspy.InputField(
        desc="Pełen opis wymagań projektu IT"
    )
    historia_klienta: str = dspy.InputField(
        desc="Historia poprzednich projektów klienta z Graphiti (lub 'Brak historii.')"
    )
    wzorce_ryzyk: str = dspy.InputField(
        desc="Wyuczone wzorce ryzyk z Graphiti (lub 'Brak wzorców.')"
    )

    szacunek_godzin: int = dspy.OutputField(
        desc="Szacunkowa liczba roboczogodzin (liczba całkowita)"
    )
    uzasadnienie: str = dspy.OutputField(
        desc="Szczegółowe wyjaśnienie metodyki wyceny z podziałem na komponenty"
    )
    pewnosc: float = dspy.OutputField(
        desc="Pewność wyceny od 0.0 (brak pewności) do 1.0 (pełna pewność)"
    )
```

**Step 4: Utwórz `gepa/dspy_modules/estimator.py`**

```python
import dspy
from gepa.dspy_modules.signatures import WycenaIT


def create_estimator() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(WycenaIT)
```

**Step 5: Uruchom test — sprawdź PASS**

```bash
pytest tests/dspy_modules/test_estimator.py -v
```
Oczekiwane: PASS

**Step 6: Commit**

```bash
git add gepa/dspy_modules/ tests/dspy_modules/
git commit -m "feat: DSPy WycenaIT signature and ChainOfThought estimator"
```

---

## Task 3: Schematy Pydantic i klient Graphiti

**Files:**
- Create: `gepa/memory/schemas.py`
- Create: `gepa/memory/graphiti_client.py`
- Create: `tests/memory/test_graphiti_client.py`

**Step 1: Utwórz `gepa/memory/schemas.py`**

```python
from pydantic import BaseModel


class ProjektIT(BaseModel):
    nazwa: str
    technologie: list[str]
    typ: str  # "nowy" | "legacy" | "migracja" | "ai"
    budzet_szacowany_godz: float | None = None
    budzet_rzeczywisty_godz: float | None = None
    odchylenie_procent: float | None = None


class Klient(BaseModel):
    nazwa: str
    branza: str
    preferencje_wyceny: str = "szczegółowy"


class WzorzecRyzyka(BaseModel):
    opis: str
    typowy_narzut_procent: float
    kiedy_wystepuje: str
```

**Step 2: Napisz failing testy dla klienta Graphiti**

```python
# tests/memory/test_graphiti_client.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_get_context_returns_string_on_empty():
    with patch("graphiti_core.Graphiti") as mock_graphiti:
        mock_instance = AsyncMock()
        mock_instance.search.return_value = []
        mock_graphiti.return_value = mock_instance

        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient.__new__(GraphitiClient)
        client.graphiti = mock_instance

        result = await client.get_context("nieznany klient", "nowy projekt")
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_add_episode_calls_graphiti():
    with patch("graphiti_core.Graphiti") as mock_graphiti:
        mock_instance = AsyncMock()
        mock_graphiti.return_value = mock_instance

        from gepa.memory.graphiti_client import GraphitiClient
        client = GraphitiClient.__new__(GraphitiClient)
        client.graphiti = mock_instance

        await client.add_episode(
            session_id="test_session",
            content="Projekt X: 120 godzin, szacunek 110 godzin.",
        )
        mock_instance.add_episode.assert_called_once()
```

**Step 3: Uruchom testy — upewnij się że FAIL**

```bash
pytest tests/memory/test_graphiti_client.py -v
```
Oczekiwane: FAIL — "cannot import name 'GraphitiClient'"

**Step 4: Utwórz `gepa/memory/graphiti_client.py`**

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from gepa.config.settings import settings


class GraphitiClient:
    def __init__(self) -> None:
        self.graphiti = Graphiti(
            settings.graphiti_neo4j_uri,
            settings.graphiti_neo4j_user,
            settings.graphiti_neo4j_password,
        )

    async def get_context(self, klient: str, opis_projektu: str) -> str:
        results = await self.graphiti.search(
            f"historia projektów klienta {klient}: {opis_projektu}"
        )
        if not results:
            return "Brak historii klienta w bazie wiedzy."
        return "\n".join(r.fact for r in results[:5])

    async def get_risk_patterns(self, opis_projektu: str) -> str:
        results = await self.graphiti.search(
            f"wzorce ryzyk wycena: {opis_projektu}"
        )
        if not results:
            return "Brak wyuczonych wzorców ryzyk."
        return "\n".join(r.fact for r in results[:3])

    async def add_episode(self, session_id: str, content: str) -> None:
        await self.graphiti.add_episode(
            name=session_id,
            episode_body=content,
            source=EpisodeType.text,
        )

    async def close(self) -> None:
        await self.graphiti.close()
```

**Step 5: Uruchom testy — sprawdź PASS**

```bash
pytest tests/memory/test_graphiti_client.py -v
```
Oczekiwane: PASS

**Step 6: Commit**

```bash
git add gepa/memory/ tests/memory/
git commit -m "feat: Graphiti client and Pydantic schemas"
```

---

## Task 4: LangGraph — State i workflow

**Files:**
- Create: `gepa/graph/state.py`
- Create: `gepa/graph/workflow.py`
- Create: `tests/graph/test_workflow.py`

**Step 1: Utwórz `gepa/graph/state.py`**

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class EstimationState(TypedDict):
    session_id: str
    klient: str
    opis_projektu: str
    historia_klienta: str
    wzorce_ryzyk: str
    szacunek_godzin: int | None
    uzasadnienie: str | None
    pewnosc: float | None
    korekta_pm: int | None
    komentarz_pm: str | None
    zatwierdzone: bool
```

**Step 2: Napisz failing testy dla workflow**

```python
# tests/graph/test_workflow.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_workflow_has_required_nodes():
    with patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("gepa.dspy_modules.estimator.create_estimator"):
        from gepa.graph.workflow import create_graph
        graph = create_graph()
        assert "intake" in graph.nodes
        assert "context" in graph.nodes
        assert "estimation" in graph.nodes
        assert "store" in graph.nodes


@pytest.mark.asyncio
async def test_initial_state_missing_fields_handled():
    state = {
        "session_id": "test-001",
        "klient": "Klient ABC",
        "opis_projektu": "Nowy portal internetowy",
        "historia_klienta": "",
        "wzorce_ryzyk": "",
        "szacunek_godzin": None,
        "uzasadnienie": None,
        "pewnosc": None,
        "korekta_pm": None,
        "komentarz_pm": None,
        "zatwierdzone": False,
    }
    from gepa.graph.state import EstimationState
    typed: EstimationState = state
    assert typed["zatwierdzone"] is False
    assert typed["szacunek_godzin"] is None
```

**Step 3: Uruchom testy — upewnij się że FAIL**

```bash
pytest tests/graph/test_workflow.py -v
```
Oczekiwane: FAIL — "cannot import name 'create_graph'"

**Step 4: Utwórz `gepa/graph/workflow.py`**

```python
import dspy
import uuid
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from gepa.graph.state import EstimationState
from gepa.memory.graphiti_client import GraphitiClient
from gepa.dspy_modules.estimator import create_estimator
from gepa.config.settings import settings


def create_graph(checkpointer=None):
    graphiti = GraphitiClient()
    estimator = create_estimator()

    async def intake_node(state: EstimationState) -> EstimationState:
        if not state.get("session_id"):
            state["session_id"] = str(uuid.uuid4())
        return state

    async def context_node(state: EstimationState) -> EstimationState:
        historia = await graphiti.get_context(
            state["klient"], state["opis_projektu"]
        )
        wzorce = await graphiti.get_risk_patterns(state["opis_projektu"])
        return {**state, "historia_klienta": historia, "wzorce_ryzyk": wzorce}

    async def estimation_node(state: EstimationState) -> EstimationState:
        result = estimator(
            opis_projektu=state["opis_projektu"],
            historia_klienta=state["historia_klienta"],
            wzorce_ryzyk=state["wzorce_ryzyk"],
        )
        return {
            **state,
            "szacunek_godzin": result.szacunek_godzin,
            "uzasadnienie": result.uzasadnienie,
            "pewnosc": result.pewnosc,
        }

    async def store_node(state: EstimationState) -> EstimationState:
        godziny = state.get("korekta_pm") or state["szacunek_godzin"]
        content = (
            f"Projekt: {state['opis_projektu']}\n"
            f"Klient: {state['klient']}\n"
            f"Szacunek agenta: {state['szacunek_godzin']} godz.\n"
            f"Rzeczywiste (PM): {godziny} godz.\n"
            f"Komentarz PM: {state.get('komentarz_pm', '')}"
        )
        await graphiti.add_episode(state["session_id"], content)
        return state

    builder = StateGraph(EstimationState)
    builder.add_node("intake", intake_node)
    builder.add_node("context", context_node)
    builder.add_node("estimation", estimation_node)
    builder.add_node("store", store_node)

    builder.set_entry_point("intake")
    builder.add_edge("intake", "context")
    builder.add_edge("context", "estimation")
    builder.add_edge("store", END)

    # HITL interrupt po estimation — PM musi zatwierdzić
    builder.add_edge("estimation", "store")

    cp = checkpointer or MemorySaver()
    return builder.compile(checkpointer=cp, interrupt_before=["store"])
```

**Step 5: Uruchom testy**

```bash
pytest tests/graph/test_workflow.py -v
```
Oczekiwane: PASS

**Step 6: Commit**

```bash
git add gepa/graph/ tests/graph/
git commit -m "feat: LangGraph workflow with HITL interrupt before store"
```

---

## Task 5: FastAPI bridge

**Files:**
- Create: `gepa/api.py`
- Create: `tests/test_api.py`

**Step 1: Napisz failing test**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock


def test_estimate_endpoint_exists():
    with patch("gepa.graph.workflow.create_graph") as mock_graph:
        mock_compiled = MagicMock()
        mock_compiled.ainvoke = AsyncMock(return_value={
            "szacunek_godzin": 120,
            "uzasadnienie": "Test uzasadnienia.",
            "pewnosc": 0.75,
            "session_id": "test-001",
        })
        mock_graph.return_value = mock_compiled

        from gepa.api import app
        client = TestClient(app)
        response = client.post("/estimate", json={
            "klient": "Klient TEST",
            "opis_projektu": "Portal webowy",
        })
        assert response.status_code == 200
        data = response.json()
        assert "szacunek_godzin" in data
        assert "session_id" in data


def test_approve_endpoint_exists():
    with patch("gepa.graph.workflow.create_graph") as mock_graph:
        mock_compiled = MagicMock()
        mock_compiled.ainvoke = AsyncMock(return_value={"zatwierdzone": True})
        mock_graph.return_value = mock_compiled

        from gepa.api import app
        client = TestClient(app)
        response = client.post("/approve", json={
            "session_id": "test-001",
            "zatwierdzone": True,
        })
        assert response.status_code == 200
```

**Step 2: Uruchom testy — FAIL**

```bash
pytest tests/test_api.py -v
```
Oczekiwane: FAIL — "cannot import name 'app'"

**Step 3: Utwórz `gepa/api.py`**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from gepa.graph.workflow import create_graph
from gepa.config.settings import settings
import dspy
import litellm


graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    lm = dspy.LM(
        model=settings.llm_model,
        api_base=settings.llm_api_base or None,
        api_key=settings.llm_api_key or None,
    )
    dspy.configure(lm=lm)
    graph = create_graph()
    yield


app = FastAPI(title="GEPA Estimation API", lifespan=lifespan)


class EstimateRequest(BaseModel):
    klient: str
    opis_projektu: str


class ApproveRequest(BaseModel):
    session_id: str
    zatwierdzone: bool
    korekta_pm: int | None = None
    komentarz_pm: str | None = None


@app.post("/estimate")
async def estimate(req: EstimateRequest):
    config = {"configurable": {"thread_id": req.klient}}
    initial_state = {
        "session_id": "",
        "klient": req.klient,
        "opis_projektu": req.opis_projektu,
        "historia_klienta": "",
        "wzorce_ryzyk": "",
        "szacunek_godzin": None,
        "uzasadnienie": None,
        "pewnosc": None,
        "korekta_pm": None,
        "komentarz_pm": None,
        "zatwierdzone": False,
    }
    result = await graph.ainvoke(initial_state, config)
    return {
        "session_id": result["session_id"],
        "szacunek_godzin": result["szacunek_godzin"],
        "uzasadnienie": result["uzasadnienie"],
        "pewnosc": result["pewnosc"],
    }


@app.post("/approve")
async def approve(req: ApproveRequest):
    config = {"configurable": {"thread_id": req.session_id}}
    update = {
        "zatwierdzone": req.zatwierdzone,
        "korekta_pm": req.korekta_pm,
        "komentarz_pm": req.komentarz_pm,
    }
    await graph.aupdate_state(config, update)
    result = await graph.ainvoke(None, config)
    return {"status": "saved", "session_id": req.session_id}
```

**Step 4: Uruchom testy**

```bash
pytest tests/test_api.py -v
```
Oczekiwane: PASS

**Step 5: Commit**

```bash
git add gepa/api.py tests/test_api.py
git commit -m "feat: FastAPI bridge for LangGraph with estimate and approve endpoints"
```

---

## Task 6: Streamlit UI

**Files:**
- Create: `gepa/app.py`

*(Streamlit nie jest testowalny unit-testami — testujemy manualnie)*

**Step 1: Utwórz `gepa/app.py`**

```python
import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="GEPA — Wycena IT", layout="wide")
st.title("Agent Wyceny Projektów IT")

if "phase" not in st.session_state:
    st.session_state.phase = "input"
    st.session_state.result = None
    st.session_state.session_id = None

if st.session_state.phase == "input":
    with st.form("wycena_form"):
        klient = st.text_input("Nazwa klienta", placeholder="np. Orange Polska")
        opis = st.text_area(
            "Opis projektu",
            height=200,
            placeholder="Opisz wymagania projektu, technologie, zakres...",
        )
        submitted = st.form_submit_button("Wyceń projekt")

    if submitted and klient and opis:
        with st.spinner("Generuję wycenę..."):
            resp = httpx.post(
                f"{API_BASE}/estimate",
                json={"klient": klient, "opis_projektu": opis},
                timeout=60,
            )
            if resp.status_code == 200:
                st.session_state.result = resp.json()
                st.session_state.session_id = resp.json()["session_id"]
                st.session_state.phase = "review"
                st.rerun()
            else:
                st.error(f"Błąd API: {resp.text}")

elif st.session_state.phase == "review":
    r = st.session_state.result
    st.subheader("Wynik wyceny")

    col1, col2, col3 = st.columns(3)
    col1.metric("Szacunek (godz.)", r["szacunek_godzin"])
    col2.metric("Pewność", f"{r['pewnosc']:.0%}")
    col3.metric("Sesja", r["session_id"][:8] + "...")

    st.markdown("**Uzasadnienie:**")
    st.info(r["uzasadnienie"])

    st.divider()
    st.subheader("Ocena PM")

    with st.form("approve_form"):
        decision = st.radio("Decyzja", ["Zatwierdź", "Koryguj"])
        korekta = None
        komentarz = ""
        if decision == "Koryguj":
            korekta = st.number_input(
                "Rzeczywista liczba godzin (Twoja ocena)",
                min_value=1,
                value=r["szacunek_godzin"],
            )
            komentarz = st.text_area("Komentarz (opcjonalny)")
        submitted = st.form_submit_button("Zatwierdź i zapisz")

    if submitted:
        payload = {
            "session_id": st.session_state.session_id,
            "zatwierdzone": True,
            "korekta_pm": int(korekta) if korekta else None,
            "komentarz_pm": komentarz or None,
        }
        with st.spinner("Zapisuję..."):
            resp = httpx.post(f"{API_BASE}/approve", json=payload, timeout=30)
            if resp.status_code == 200:
                st.success("Wycena zapisana w pamięci agenta.")
                st.session_state.phase = "input"
                st.session_state.result = None
                st.rerun()
            else:
                st.error(f"Błąd zapisu: {resp.text}")
```

**Step 2: Uruchom manualnie (wymaga uruchomionego API)**

```bash
# Terminal 1: API
uvicorn gepa.api:app --reload

# Terminal 2: Streamlit
streamlit run gepa/app.py
```

Otwórz `http://localhost:8501` — sprawdź formularz, wycenę, zatwierdzenie.

**Step 3: Commit**

```bash
git add gepa/app.py
git commit -m "feat: Streamlit UI with estimate form and PM HITL review"
```

---

## Task 7: Migracja danych treningowych z ace-poc

**Files:**
- Create: `gepa/data/migrate_ace_poc.py`
- Create: `tests/test_migration.py`

**Step 1: Napisz failing test**

```python
# tests/test_migration.py
import json
import tempfile
from pathlib import Path


def test_migrate_converts_ace_poc_format():
    ace_example = {
        "project_spec": "Portal klientów dla banku",
        "actual_costs": {"total_md": 45, "breakdown": {"backend": 20, "frontend": 15, "testing": 10}},
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src"
        dst = Path(tmpdir) / "dst"
        src.mkdir()
        dst.mkdir()

        (src / "bank_portal.json").write_text(json.dumps(ace_example))

        from gepa.data.migrate_ace_poc import migrate
        migrate(str(src), str(dst))

        files = list(dst.glob("*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert "opis_projektu" in data
        assert "rzeczywiste_godziny" in data
        assert data["rzeczywiste_godziny"] == 45 * 8
```

**Step 2: Uruchom test — FAIL**

```bash
pytest tests/test_migration.py -v
```
Oczekiwane: FAIL

**Step 3: Utwórz `gepa/data/migrate_ace_poc.py`**

```python
import json
from pathlib import Path


def migrate(src_dir: str, dst_dir: str) -> int:
    src = Path(src_dir)
    dst = Path(dst_dir)
    dst.mkdir(parents=True, exist_ok=True)

    count = 0
    for f in src.glob("*.json"):
        raw = json.loads(f.read_text())
        md = raw.get("actual_costs", {}).get("total_md", 0)
        converted = {
            "opis_projektu": raw.get("project_spec", ""),
            "rzeczywiste_godziny": md * 8,
            "zrodlo": "ace-poc",
            "oryginalny_plik": f.name,
        }
        (dst / f.name).write_text(json.dumps(converted, ensure_ascii=False, indent=2))
        count += 1

    print(f"Zmigrowano {count} przykładów treningowych.")
    return count


if __name__ == "__main__":
    import sys
    migrate(sys.argv[1], sys.argv[2])
```

**Step 4: Uruchom test — PASS**

```bash
pytest tests/test_migration.py -v
```

**Step 5: Uruchom migrację na prawdziwych danych**

```bash
# Zakładając że ace-poc jest w ../ace-poc
python -m gepa.data.migrate_ace_poc ../ace-poc/data/training gepa/data/training
```

**Step 6: Commit**

```bash
git add gepa/data/ tests/test_migration.py
git commit -m "feat: migrate ace-poc training data to GEPA format"
```

---

## Task 8: Generator danych syntetycznych

**Files:**
- Create: `gepa/data/generate_synthetic.py`
- Create: `tests/test_generate_synthetic.py`

**Step 1: Napisz failing test**

```python
# tests/test_generate_synthetic.py
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_generate_creates_n_examples():
    mock_lm = MagicMock()
    mock_lm.return_value = [MagicMock(
        opis_projektu="Aplikacja mobilna iOS",
        rzeczywiste_godziny=320,
        typ_projektu="nowy",
        technologie='["Swift", "Firebase"]',
        uzasadnienie="Typowy projekt mobilny.",
    )]

    with patch("dspy.Predict", return_value=mock_lm), \
         tempfile.TemporaryDirectory() as tmpdir:

        from gepa.data.generate_synthetic import generate
        count = generate(n=3, output_dir=tmpdir, seed_file=None)
        assert count == 3
        files = list(Path(tmpdir).glob("*.json"))
        assert len(files) == 3
```

**Step 2: Uruchom test — FAIL**

```bash
pytest tests/test_generate_synthetic.py -v
```

**Step 3: Utwórz `gepa/data/generate_synthetic.py`**

```python
import dspy
import json
import uuid
from pathlib import Path
from gepa.config.settings import settings


class GenerujPrzykladWyceny(dspy.Signature):
    """Wygeneruj realistyczny przykład projektu IT do wyceny dla Orange Polska."""

    kontekst: str = dspy.InputField(desc="Typ projektu i technologie do użycia")

    opis_projektu: str = dspy.OutputField(desc="Realistyczny opis wymagań projektu IT")
    rzeczywiste_godziny: int = dspy.OutputField(desc="Rzeczywista liczba roboczogodzin (100–2000)")
    typ_projektu: str = dspy.OutputField(desc="nowy | legacy | migracja | ai")
    technologie: str = dspy.OutputField(desc="Lista technologii jako JSON array string")
    uzasadnienie: str = dspy.OutputField(desc="Krótkie uzasadnienie liczby godzin")


KONTEKSTY = [
    "nowy projekt webowy REST API Python",
    "migracja systemu legacy Java 8 do Java 17",
    "integracja z systemem SAP ERP",
    "projekt AI/ML pipeline na danych telco",
    "aplikacja mobilna React Native",
    "portal self-service dla klientów telco",
    "mikroserwisy na Kubernetes AWS",
    "system raportowania BI z Spark",
    "modernizacja bazy danych Oracle do PostgreSQL",
    "chatbot obsługa klienta LLM",
]


def generate(n: int, output_dir: str, seed_file: str | None = None) -> int:
    generator = dspy.Predict(GenerujPrzykladWyceny)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(n):
        kontekst = KONTEKSTY[i % len(KONTEKSTY)]
        result = generator(kontekst=kontekst)
        example = {
            "opis_projektu": result.opis_projektu,
            "rzeczywiste_godziny": result.rzeczywiste_godziny,
            "typ_projektu": result.typ_projektu,
            "technologie": result.technologie,
            "uzasadnienie": result.uzasadnienie,
            "zrodlo": "synthetic",
        }
        fname = out / f"synthetic_{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(example, ensure_ascii=False, indent=2))

    return n


if __name__ == "__main__":
    import sys
    lm = dspy.LM(model=settings.llm_model, api_key=settings.llm_api_key or None)
    dspy.configure(lm=lm)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    count = generate(n=n, output_dir="gepa/data/training")
    print(f"Wygenerowano {count} przykładów syntetycznych.")
```

**Step 4: Uruchom test — PASS**

```bash
pytest tests/test_generate_synthetic.py -v
```

**Step 5: Wygeneruj dane syntetyczne (gdy LLM skonfigurowany)**

```bash
cp .env.example .env
# Uzupełnij LLM_MODEL i LLM_API_KEY w .env
python -m gepa.data.generate_synthetic 50
```

**Step 6: Commit**

```bash
git add gepa/data/generate_synthetic.py tests/test_generate_synthetic.py
git commit -m "feat: synthetic training data generator with DSPy"
```

---

## Task 9: Zarządzanie trainsetem (przygotowanie do GEPA w Fazie 2)

**Files:**
- Create: `gepa/optimization/trainset.py`
- Create: `tests/optimization/test_trainset.py`

**Step 1: Napisz failing test**

```python
# tests/optimization/test_trainset.py
import json
import tempfile
from pathlib import Path


def test_load_trainset_returns_dspy_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        example = {
            "opis_projektu": "Portal webowy",
            "rzeczywiste_godziny": 200,
            "typ_projektu": "nowy",
        }
        (Path(tmpdir) / "ex1.json").write_text(json.dumps(example))

        from gepa.optimization.trainset import load_trainset
        examples = load_trainset(tmpdir)

        assert len(examples) == 1
        assert examples[0].rzeczywiste_godziny == 200
        assert examples[0].opis_projektu == "Portal webowy"


def test_trainset_count():
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(5):
            ex = {"opis_projektu": f"Projekt {i}", "rzeczywiste_godziny": 100 + i * 10}
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps(ex))

        from gepa.optimization.trainset import load_trainset, count_examples
        assert count_examples(tmpdir) == 5
```

**Step 2: Uruchom test — FAIL**

```bash
pytest tests/optimization/test_trainset.py -v
```

**Step 3: Utwórz `gepa/optimization/trainset.py`**

```python
import json
from pathlib import Path
import dspy


def load_trainset(training_dir: str) -> list[dspy.Example]:
    examples = []
    for f in Path(training_dir).glob("*.json"):
        data = json.loads(f.read_text())
        if "opis_projektu" not in data or "rzeczywiste_godziny" not in data:
            continue
        ex = dspy.Example(
            opis_projektu=data["opis_projektu"],
            historia_klienta=data.get("historia_klienta", "Brak historii."),
            wzorce_ryzyk=data.get("wzorce_ryzyk", "Brak wzorców."),
            rzeczywiste_godziny=data["rzeczywiste_godziny"],
        ).with_inputs("opis_projektu", "historia_klienta", "wzorce_ryzyk")
        examples.append(ex)
    return examples


def count_examples(training_dir: str) -> int:
    return len(list(Path(training_dir).glob("*.json")))
```

**Step 4: Uruchom test — PASS**

```bash
pytest tests/optimization/test_trainset.py -v
```

**Step 5: Commit**

```bash
git add gepa/optimization/trainset.py tests/optimization/test_trainset.py
git commit -m "feat: trainset loader for GEPA optimization (Faza 2 prep)"
```

---

## Task 10: End-to-end smoke test i uruchomienie

**Files:**
- Create: `tests/test_e2e_smoke.py`
- Create: `docker-compose.yml` (Neo4j dla Graphiti)

**Step 1: Utwórz `docker-compose.yml`**

```yaml
services:
  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

**Step 2: Napisz smoke test (bez prawdziwego LLM)**

```python
# tests/test_e2e_smoke.py
from unittest.mock import patch, MagicMock, AsyncMock


def test_full_pipeline_imports():
    """Sprawdź że wszystkie moduły importują się bez błędów."""
    from gepa.config.settings import settings
    from gepa.dspy_modules.signatures import WycenaIT
    from gepa.dspy_modules.estimator import create_estimator
    from gepa.memory.schemas import ProjektIT, Klient, WzorzecRyzyka
    from gepa.graph.state import EstimationState
    from gepa.optimization.trainset import load_trainset, count_examples
    assert True


def test_api_app_creates():
    with patch("gepa.graph.workflow.create_graph") as mock:
        mock.return_value = MagicMock()
        from gepa.api import app
        assert app is not None
```

**Step 3: Uruchom wszystkie testy**

```bash
pytest tests/ -v --tb=short
```
Oczekiwane: wszystkie PASS

**Step 4: Uruchom Neo4j i usługi**

```bash
docker compose up -d
cp .env.example .env
# Uzupełnij LLM_API_KEY w .env
uvicorn gepa.api:app --reload &
streamlit run gepa/app.py
```

**Step 5: Manualne end-to-end sprawdzenie**

- Otwórz `http://localhost:8501`
- Wprowadź klienta i opis projektu
- Sprawdź czy wycena się generuje
- Zatwierdź lub skoryguj
- Sprawdź logi API — czy `store_node` się uruchomił

**Step 6: Commit końcowy Fazy 1**

```bash
git add docker-compose.yml tests/test_e2e_smoke.py
git commit -m "feat: Faza 1 complete — working estimation agent with HITL and Graphiti memory"
```

---

## Podsumowanie Fazy 1

Po ukończeniu tej fazy masz:
- Działający agent wyceny z DSPy ChainOfThought
- LangGraph graf z HITL interrupt (PM zatwierdza wycenę)
- Graphiti przechowuje historię każdej wyceny
- Streamlit UI do interakcji z agentem
- FastAPI bridge między UI a LangGraph
- Dane treningowe z ace-poc + syntetyczne (50+ przykładów)
- Trainset loader gotowy na GEPA w Fazie 2

**Następny krok: Faza 2** — metryka GEPA, pierwszy cykl optymalizacji, MLflow tracking.
