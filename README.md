# Multi-Agent OLAP Analytics — Retail Decision Support

A full-stack analytics application that transforms retail CSV data into AI-powered reports through a multi-agent system backed by a DuckDB star-schema warehouse.

## Documentation

| Document | Description |
|---|---|
| [Architecture Overview](docs/ARCHITECTURE.md) | Layer responsibilities, request lifecycle, runtime modes, deployment model |
| [Star Schema](docs/data/STAR_SCHEMA.md) | Fact/dimension tables, surrogate keys, build pipeline |
| [Full Project Docs](docs/README.md) | Abstract, objectives, API contract, research questions |
| [Frontend Notes](docs/frontend/README.md) | React/Vite client, environment variables, build for static hosting |

## Stack

- **Backend** — FastAPI, DuckDB, LangChain + OpenAI (`gpt-4o-mini`)
- **Frontend** — React + Vite
- **Warehouse** — DuckDB star schema built from `global_retail_sales.csv`
- **Deploy** — Docker Compose (local) · Render Blueprint (cloud)

---

## Running the Project

### Option 1 — Docker Compose (recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# 1. Clone and enter the project
cd "Zed Project"

# 2. (Optional) create a .env file for secrets
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Start both services
docker compose up --build
```

| Service | URL |
|---|---|
| API | http://localhost:8001 |
| Frontend | http://localhost:5174 |
| API health | http://localhost:8001/health |

The API container automatically builds the star schema from the CSV on first start if the warehouse file is absent.

To change default ports, set `API_HOST_PORT` and `FRONTEND_HOST_PORT` in `.env`.

---

### Option 2 — Local Development

#### Prerequisites

- Python 3.11+
- Node.js 18+

#### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 2. Build the warehouse

```bash
python src/data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv
```

#### 3. Start the API

```bash
# PowerShell
$env:WAREHOUSE_DB_PATH="retail_warehouse.duckdb"
$env:HISTORY_DB_PATH="agent_history.duckdb"
$env:CSV_PATH="global_retail_sales.csv"
# Optional — enables LLM mode:
$env:OPENAI_API_KEY="sk-..."

uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

API is available at http://localhost:8001. Without `OPENAI_API_KEY` the system runs in **deterministic fallback mode** (fully functional, no LLM calls).

#### 4. Start the frontend

```bash
cd src/frontend
npm install

# PowerShell
$env:VITE_API_URL="http://localhost:8001"
npm run dev
```

Frontend is available at http://localhost:5173.

---

### Option 3 — Render (cloud)

The `render.yaml` Blueprint wires the API and frontend services together automatically.

1. Push the repository to GitHub.
2. In the [Render dashboard](https://dashboard.render.com), click **New > Blueprint** and connect the repo.
3. Set `OPENAI_API_KEY` as a secret environment variable on the API service.

Render builds and deploys both services; `VITE_API_URL` and `CORS_ORIGINS` are cross-wired automatically via `fromService` references.

---

## Environment Variables

### API

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(none)_ | Enables LLM mode. Fallback mode used when absent. |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `WAREHOUSE_DB_PATH` | `retail_warehouse.duckdb` | Path to warehouse DuckDB file |
| `HISTORY_DB_PATH` | `agent_history.duckdb` | Path to history DuckDB file |
| `CSV_PATH` | `global_retail_sales.csv` | Source data file |
| `CORS_ORIGINS` | localhost allowlist | Comma-separated allowed origins |
| `PORT` | `8000` | Uvicorn bind port |

### Frontend

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Full base URL of the API (e.g. `http://localhost:8001`) |

---

## Verify the API

```bash
python src/scripts/check_api.py
```

## Project Structure

```
.
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── README.md
│   ├── data/STAR_SCHEMA.md
│   └── frontend/README.md
├── src/
│   ├── agents/                  # Agent interface, LangChain implementation, registry
│   ├── api/                     # FastAPI app, schemas, Dockerfile
│   ├── data_access/             # DuckDB warehouse + history adapters + schema SQL
│   ├── frontend/                # React/Vite client
│   ├── planner/                 # Run coordination and history writes
│   ├── scripts/check_api.py     # API smoke test
│   └── generate_dataset.py      # Dataset generation utility
├── global_retail_sales.csv      # Source data
├── docker-compose.yml
├── render.yaml
└── requirements.txt
```
