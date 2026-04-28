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
