from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import dspy
from gepa.graph.workflow import create_graph
from gepa.config.settings import settings


_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph
    lm = dspy.LM(
        model=settings.llm_model,
        api_base=settings.llm_api_base or None,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)
    _graph = create_graph()
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
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
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
    result = await _graph.ainvoke(initial_state, config)
    return {
        "session_id": result["session_id"],
        "szacunek_godzin": result["szacunek_godzin"],
        "uzasadnienie": result["uzasadnienie"],
        "pewnosc": result["pewnosc"],
    }


@app.post("/approve")
async def approve(req: ApproveRequest):
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    config = {"configurable": {"thread_id": req.session_id}}
    update = {
        "zatwierdzone": req.zatwierdzone,
        "korekta_pm": req.korekta_pm,
        "komentarz_pm": req.komentarz_pm,
    }
    await _graph.aupdate_state(config, update)
    await _graph.ainvoke(None, config)
    return {"status": "saved", "session_id": req.session_id}
