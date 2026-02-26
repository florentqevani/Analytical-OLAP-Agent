# Analytical OLAP Agent

Multi-agent retail analytics app with:
- `frontend`: React/Vite UI
- `api`: FastAPI HTTP layer
- `planner`: orchestration + agent dispatch
- `agents`: LangChain/OpenAI-backed analytics agents
- `data_access`: DuckDB warehouse + history store

The system can run with or without an OpenAI key. Without `OPENAI_API_KEY`, agents return deterministic fallback summaries from warehouse aggregates.

## Runtime Topology

1. Frontend calls API (`/agents`, `/analyze`, `/history`).
2. API validates request and routes to `PlannerOrchestrator`.
3. Orchestrator resolves `agent_id` from `AGENT_REGISTRY`, executes agent, stores run in history DB.
4. Agent reads warehouse aggregates from DuckDB and returns report JSON.
5. History API reads persisted runs for a `user_id`.

## Repository Map

```text
.
├─ api/                    # FastAPI app + request/response schemas
├─ agents/                 # Agent interface + LangChain implementation + registry
├─ planner/                # Run coordination and history writes
├─ data_access/            # DuckDB warehouse + history DB adapters + schema SQL
├─ frontend/               # React client
├─ scripts/check_api.py    # Basic API smoke check
├─ render.yaml             # Render Blueprint (API + static frontend)
└─ docker-compose.yml      # Local multi-service stack
```

## API Contract

Base URL:
- Docker Compose default: `http://localhost:8001`
- Direct Uvicorn default: `http://localhost:8000`

### `GET /health`
Response:
```json
{ "status": "ok" }
```

### `GET /agents`
Response:
```json
{
  "agents": [
    { "agent_id": "dimension_navigator", "label": "Dimension Navigator Agent" }
  ]
}
```

### `POST /analyze`
Request:
```json
{
  "user_id": "demo_user",
  "agent_id": "kpi_calculator",
  "prompt": "Analyze MoM and YoY revenue changes."
}
```

Response shape:
```json
{
  "history_id": "uuid",
  "agent_id": "kpi_calculator",
  "agent_label": "KPI Calculator Agent",
  "result": {
    "message": "string",
    "report": {
      "title": "string",
      "executiveSummary": "string",
      "keyFindings": ["string"],
      "risks": ["string"],
      "recommendations": ["string"],
      "chartHint": { "dimension": "string", "metric": "string" },
      "chartData": {
        "title": "string",
        "unit": "string",
        "series": [{ "label": "string", "value": 123.4 }]
      }
    }
  }
}
```

Validation limits:
- `user_id`: 1..120 chars
- `agent_id`: 1..80 chars
- `prompt`: 1..3000 chars

### `GET /history?user_id=<id>&limit=<n>`
- `limit` range: 1..200 (default 50)
- Returns most recent first.

## Environment Variables

| Variable | Required | Default | Used By | Notes |
|---|---|---|---|---|
| `OPENAI_API_KEY` | No | empty | API/agents | If missing, fallback mode is used. |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | API/agents | LLM model for LangChain agent calls. |
| `WAREHOUSE_DB_PATH` | No | `retail_warehouse.duckdb` | API/data_access | DuckDB file with star schema tables. |
| `HISTORY_DB_PATH` | No | `agent_history.duckdb` | API/data_access | DuckDB file for `agent_history`. |
| `CSV_PATH` | No | `global_retail_sales.csv` | API entrypoint | Used only when warehouse DB must be built at startup. |
| `CORS_ORIGINS` | No | built-in allowlist | API | Comma-separated origins. |
| `VITE_API_URL` | Yes (frontend) | none | Frontend | Required; frontend fails requests if unset. |
| `API_HOST_PORT` | No | `8001` | docker-compose | Host bind for API container port 8000. |
| `FRONTEND_HOST_PORT` | No | `5174` | docker-compose | Host bind for frontend container port 5174. |

## Local Development

### Option A: Docker Compose (recommended)

1. Create/update `.env` with at least:
```bash
OPENAI_API_KEY=...
```
2. Start services:
```bash
docker compose up --build
```
3. Validate:
- Frontend: `http://localhost:5174`
- API health: `http://localhost:8001/health`

Optional host-port override:
```bash
API_HOST_PORT=8000 FRONTEND_HOST_PORT=5173 docker compose up --build
```

### Option B: Run services directly

Backend:
```bash
pip install -r requirements.txt
python data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv
uvicorn api.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
# Required for frontend requests:
# set VITE_API_URL=http://localhost:8000   (Windows PowerShell: $env:VITE_API_URL="http://localhost:8000")
npm run dev
```

## Deployment (Render Blueprint)

`render.yaml` provisions:
- `analytical-olap-agent-api` (Python web service)
- `analytical-olap-agent-frontend` (static site)

Wiring:
- Frontend `VITE_API_URL` <- API `RENDER_EXTERNAL_URL`
- API `CORS_ORIGINS` <- Frontend `RENDER_EXTERNAL_URL`

Only secret you must set manually:
- `OPENAI_API_KEY` on the API service.

## Operational Notes

- API startup checks warehouse and history DB connectivity and logs results.
- In containerized runs, `api/entrypoint.sh` builds the warehouse DB automatically if `WAREHOUSE_DB_PATH` does not exist.
- History persistence is local DuckDB. In Docker Compose it is backed by `duckdb_data` volume.

## Smoke Test

After API is up:
```bash
python scripts/check_api.py --base-url http://127.0.0.1:8001
```

## Extending Agents

1. Register a new agent in `agents/__init__.py` (`AGENT_REGISTRY`).
2. Implement behavior by extending `AnalyticsAgent` or reusing `LangChainAnalyticsAgent`.
3. Keep output aligned with current report schema (`message` + `report` object), since frontend rendering assumes this contract.
