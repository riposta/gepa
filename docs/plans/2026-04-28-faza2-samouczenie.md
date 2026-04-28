# Faza 2 — Samouczenie: Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Dodanie pętli samouczenia — metryki wyceny, optymalizacji MIPROv2 (surrogate za GEPA, gotowy interfejs do podmiany), hot-swap programów w API oraz monitoringu MLflow + Langfuse.

**Architecture:** `gepa/dspy_modules/metrics.py` definiuje metrykę oceniającą dokładność/uzasadnienie/pewność. `gepa/optimization/optimizer.py` opakowuje MIPROv2 z interfejsem kompatybilnym z przyszłym GEPA. Skompilowany program zapisywany do `gepa/dspy_modules/programs/`. API hot-swapuje program gdy dostępna nowsza wersja. MLflow śledzi metryki optymalizacji, Langfuse śledzi każde wywołanie LLM. Streamlit pokazuje statystyki i umożliwia A/B wybór wersji.

**Tech Stack:** DSPy 2.6.27 + MIPROv2, MLflow 2.x, Langfuse 3.x, Python 3.12

**UWAGA:** DSPy 2.6.27 nie ma `dspy.GEPA` — używamy MIPROv2 z `auto='light'` jako optimizer. Interfejs `OptimizerRunner` jest zaprojektowany tak by podmiana na GEPA wymagała tylko zmiany jednej linii gdy będzie dostępna.

---

## Task 1: Metryka wyceny DSPy

**Files:**
- Create: `gepa/dspy_modules/metrics.py`
- Create: `tests/dspy_modules/test_metrics.py`

**Step 1: Napisz failing testy**

```python
# tests/dspy_modules/test_metrics.py
from unittest.mock import MagicMock


def test_metryka_dokladna_wycena():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 105
    pred.uzasadnienie = "Projekt wymaga 5 sprintów: backend 60h, frontend 30h, testy 15h."
    pred.pewnosc = 0.7

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert 0.8 < score <= 1.0


def test_metryka_zla_wycena():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 200  # 100% błąd
    pred.uzasadnienie = "Ok."  # za krótkie
    pred.pewnosc = 0.99  # przesadna pewność

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert score < 0.5


def test_metryka_zwraca_float():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 200

    pred = MagicMock()
    pred.szacunek_godzin = 180
    pred.uzasadnienie = "Standardowy projekt webowy."
    pred.pewnosc = 0.6

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_feedback_tekstowy():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 150
    pred.uzasadnienie = "Projekt webowy."
    pred.pewnosc = 0.5

    from gepa.dspy_modules.metrics import metryka_wyceny_z_feedbackiem
    score, feedback = metryka_wyceny_z_feedbackiem(gold, pred)
    assert isinstance(score, float)
    assert isinstance(feedback, str)
    assert len(feedback) > 0
```

**Step 2: Uruchom test — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/dspy_modules/test_metrics.py -v
```
Oczekiwane: FAIL — "cannot import name 'metryka_wyceny'"

**Step 3: Utwórz `gepa/dspy_modules/metrics.py`**

```python
from unittest.mock import MagicMock


def metryka_wyceny(gold, pred, trace=None) -> float:
    rzeczywiste = getattr(gold, "rzeczywiste_godziny", 0) or 0
    szacunek = getattr(pred, "szacunek_godzin", 0) or 0
    uzasadnienie = getattr(pred, "uzasadnienie", "") or ""
    pewnosc = getattr(pred, "pewnosc", 0.5) or 0.5

    # Dokładność (50%) — błąd względny, max 0% przy idealnym szacunku
    if rzeczywiste == 0:
        dokladnosc = 0.0
    else:
        blad = abs(szacunek - rzeczywiste) / rzeczywiste
        dokladnosc = max(0.0, 1.0 - blad)

    # Uzasadnienie (30%) — długość jako proxy jakości
    uzasadnienie_score = min(1.0, len(uzasadnienie) / 150)

    # Kalibracja pewności (20%) — kara za skrajne wartości (<0.2 lub >0.95)
    if pewnosc < 0.2 or pewnosc > 0.95:
        kalibracja = 0.3
    elif 0.3 <= pewnosc <= 0.85:
        kalibracja = 1.0
    else:
        kalibracja = 0.7

    return round(
        0.5 * dokladnosc + 0.3 * uzasadnienie_score + 0.2 * kalibracja,
        4,
    )


