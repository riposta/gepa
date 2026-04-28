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
from gepa.dspy_modules.classifier import create_classifier, normalize_type, PROJECT_TYPES
from gepa.optimization.optimizer import OptimizerRunner

logger = logging.getLogger(__name__)

from gepa.config.settings import settings as _settings

TRAINING_DIR = os.environ.get("TRAINING_DIR", "gepa/data/training")
ESTIMATES_FILE = os.environ.get("ESTIMATES_FILE", "gepa/data/estimates_count.json")
GEPA_TRIGGER_EVERY = _settings.gepa_trigger_every


def _save_to_trainset(state: EstimationState, actual_hours: int) -> None:
    entry = {
        "project_description": state["project_description"],
        "actual_hours": actual_hours,
        "project_type": state.get("project_type", "new"),
        "client_history": state.get("client_history", ""),
        "risk_patterns": state.get("risk_patterns", ""),
        "pm_comment": state.get("pm_comment", ""),
        "source": "hitl",
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
            estimators = {typ: estimator for typ in PROJECT_TYPES}
        else:
            estimators = {typ: create_estimator() for typ in PROJECT_TYPES}

    async def intake_node(state: EstimationState) -> dict:
        if not state.get("session_id"):
            return {"session_id": str(uuid.uuid4())}
        return {}

    async def classify_node(state: EstimationState) -> dict:
        result = classifier(project_description=state["project_description"])
        return {"project_type": normalize_type(result.project_type)}

    async def context_node(state: EstimationState) -> dict:
        typ = state.get("project_type", "new")
        history = await graphiti.get_context(
            state["client"], state["project_description"], typ
        )
        patterns = await graphiti.get_risk_patterns(state["project_description"])
        return {"client_history": history, "risk_patterns": patterns}

    async def estimation_node(state: EstimationState) -> dict:
        typ = state.get("project_type", "new")
        est = estimators.get(typ) or estimators.get("new") or list(estimators.values())[0]
        result = est(
            project_description=state["project_description"],
            client_history=state["client_history"],
            risk_patterns=state["risk_patterns"],
        )
        return {
            "estimated_hours": result.estimated_hours,
            "reasoning": result.reasoning,
            "confidence": result.confidence,
        }

    async def store_node(state: EstimationState) -> dict:
        hours = state.get("pm_correction") or state["estimated_hours"]
        typ = state.get("project_type", "new")
        content = (
            f"Project: {state['project_description']}\n"
            f"Type: {typ}\n"
            f"Client: {state['client']}\n"
            f"Agent estimate: {state['estimated_hours']} hrs\n"
            f"Actual (PM): {hours} hrs\n"
            f"PM comment: {state.get('pm_comment', '')}"
        )
        await graphiti.add_episode(state["session_id"], content)

        if state.get("pm_correction"):
            _save_to_trainset(state, hours)

        count = _increment_estimate_count()
        if count % GEPA_TRIGGER_EVERY == 0:
            runner = OptimizerRunner()
            try:
                est = estimators.get("new") or list(estimators.values())[0]
                program_path = runner.run(student=est, training_dir=TRAINING_DIR)
                for typ, typ_est in estimators.items():
                    typ_est.load(str(program_path))
                logger.info("[GEPA] Reloaded optimized program: %s", program_path.name)
            except Exception:
                logger.exception("[GEPA] Optimization failed")

        return {"approved": True}

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
