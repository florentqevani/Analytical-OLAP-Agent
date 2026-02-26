# Architecture

## Layers and Responsibilities

### `frontend/` (React + Vite)
- Calls API endpoints through `frontend/src/services/api.js`.
- Renders agent output assuming a stable result contract:
  - `result.message`
  - `result.report.{title, executiveSummary, keyFindings, risks, recommendations, chartHint, chartData}`
- Uses `VITE_API_URL` at build/runtime. If missing, calls are blocked with explicit errors.

### `api/` (FastAPI boundary)
- `api/main.py` defines transport concerns:
  - CORS configuration (`CORS_ORIGINS` or default allowlist)
  - startup DB health probes
  - HTTP -> orchestrator mapping
  - input validation and HTTP error mapping
- `api/schemas.py` defines external request/response contracts.

### `planner/` (application service)
- `PlannerOrchestrator` owns:
  - agent lookup and dispatch (`AGENT_REGISTRY`)
  - run persistence in history store
  - response envelope returned to API layer
- This layer is intentionally thin; no transport/UI dependencies.

### `agents/` (domain behavior)
- `AnalyticsAgent` is the runtime interface.
- `LangChainAnalyticsAgent`:
  - gathers warehouse aggregates
  - calls OpenAI model via LangChain
  - parses/normalizes JSON output
  - falls back to deterministic report when LLM call cannot run
- Agent specializations are declarative in `AGENT_REGISTRY`.

### `data_access/` (persistence adapters)
- `StarSchemaWarehouse`: query helpers over DuckDB star schema.
- `HistoryStore`: append/read agent runs in `agent_history` table.
- `build_star_schema.py` + `star_schema.sql`: one-time/recurring warehouse build pipeline from CSV.

## Request Lifecycle

1. UI sends `POST /analyze` with `user_id`, `agent_id`, `prompt`.
2. FastAPI validates payload (Pydantic).
3. Planner checks `agent_id` existence and invokes selected agent.
4. Agent loads aggregate slices from warehouse (`overview`, by region/category/period).
5. Agent returns normalized report JSON (LLM or fallback).
6. Planner persists full response in history DuckDB.
7. API returns response including `history_id`.

## Data Model Boundaries

- Warehouse DB and history DB are physically separate DuckDB files by default.
- Warehouse is read through a narrow query API (`overview`, `revenue_by_*`), not ad hoc SQL from agents.
- History stores prompt + full response JSON for replay in UI.

## Runtime Modes

### LLM-enabled mode
- Requires `OPENAI_API_KEY`.
- `OPENAI_MODEL` defaults to `gpt-4o-mini`.
- Higher quality narrative and recommendations.

### Fallback mode
- Triggered when API key is missing/blank or model output is unusable.
- Returns deterministic report with warehouse summary and chart data.
- Keeps API/UI functional for local smoke testing and demos.

## Deployment Model

### Docker Compose
- `api` service on container port `8000`, host default `8001`.
- `frontend` service on container/host default `5174`.
- Named volume `duckdb_data` persists both DuckDB files.

### Render Blueprint
- Python web service for API + static site for frontend.
- API entrypoint builds star schema if warehouse DB file is absent.
- Render environment wiring connects frontend origin to API CORS and API URL.

## Failure and Recovery Characteristics

- Unknown `agent_id` -> HTTP 400.
- Internal errors in run/history paths -> HTTP 500.
- Missing `VITE_API_URL` -> frontend request guard throws before network call.
- Missing warehouse DB in container runs -> auto-build from CSV at startup.
- History DB schema created automatically on `HistoryStore` initialization.