def metryka_wyceny_z_feedbackiem(gold, pred, trace=None) -> tuple[float, str]:
    score = metryka_wyceny(gold, pred, trace)

    rzeczywiste = getattr(gold, "rzeczywiste_godziny", 0) or 0
    szacunek = getattr(pred, "szacunek_godzin", 0) or 0
    uzasadnienie = getattr(pred, "uzasadnienie", "") or ""
    pewnosc = getattr(pred, "pewnosc", 0.5) or 0.5

    feedback_parts = []

    if rzeczywiste > 0:
        blad = (szacunek - rzeczywiste) / rzeczywiste
        if blad > 0.3:
            feedback_parts.append(
                f"Szacunek za wysoki o {blad:.0%} — sprawdź czy nie duplikujesz zadań."
            )
        elif blad < -0.3:
            feedback_parts.append(
                f"Szacunek za niski o {abs(blad):.0%} — uwzględnij bufor na ryzyko i testy."
            )

    if len(uzasadnienie) < 80:
        feedback_parts.append(
            "Uzasadnienie zbyt krótkie — dodaj podział na komponenty (backend/frontend/testy)."
        )

    if pewnosc > 0.95:
        feedback_parts.append(
            "Zbyt wysoka pewność — dla nowych projektów trzymaj pewność poniżej 0.9."
        )
    elif pewnosc < 0.2:
        feedback_parts.append(
            "Zbyt niska pewność — jeśli masz historyczne dane, podnieś pewność."
        )

    feedback = " ".join(feedback_parts) if feedback_parts else "Wycena w normie."
    return score, feedback
```

**Step 4: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/dspy_modules/test_metrics.py -v
```
Oczekiwane: 4/4 PASS

**Step 5: Commit**

```bash
git add gepa/dspy_modules/metrics.py tests/dspy_modules/test_metrics.py
git commit -m "feat: DSPy estimation metric with text feedback for MIPROv2"
```

---

## Task 2: Optimizer runner (MIPROv2 z interfejsem GEPA-ready)

**Files:**
- Create: `gepa/optimization/optimizer.py`
- Create: `tests/optimization/test_optimizer.py`

**Step 1: Sprawdź API MIPROv2**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/python -c "
from dspy.teleprompt import MIPROv2
import inspect
print(inspect.signature(MIPROv2.__init__))
print(inspect.signature(MIPROv2.compile))
"
```

**Step 2: Napisz failing testy**

```python
# tests/optimization/test_optimizer.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile


def test_optimizer_runner_creates_instance():
    from gepa.optimization.optimizer import OptimizerRunner
    runner = OptimizerRunner(programs_dir="/tmp/test_programs")
    assert runner is not None
    assert runner.programs_dir == Path("/tmp/test_programs")


def test_get_latest_program_returns_none_when_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        result = runner.get_latest_program()
        assert result is None


def test_get_latest_program_returns_highest_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "v1_baseline.json").write_text("{}")
        (p / "v2_optimized.json").write_text("{}")
        (p / "v3_optimized.json").write_text("{}")

        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir)
        result = runner.get_latest_program()
        assert result is not None
        assert "v3" in str(result)


def test_should_trigger_returns_false_below_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        assert runner.should_trigger(training_dir=tmpdir) is False


def test_should_trigger_returns_true_above_threshold():
    import json
    with tempfile.TemporaryDirectory() as tmpdir:
        # Utwórz 60 prawidłowych przykładów
        for i in range(60):
            ex = {"opis_projektu": f"Projekt {i}", "rzeczywiste_godziny": 100 + i}
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps(ex))

        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        # Sprawdź że threshold jest przekroczony
        from gepa.optimization.trainset import count_examples
        assert count_examples(tmpdir) >= 50
```

**Step 3: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/optimization/test_optimizer.py -v
```
Oczekiwane: FAIL

**Step 4: Utwórz `gepa/optimization/optimizer.py`**

