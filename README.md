# Analytical-OLAP-Agent

## Project Structure

```
.
├─ frontend/               # React frontend (Vite)
│  ├─ src/App.jsx
│  └─ package.json
├─ api/                    # FastAPI API layer
│  ├─ main.py
│  └─ schemas.py
├─ planner/                # Planner / orchestrator
│  └─ orchestrator.py
├─ agents/                 # LangChain agents (OpenAI-backed)
│  ├─ langchain_agent.py
│  └─ __init__.py
├─ data_access/            # Data access + star schema
│  ├─ warehouse.py
│  ├─ history_store.py
│  ├─ star_schema.sql
│  └─ build_star_schema.py
├─ global_retail_sales.csv
├─ retail_warehouse.duckdb
├─ ARCHITECTURE.md
└─ requirements.txt
```

## Quick Start

### Deploy on Render (recommended)

This repository now includes a Render Blueprint in `render.yaml` that deploys:

- `analytical-olap-agent-api` (FastAPI web service)
- `analytical-olap-agent-frontend` (static site)

Steps:

1. Push this repo to GitHub.
2. In Render, create a new Blueprint and select this repo.
3. Set `OPENAI_API_KEY` for the API service.
4. Deploy.

The Blueprint wires:

- Frontend `VITE_API_URL` -> API `RENDER_EXTERNAL_URL`
- API `CORS_ORIGINS` -> Frontend `RENDER_EXTERNAL_URL`

### Run with Docker (recommended)

1. Add your OpenAI key in `.env`:
   - `OPENAI_API_KEY=your_key_here`
2. Build and run:
   - `docker compose up --build`
3. Open:
   - UI: `http://localhost:5174`
   - API health: `http://localhost:8001/health`
4. Optional host port overrides:
   - `API_HOST_PORT=8000 FRONTEND_HOST_PORT=5173 docker compose up --build`

### Run without Docker

1. Install Python dependencies:
   - `pip install -r requirements.txt`
2. Build star schema (if needed):
   - `python data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv`
3. Set OpenAI API key:
   - `OPENAI_API_KEY=...`
4. Run API:
   - `uvicorn api.main:app --reload`
5. Run React frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
