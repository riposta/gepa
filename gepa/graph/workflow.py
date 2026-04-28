import uuid
import dspy
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from gepa.graph.state import EstimationState
from gepa.memory.graphiti_client import GraphitiClient
from gepa.dspy_modules.estimator import create_estimator


def create_graph(checkpointer=None, graphiti_client=None, estimator=None):
    graphiti = graphiti_client or GraphitiClient()
    est = estimator or create_estimator()

    async def intake_node(state: EstimationState) -> dict:
        if not state.get("session_id"):
            return {"session_id": str(uuid.uuid4())}
        return {}

    async def context_node(state: EstimationState) -> dict:
        historia = await graphiti.get_context(
            state["klient"], state["opis_projektu"]
        )
        wzorce = await graphiti.get_risk_patterns(state["opis_projektu"])
        return {"historia_klienta": historia, "wzorce_ryzyk": wzorce}

    async def estimation_node(state: EstimationState) -> dict:
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
        content = (
            f"Projekt: {state['opis_projektu']}\n"
            f"Klient: {state['klient']}\n"
            f"Szacunek agenta: {state['szacunek_godzin']} godz.\n"
            f"Rzeczywiste (PM): {godziny} godz.\n"
            f"Komentarz PM: {state.get('komentarz_pm', '')}"
        )
        await graphiti.add_episode(state["session_id"], content)
        return {"zatwierdzone": True}

    builder = StateGraph(EstimationState)
    builder.add_node("intake", intake_node)
    builder.add_node("context", context_node)
    builder.add_node("estimation", estimation_node)
    builder.add_node("store", store_node)

    builder.set_entry_point("intake")
    builder.add_edge("intake", "context")
    builder.add_edge("context", "estimation")
    builder.add_edge("estimation", "store")
    builder.add_edge("store", END)

    cp = checkpointer or MemorySaver()
    return builder.compile(checkpointer=cp, interrupt_before=["store"])