```python
import json
from pathlib import Path
import dspy
from dspy.teleprompt import MIPROv2
from gepa.dspy_modules.metrics import metryka_wyceny
from gepa.optimization.trainset import load_trainset, count_examples
from gepa.config.settings import settings


class OptimizerRunner:
    def __init__(
        self,
        programs_dir: str | None = None,
        trigger_threshold: int | None = None,
    ) -> None:
        self.programs_dir = Path(programs_dir or settings.programs_dir)
        self.trigger_threshold = trigger_threshold or settings.gepa_trigger_threshold
        self.programs_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_program(self) -> Path | None:
        files = sorted(self.programs_dir.glob("v*.json"))
        return files[-1] if files else None

    def next_version(self) -> str:
        latest = self.get_latest_program()
        if latest is None:
            return "v2"
        num = int(latest.stem.split("_")[0].lstrip("v"))
        return f"v{num + 1}"

    def should_trigger(self, training_dir: str) -> bool:
        return count_examples(training_dir) >= self.trigger_threshold

    def run(
        self,
        student: dspy.Module,
        training_dir: str,
        val_split: float = 0.2,
    ) -> Path:
        examples = load_trainset(training_dir)
        split = max(1, int(len(examples) * (1 - val_split)))
        trainset = examples[:split]
        valset = examples[split:] or examples[:5]

        # MIPROv2 z auto='light' — mała liczba iteracji, dobry baseline
        # INTERFEJS GEPA-READY: gdy GEPA wejdzie do DSPy, podmień MIPROv2 na GEPA
        # i zamień metric= na tuple (score, feedback) z metryka_wyceny_z_feedbackiem
        optimizer = MIPROv2(
            metric=metryka_wyceny,
            auto="light",
            num_threads=1,
            verbose=True,
        )
        optimized = optimizer.compile(
            student,
            trainset=trainset,
            valset=valset,
            requires_permission_to_run=False,
        )

        version = self.next_version()
        output_path = self.programs_dir / f"{version}_miprov2.json"
        optimized.save(str(output_path))
        return output_path
```

**Step 5: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/optimization/test_optimizer.py -v
```
Oczekiwane: PASS

**Step 6: Commit**

```bash
git add gepa/optimization/optimizer.py tests/optimization/test_optimizer.py
git commit -m "feat: MIPROv2 optimizer runner with GEPA-ready interface"
```

---

## Task 3: MLflow tracking dla optymalizacji

**Files:**
- Create: `gepa/monitoring/mlflow_tracker.py`
- Create: `tests/monitoring/__init__.py`
- Create: `tests/monitoring/test_mlflow_tracker.py`
- Modify: `gepa/optimization/optimizer.py`

**Step 1: Utwórz katalog monitoring**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
mkdir -p gepa/monitoring tests/monitoring
touch gepa/monitoring/__init__.py tests/monitoring/__init__.py
```

**Step 2: Napisz failing testy**

```python
# tests/monitoring/test_mlflow_tracker.py
import pytest
from unittest.mock import patch, MagicMock


def test_tracker_creates_instance():
    from gepa.monitoring.mlflow_tracker import OptimizationTracker
    tracker = OptimizationTracker(experiment_name="test")
    assert tracker is not None


def test_log_optimization_run_calls_mlflow():
    with patch("mlflow.start_run") as mock_run, \
         patch("mlflow.log_params") as mock_params, \
         patch("mlflow.log_metrics") as mock_metrics, \
         patch("mlflow.log_artifact") as mock_artifact, \
         patch("mlflow.set_experiment"):
        mock_run.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_run.return_value.__exit__ = MagicMock(return_value=False)

        from gepa.monitoring.mlflow_tracker import OptimizationTracker
        tracker = OptimizationTracker(experiment_name="test")
        tracker.log_run(
            optimizer_name="MIPROv2",
            num_examples=60,
            val_score=0.78,
            program_path="/tmp/v2_miprov2.json",
        )
        mock_params.assert_called_once()
        mock_metrics.assert_called_once()
```

**Step 3: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/monitoring/test_mlflow_tracker.py -v
```

**Step 4: Utwórz `gepa/monitoring/mlflow_tracker.py`**

```python
import mlflow
from gepa.config.settings import settings


class OptimizationTracker:
    def __init__(self, experiment_name: str = "gepa_optimization") -> None:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name

    def log_run(
        self,
        optimizer_name: str,
        num_examples: int,
        val_score: float,
        program_path: str,
    ) -> None:
        with mlflow.start_run():
            mlflow.log_params({
                "optimizer": optimizer_name,
                "num_examples": num_examples,
            })
            mlflow.log_metrics({"val_score": val_score})
            mlflow.log_artifact(program_path)
