from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalyzeRequest, AnalyzeResponse, HistoryResponse
from data_access import HistoryStore, StarSchemaWarehouse
from planner import PlannerOrchestrator

app = FastAPI(title="Retail Analytics API", version="1.0.0")
load_dotenv()

logger = logging.getLogger(__name__)
default_allowed_origins = [
    "https://analytical-olap-agent-frontend.onrender.com",
    "https://superb-tiramisu-dcfab1.netlify.app",
    "http://localhost:5173",
    "http://localhost:3000",
]
cors_origins_raw = os.getenv("CORS_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()
] or default_allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

warehouse = StarSchemaWarehouse(
    os.getenv("WAREHOUSE_DB_PATH", "retail_warehouse.duckdb")
)
history_store = HistoryStore(os.getenv("HISTORY_DB_PATH", "agent_history.duckdb"))
orchestrator = PlannerOrchestrator(warehouse=warehouse, history_store=history_store)


@app.on_event("startup")
def startup_checks() -> None:
    try:
        overview = warehouse.overview()
        logger.info(
            "Warehouse DB check OK. path=%s transactions=%s",
            warehouse.db_path,
            overview.get("transactions"),
        )
    except Exception as error:  # pragma: no cover
        logger.exception(
            "Warehouse DB check failed. path=%s error=%s",
            warehouse.db_path,
            error,
        )

    try:
        history_store.list_for_user(user_id="startup_probe", limit=1)
        logger.info("History DB check OK. path=%s", history_store.db_path)
    except Exception as error:  # pragma: no cover
        logger.exception(
            "History DB check failed. path=%s error=%s",
            history_store.db_path,
            error,
        )


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
