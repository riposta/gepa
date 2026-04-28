import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from gepa.api_auth import verify_api_key
from pydantic import BaseModel
import dspy
from gepa.graph.workflow import create_graph
from gepa.config.settings import settings
from gepa.memory.graphiti_client import GraphitiClient
from gepa.optimization.optimizer import OptimizerRunner
from gepa.dspy_modules.estimator import create_estimator


_graph = None
_graphiti_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph, _graphiti_client
    lm = dspy.LM(
        model=settings.llm_model,
        api_base=settings.llm_api_base or None,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)
    from gepa.monitoring.langfuse_config import configure_langfuse
    langfuse_handler = configure_langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key.get_secret_value(),
    )
    if langfuse_handler:
        dspy.configure(callbacks=[langfuse_handler])
    _graphiti_client = GraphitiClient()
    _graph = create_graph(graphiti_client=_graphiti_client)
    yield
    await _graphiti_client.close()


app = FastAPI(title="GEPA Estimation API", lifespan=lifespan)


class EstimateRequest(BaseModel):
    client: str
    project_description: str


class ApproveRequest(BaseModel):
    session_id: str
    approved: bool
    pm_correction: int | None = None
    pm_comment: str | None = None


@app.post("/estimate", dependencies=[Depends(verify_api_key)])
async def estimate(req: EstimateRequest):
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "session_id": thread_id,
        "client": req.client,
        "project_description": req.project_description,
        "project_type": "",
        "client_history": "",
        "risk_patterns": "",
        "estimated_hours": None,
        "reasoning": None,
        "confidence": None,
        "pm_correction": None,
        "pm_comment": None,
        "approved": False,
    }
    result = await _graph.ainvoke(initial_state, config)
    return {
        "session_id": thread_id,
        "estimated_hours": result["estimated_hours"],
        "reasoning": result["reasoning"],
        "confidence": result["confidence"],
        "project_type": result.get("project_type", "new"),
    }


@app.post("/approve", dependencies=[Depends(verify_api_key)])
async def approve(req: ApproveRequest):
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    config = {"configurable": {"thread_id": req.session_id}}
    update = {
        "approved": req.approved,
        "pm_correction": req.pm_correction,
        "pm_comment": req.pm_comment,
    }
    await _graph.aupdate_state(config, update)
    await _graph.ainvoke(None, config)
    return {"status": "saved", "session_id": req.session_id}


@app.get("/model/info")
async def model_info():
    runner = OptimizerRunner()
    latest = runner.get_latest_program()
    return {
        "program_version": latest.stem if latest else "baseline",
        "program_path": str(latest) if latest else None,
    }


@app.post("/model/reload", dependencies=[Depends(verify_api_key)])
async def model_reload():
    global _graph, _graphiti_client
    runner = OptimizerRunner()
    latest = runner.get_latest_program()
    if latest is None:
        return {"status": "no_program", "message": "No optimized program available."}

    new_estimator = create_estimator()
    new_estimator.load(str(latest))
    _graph = create_graph(
        graphiti_client=_graphiti_client,
        estimator=new_estimator,
    )
    return {"status": "reloaded", "program": latest.stem}