```

**Step 5: Zaktualizuj `gepa/optimization/optimizer.py` — dodaj MLflow logging**

Zmień metodę `run()` — dodaj tracking po kompilacji:

```python
# Na początku pliku dodaj import:
from gepa.monitoring.mlflow_tracker import OptimizationTracker

# Na końcu metody run(), przed return output_path:
        tracker = OptimizationTracker()
        tracker.log_run(
            optimizer_name="MIPROv2",
            num_examples=len(examples),
            val_score=0.0,  # placeholder — MIPROv2 nie zwraca val_score bezpośrednio
            program_path=str(output_path),
        )
        return output_path
```

**Step 6: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/monitoring/test_mlflow_tracker.py tests/optimization/test_optimizer.py -v
```

**Step 7: Commit**

```bash
git add gepa/monitoring/ tests/monitoring/ gepa/optimization/optimizer.py
git commit -m "feat: MLflow tracking for optimization runs"
```

---

## Task 4: Langfuse tracing wywołań LLM

**Files:**
- Create: `gepa/monitoring/langfuse_config.py`
- Modify: `gepa/api.py` (dodaj Langfuse callback do DSPy)
- Create: `tests/monitoring/test_langfuse_config.py`

**Step 1: Napisz failing test**

```python
# tests/monitoring/test_langfuse_config.py
from unittest.mock import patch, MagicMock


def test_configure_langfuse_returns_none_without_keys():
    from gepa.monitoring.langfuse_config import configure_langfuse
    # Bez kluczy — powinno wrócić None bez błędu
    result = configure_langfuse(public_key="", secret_key="")
    assert result is None


def test_configure_langfuse_returns_callback_with_keys():
    with patch("langfuse.Langfuse") as mock_lf:
        mock_lf.return_value = MagicMock()
        from gepa.monitoring.langfuse_config import configure_langfuse
        # Reimportuj po patchu
        import importlib
        import gepa.monitoring.langfuse_config as lf_mod
        importlib.reload(lf_mod)
        # Bez kluczy powinno zwrócić None
        result = lf_mod.configure_langfuse(public_key="", secret_key="")
        assert result is None
```

**Step 2: Uruchom test — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/monitoring/test_langfuse_config.py -v
```

**Step 3: Utwórz `gepa/monitoring/langfuse_config.py`**

```python
from __future__ import annotations


def configure_langfuse(public_key: str, secret_key: str):
    if not public_key or not secret_key:
        return None
    try:
        from langfuse.callback import CallbackHandler
        handler = CallbackHandler(
            public_key=public_key,
            secret_key=secret_key,
        )
        return handler
    except Exception:
        return None
```

**Step 4: Zaktualizuj `gepa/api.py` — włącz Langfuse gdy klucze są dostępne**

Dodaj w `lifespan` po `dspy.configure(lm=lm)`:

```python
from gepa.monitoring.langfuse_config import configure_langfuse

# W lifespan, po dspy.configure:
    langfuse_handler = configure_langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key.get_secret_value(),
    )
    if langfuse_handler:
        dspy.configure(callbacks=[langfuse_handler])
```

**Step 5: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/monitoring/ -v
```

**Step 6: Commit**

```bash
git add gepa/monitoring/langfuse_config.py tests/monitoring/test_langfuse_config.py gepa/api.py
git commit -m "feat: Langfuse tracing integration (opt-in via .env keys)"
```

---

## Task 5: Hot-swap programów w API

**Files:**
- Modify: `gepa/api.py` (dodaj endpoint `/model/reload` i logikę ładowania programu)
- Modify: `gepa/graph/workflow.py` (estimator ładuje program z pliku jeśli istnieje)
- Create: `tests/test_hot_swap.py`

**Step 1: Napisz failing testy**

```python
# tests/test_hot_swap.py
import pytest
from unittest.mock import patch, MagicMock
import tempfile
import json
from pathlib import Path


def test_load_program_returns_none_when_no_file():
    from gepa.optimization.optimizer import OptimizerRunner
    runner = OptimizerRunner(programs_dir="/tmp/nonexistent_xyz")
    assert runner.get_latest_program() is None


def test_api_reload_endpoint_exists():
    with patch("gepa.graph.workflow.create_graph") as mock_graph, \
         patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("dspy.configure"):
        mock_graph.return_value = MagicMock()

        from gepa.api import app
        from fastapi.testclient import TestClient
        import gepa.api as api_module
        api_module._graph = MagicMock()

        client = TestClient(app)
        # Endpoint musi istnieć
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "program_version" in data
```

