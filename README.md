# Multi-Agent OLAP Analytics for Retail Decision Support

This repository is documented as a **Master's-level software and analytics project**.  
It demonstrates how to design, implement, and evaluate a multi-agent decision-support system that combines:
- an OLAP-style warehouse (DuckDB star schema),
- LLM-assisted analytical reasoning,
- and a reproducible full-stack deployment workflow.

## Documentation Index

- [Architecture Overview](ARCHITECTURE.md)
- [Star Schema Documentation](data_access/STAR_SCHEMA.md)
- [Frontend Documentation](frontend/README.md)
- [Prompt Library](PROMPTS.md)

## 1. Project Abstract

Retail teams often need fast answers to complex questions (trend breaks, regional performance shifts, category risk, and KPI movement). Traditional dashboards provide slices of data but not decision-ready narratives.

This project implements a multi-agent analytical system where specialized agents query curated warehouse aggregates and return structured reports (`executiveSummary`, `keyFindings`, `risks`, `recommendations`, `chartData`). The system supports two operating modes:
- **LLM-enabled mode** (OpenAI via LangChain), and
- **deterministic fallback mode** (no API key required), enabling reproducible local testing and robust demo behavior.

## 2. Problem Statement

How can we build a reliable, explainable analytics assistant that:
1. integrates OLAP data modeling with LLM-based insight generation,
2. preserves stable output contracts for product integration,
3. and remains usable when LLM services are unavailable?

## 3. Project Objectives

1. Build a modular multi-agent analytics architecture with clear layer boundaries.
2. Use a star-schema warehouse for consistent and query-efficient analytical slices.
3. Expose a validated API contract for frontend and external clients.
4. Provide deterministic fallback behavior for resilience and reproducibility.
5. Persist interaction history to support auditability and longitudinal analysis.

## 4. Research Questions (Suggested for Thesis Write-up)

1. Does an agent-based architecture improve maintainability versus a single monolithic analytics service?
2. How does deterministic fallback mode affect system reliability in real-world deployment conditions?
3. What is the quality difference between LLM-generated narratives and deterministic summaries for retail analytics tasks?
4. Which metrics best capture success: latency, contract stability, insight usefulness, or user trust?

## 5. System Scope

### In Scope
- Retail analytics Q&A through predefined agents.
- DuckDB-backed OLAP-style querying using curated aggregation methods.
- End-to-end flow: frontend -> API -> planner -> agent -> warehouse/history.
- Local + containerized deployment; cloud blueprint with Render.

### Out of Scope
- Real-time streaming ingestion.
- Advanced role-based authorization.
- Automated model fine-tuning.
- Distributed warehouse scaling beyond single-node DuckDB.

## 6. Architecture and Components

Runtime pipeline:
1. Frontend calls API (`/agents`, `/analyze`, `/history`).
2. API validates payload and routes to `PlannerOrchestrator`.
3. Planner resolves `agent_id` from `AGENT_REGISTRY`, executes selected agent, and stores run history.
4. Agent reads warehouse aggregates and returns normalized report JSON.
5. History endpoint returns recent stored runs by `user_id`.

Repository map:

```text
.
|-- api/                    # FastAPI app + request/response schemas
|-- agents/                 # Agent interface + LangChain implementation + registry
|-- planner/                # Run coordination and history writes
|-- data_access/            # DuckDB warehouse + history adapters + schema SQL
|-- frontend/               # React client
|-- scripts/check_api.py    # API smoke check
|-- render.yaml             # Render Blueprint (API + static frontend)
`-- docker-compose.yml      # Local multi-service stack
```

## 7. Data and Analytical Model

- Dataset source file: `global_retail_sales.csv`
- Warehouse: `retail_warehouse.duckdb`
- History store: `agent_history.duckdb`
- Query access is intentionally constrained through `StarSchemaWarehouse` methods (for example `overview`, `revenue_by_region`, `revenue_by_category`, `revenue_by_period`) to keep agent behavior consistent and testable.

## 8. API Contract

Base URL:
- Docker Compose default: `http://localhost:8001`
- Direct Uvicorn default: `http://localhost:8000`

### `GET /health`
```json
{ "status": "ok" }
```

### `GET /agents`
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
- Returns most recent first

## 9. Environment Variables

| Variable | Required | Default | Used By | Notes |
|---|---|---|---|---|
| `OPENAI_API_KEY` | No | empty | API/agents | Missing key triggers deterministic fallback mode. |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | API/agents | LLM model for LangChain agent calls. |
| `WAREHOUSE_DB_PATH` | No | `retail_warehouse.duckdb` | API/data_access | DuckDB file with star schema tables. |
| `HISTORY_DB_PATH` | No | `agent_history.duckdb` | API/data_access | DuckDB file for `agent_history`. |
| `CSV_PATH` | No | `global_retail_sales.csv` | API entrypoint | Used when warehouse DB must be built at startup. |
| `CORS_ORIGINS` | No | built-in allowlist | API | Comma-separated origins. |
| `VITE_API_URL` | Yes (frontend) | none | Frontend | Required for frontend API calls. |
| `API_HOST_PORT` | No | `8001` | docker-compose | Host bind for API container port 8000. |
| `FRONTEND_HOST_PORT` | No | `5174` | docker-compose | Host bind for frontend container port 5174. |

## 10. Reproducible Setup

### Option A: Docker Compose (recommended)

1. Configure `.env`:
```bash
OPENAI_API_KEY=...
```
2. Start:
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

### Option B: Run Services Directly

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
# PowerShell example:
$env:VITE_API_URL="http://localhost:8000"
npm run dev
```

Smoke test:
```bash
python scripts/check_api.py --base-url http://127.0.0.1:8001
```

## 11. Evaluation Plan (Master's Project)

Use this section as your baseline methodology chapter.

### 11.1 Technical Metrics
- API latency (`/analyze`) with and without LLM.
- Error rate by endpoint and by failure class (invalid payload, unknown agent, model failure).
- Contract conformance: percentage of responses matching required report schema.
- Fallback reliability: successful response rate when `OPENAI_API_KEY` is absent.

### 11.2 Analytical Quality Metrics
- Expert review score of `executiveSummary`, `keyFindings`, and `recommendations`.
- Hallucination incidence (claims not supported by warehouse aggregates).
- Actionability rating from target users (e.g., analysts/managers).

### 11.3 Suggested Experiment Design
1. Define a fixed benchmark set of prompts (KPI, trend, category, region, risk).
2. Run each prompt in LLM mode and fallback mode.
3. Compare output quality, latency, and consistency.
4. Report trade-offs and include representative cases.

## 12. Deployment Notes

- `render.yaml` provisions both API and static frontend services.
- API startup checks warehouse and history DB connectivity.
- In containerized mode, `api/entrypoint.sh` can build warehouse DB automatically if missing.
- History is persisted in DuckDB; Docker Compose uses `duckdb_data` volume for persistence.

## 13. Extending the Project

1. Register a new agent in `agents/__init__.py` (`AGENT_REGISTRY`).
2. Implement behavior by extending `AnalyticsAgent` or reusing `LangChainAnalyticsAgent`.
3. Preserve response schema (`message` + `report`) because frontend rendering depends on it.
4. Add benchmark prompts and tests before introducing major agent logic changes.

## 14. Suggested Thesis Deliverables

1. Architecture and design rationale document.
2. Experimental results (latency, reliability, quality metrics).
3. Reproducible deployment package (`docker-compose.yml` + environment template).
4. Critical reflection on limitations, ethical concerns, and future work.
