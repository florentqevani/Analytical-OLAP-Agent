from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalyzeRequest, AnalyzeResponse, HistoryResponse
from data_access import HistoryStore, StarSchemaWarehouse
from planner import PlannerOrchestrator

app = FastAPI(title="Retail Analytics API", version="1.0.0")
load_dotenv()

allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

warehouse = StarSchemaWarehouse(
    os.getenv("WAREHOUSE_DB_PATH", "retail_warehouse.duckdb")
)
history_store = HistoryStore(os.getenv("HISTORY_DB_PATH", "agent_history.duckdb"))
orchestrator = PlannerOrchestrator(warehouse=warehouse, history_store=history_store)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/agents")
def list_agents() -> dict[str, list[dict[str, str]]]:
    return {"agents": orchestrator.list_agents()}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = orchestrator.run_agent(
            user_id=payload.user_id,
            agent_id=payload.agent_id,
            prompt=payload.prompt,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(error)) from error
    return AnalyzeResponse(**result)


@app.get("/history", response_model=HistoryResponse)
def history(
    user_id: str = Query(..., min_length=1, max_length=120),
    limit: int = Query(50, ge=1, le=200),
) -> HistoryResponse:
    try:
        items = orchestrator.history_for_user(user_id=user_id, limit=limit)
    except Exception as error:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(error)) from error
    return HistoryResponse(items=items)