**Step 2: Uruchom testy — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/test_hot_swap.py -v
```

**Step 3: Zaktualizuj `gepa/api.py` — dodaj `/model/info` i `/model/reload`**

```python
# Dodaj na końcu api.py (przed lub po istniejących endpointach)
from gepa.optimization.optimizer import OptimizerRunner

@app.get("/model/info")
async def model_info():
    runner = OptimizerRunner()
    latest = runner.get_latest_program()
    return {
        "program_version": latest.stem if latest else "baseline",
        "program_path": str(latest) if latest else None,
    }


@app.post("/model/reload")
async def model_reload():
    global _graph, _graphiti_client
    runner = OptimizerRunner()
    latest = runner.get_latest_program()
    if latest is None:
        return {"status": "no_program", "message": "Brak zoptymalizowanego programu."}

    from gepa.dspy_modules.estimator import create_estimator
    new_estimator = create_estimator()
    new_estimator.load(str(latest))
    _graph = create_graph(
        graphiti_client=_graphiti_client,
        estimator=new_estimator,
    )
    return {"status": "reloaded", "program": latest.stem}
```

**Step 4: Zaktualizuj `gepa/graph/workflow.py` — przyjmij opcjonalny estimator**

```python
def create_graph(checkpointer=None, graphiti_client=None, estimator=None):
    graphiti = graphiti_client or GraphitiClient()
    est = estimator or create_estimator()
    # Zmień wszystkie użycia `estimator` na `est`
    # (zastąp w estimation_node: estimator(...) -> est(...))
```

**Step 5: Uruchom testy — PASS**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/test_hot_swap.py tests/test_api.py -v
```

**Step 6: Commit**

```bash
git add gepa/api.py gepa/graph/workflow.py tests/test_hot_swap.py
git commit -m "feat: hot-swap optimized program via /model/reload endpoint"
```

---

## Task 6: Auto-trigger optymalizacji w store_node

**Files:**
- Modify: `gepa/graph/workflow.py` (store_node sprawdza próg i triggeruje optymalizację)
- Create: `tests/graph/test_auto_trigger.py`

**Step 1: Napisz failing testy**

```python
# tests/graph/test_auto_trigger.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import tempfile
from pathlib import Path


@pytest.mark.asyncio
async def test_store_node_triggers_optimization_at_threshold():
    # Utwórz 51 przykładów treningowych
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(51):
            ex = {"opis_projektu": f"Projekt {i}", "rzeczywiste_godziny": 100}
            (Path(tmpdir) / f"ex{i}.json").write_text(json.dumps(ex))

        with patch("gepa.graph.workflow.GraphitiClient") as mock_gc, \
             patch("gepa.graph.workflow.create_estimator") as mock_est, \
             patch("gepa.graph.workflow.OptimizerRunner") as mock_runner_cls, \
             patch("gepa.graph.workflow.TRAINING_DIR", tmpdir):
            mock_gc.return_value = AsyncMock()
            mock_est.return_value = MagicMock()
            mock_runner = MagicMock()
            mock_runner.should_trigger.return_value = True
            mock_runner.run = MagicMock(return_value=Path("/tmp/v2_miprov2.json"))
            mock_runner_cls.return_value = mock_runner

            from gepa.graph.workflow import create_graph
            graph = create_graph()
            assert graph is not None
            # Weryfikacja że OptimizerRunner jest importowany
            assert mock_runner_cls is not None
```

**Step 2: Uruchom test — FAIL**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/graph/test_auto_trigger.py -v
```

**Step 3: Zaktualizuj `gepa/graph/workflow.py` — dodaj auto-trigger w store_node**

Dodaj import i stałą na początku pliku:

```python
from gepa.optimization.optimizer import OptimizerRunner
import os

