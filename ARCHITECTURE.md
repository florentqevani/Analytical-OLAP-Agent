# System Architecture

This project now includes the requested layered structure:

```
frontend/                # React frontend (Vite)
api/                     # FastAPI API layer
planner/                 # Planner / Orchestrator
agents/                  # LangChain agent modules
data_access/             # Data access layer + star schema artifacts
```

## Technology Stack

- Frontend: React (Vite)
- API: FastAPI
- Agents: LangChain
- LLM: OpenAI (`OPENAI_API_KEY`)
- Database: DuckDB

## Runtime Flow

1. Frontend sends analysis request to FastAPI.
2. API passes request to Planner/Orchestrator.
3. Orchestrator invokes selected agent(s):
   - Dimension Navigator
   - Cube Operations
   - KPI Calculator
   - Report Generator
   - Visualization (optional)
   - Anomaly Detection (optional)
   - Executive Summary (optional)
4. Data access layer reads star schema data from DuckDB.
5. Result is returned and stored in history.

## Run

1. Install Python dependencies:
   - `pip install -r requirements.txt`
2. Build star schema:
   - `python data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv`
3. Set OpenAI key:
   - `set OPENAI_API_KEY=your_key_here` (Windows) or export in shell
4. Start API:
   - `uvicorn api.main:app --reload`
5. Start React frontend:
   - `cd frontend && npm install && npm run dev`