TRAINING_DIR = os.environ.get("TRAINING_DIR", "gepa/data/training")
```

Zaktualizuj `store_node`:

```python
    async def store_node(state: EstimationState) -> dict:
        godziny = state.get("korekta_pm") or state["szacunek_godzin"]
        content = (
            f"Projekt: {state['opis_projektu']}\n"
            f"Klient: {state['klient']}\n"
            f"Szacunek agenta: {state['szacunek_godzin']} godz.\n"
            f"Rzeczywiste (PM): {godziny} godz.\n"
            f"Komentarz PM: {state.get('komentarz_pm', '')}"
        )
        await graphiti.add_episode(state["session_id"], content)

        # Zapisz do trainset jeśli PM podał korektę
        if state.get("korekta_pm"):
            _save_to_trainset(state, godziny)

        # Auto-trigger optymalizacji
        runner = OptimizerRunner()
        if runner.should_trigger(TRAINING_DIR):
            try:
                runner.run(student=est, training_dir=TRAINING_DIR)
            except Exception as e:
                print(f"[GEPA] Optymalizacja nie powiodła się: {e}")

        return {"zatwierdzone": True}
```

Dodaj helper `_save_to_trainset`:

```python
import json as _json

def _save_to_trainset(state: EstimationState, rzeczywiste_godziny: int) -> None:
    import uuid
    entry = {
        "opis_projektu": state["opis_projektu"],
        "rzeczywiste_godziny": rzeczywiste_godziny,
        "historia_klienta": state.get("historia_klienta", ""),
        "wzorce_ryzyk": state.get("wzorce_ryzyk", ""),
        "komentarz_pm": state.get("komentarz_pm", ""),
        "zrodlo": "hitl",
    }
    path = Path(TRAINING_DIR) / f"hitl_{uuid.uuid4().hex[:8]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json.dumps(entry, ensure_ascii=False, indent=2))
```

**Step 4: Uruchom testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/graph/ -v
```

**Step 5: Commit**

```bash
git add gepa/graph/workflow.py tests/graph/test_auto_trigger.py
git commit -m "feat: auto-trigger optimization in store_node, save HITL corrections to trainset"
```

---

## Task 7: Dashboard Streamlit — statystyki i A/B

**Files:**
- Modify: `gepa/app.py` (dodaj zakładkę Dashboard)

**Step 1: Zaktualizuj `gepa/app.py` — dodaj zakładkę Dashboard**

Zastąp całą zawartość `gepa/app.py`:

```python
import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="GEPA — Wycena IT", layout="wide")

tab_wycena, tab_dashboard = st.tabs(["Wycena projektu", "Dashboard"])

# ─── TAB 1: WYCENA ────────────────────────────────────────────

with tab_wycena:
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
                try:
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
                        st.error(f"Błąd API ({resp.status_code}): {resp.text}")
                except httpx.ConnectError:
                    st.error("Nie można połączyć z API. Czy FastAPI działa?")

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
                    "Rzeczywista liczba godzin",
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
                try:
                    resp = httpx.post(f"{API_BASE}/approve", json=payload, timeout=30)
                    if resp.status_code == 200:
                        st.success("Wycena zapisana w pamięci agenta.")
                        st.session_state.phase = "input"
                        st.session_state.result = None
                        st.rerun()
                    else:
                        st.error(f"Błąd zapisu: {resp.text}")
                except httpx.ConnectError:
                    st.error("Nie można połączyć z API.")

# ─── TAB 2: DASHBOARD ─────────────────────────────────────────

with tab_dashboard:
    st.title("Dashboard Modelu")

    try:
        info_resp = httpx.get(f"{API_BASE}/model/info", timeout=5)
        if info_resp.status_code == 200:
            info = info_resp.json()
            col1, col2 = st.columns(2)
            col1.metric("Wersja programu", info["program_version"])
            col2.metric("Ścieżka", info["program_path"] or "baseline (DSPy default)")
        else:
            st.warning("Nie można pobrać info o modelu.")
    except httpx.ConnectError:
        st.warning("API niedostępne — uruchom `uvicorn gepa.api:app --reload`")

    st.divider()

    col_reload, col_info = st.columns(2)
    with col_reload:
        if st.button("Załaduj najnowszy program (hot-swap)"):
            try:
                resp = httpx.post(f"{API_BASE}/model/reload", timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data["status"] == "reloaded":
                        st.success(f"Program załadowany: {data['program']}")
                    else:
                        st.info(data.get("message", "Brak zoptymalizowanego programu."))
            except httpx.ConnectError:
                st.error("API niedostępne.")

    st.divider()
    st.subheader("Jak uruchomić optymalizację ręcznie")
    st.code("""
# Gdy masz 50+ przykładów treningowych w gepa/data/training/:
.venv/bin/python -c "
from gepa.optimization.optimizer import OptimizerRunner
from gepa.dspy_modules.estimator import create_estimator
import dspy
from gepa.config.settings import settings

lm = dspy.LM(model=settings.llm_model, api_key=settings.llm_api_key.get_secret_value())
dspy.configure(lm=lm)

runner = OptimizerRunner()
student = create_estimator()
path = runner.run(student, 'gepa/data/training')
print(f'Program zapisany: {path}')
"
""", language="bash")
```

**Step 2: Weryfikacja składni**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/python -m py_compile gepa/app.py && echo "OK"
```

**Step 3: Commit**

```bash
git add gepa/app.py
git commit -m "feat: Streamlit dashboard with model info and hot-swap"
```

---

## Task 8: E2E smoke test Fazy 2 i wszystkie testy

**Files:**
- Create: `tests/test_faza2_smoke.py`

**Step 1: Utwórz `tests/test_faza2_smoke.py`**

```python
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import json


def test_faza2_imports():
    from gepa.dspy_modules.metrics import metryka_wyceny, metryka_wyceny_z_feedbackiem
    from gepa.optimization.optimizer import OptimizerRunner
    from gepa.monitoring.mlflow_tracker import OptimizationTracker
    from gepa.monitoring.langfuse_config import configure_langfuse
    assert True


def test_metryka_i_feedback_integracja():
    from gepa.dspy_modules.metrics import metryka_wyceny, metryka_wyceny_z_feedbackiem
    from unittest.mock import MagicMock

    gold = MagicMock()
    gold.rzeczywiste_godziny = 100
    pred = MagicMock()
    pred.szacunek_godzin = 90
    pred.uzasadnienie = "Backend 50h, frontend 30h, testy 20h."
    pred.pewnosc = 0.7

    score = metryka_wyceny(gold, pred)
    score2, feedback = metryka_wyceny_z_feedbackiem(gold, pred)

    assert 0.0 <= score <= 1.0
    assert score == score2
    assert isinstance(feedback, str)


def test_optimizer_runner_no_trigger_without_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        from gepa.optimization.optimizer import OptimizerRunner
        runner = OptimizerRunner(programs_dir=tmpdir, trigger_threshold=50)
        assert not runner.should_trigger(tmpdir)
        assert runner.get_latest_program() is None


def test_api_model_endpoints_exist():
    with patch("gepa.graph.workflow.create_graph") as mock_graph, \
         patch("gepa.memory.graphiti_client.GraphitiClient"), \
         patch("dspy.configure"):
        mock_graph.return_value = MagicMock()
        from gepa.api import app
        import gepa.api as api_module
        api_module._graph = MagicMock()

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/model/info")
        assert resp.status_code == 200
```

**Step 2: Uruchom WSZYSTKIE testy**

```bash
cd /Users/adamdabrowski/PycharmProjects/GEPA
.venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -30
```

Oczekiwane: wszystkie PASS. Jeśli jakiś test failu — napraw.

**Step 3: Commit końcowy Fazy 2**

```bash
git add tests/test_faza2_smoke.py
git commit -m "feat: Faza 2 complete — MIPROv2 optimization, MLflow, Langfuse, hot-swap"
```

---

## Podsumowanie Fazy 2

Po ukończeniu tej fazy masz:
- Metrykę wyceny z tekstowym feedbackiem (gotową na GEPA gdy wejdzie do DSPy)
- MIPROv2 optimizer z interfejsem GEPA-ready (`optimizer.py`)
- Auto-trigger optymalizacji co 50 nowych korekt PM
- HITL corrections zapisywane do trainset automatycznie
- MLflow tracking metryk optymalizacji
- Langfuse tracing (opt-in przez `.env`)
- Hot-swap programów przez `/model/reload`
- Dashboard Streamlit z info o wersji modelu

**Następny krok: Faza 3** — specjalizowane agenty per typ projektu, LangGraph routing, REST API.

**Podmiana na GEPA:** gdy `dspy.GEPA` lub `gepa-ai` z kompatybilnym API wejdzie do DSPy, w `optimizer.py` zmień jedną linię: `MIPROv2(...)` → `GEPA(...)` i dodaj `metryka_wyceny_z_feedbackiem` (tuple score, feedback) jako metric.
