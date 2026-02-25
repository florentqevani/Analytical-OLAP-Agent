#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"
WAREHOUSE_DB_PATH="${WAREHOUSE_DB_PATH:-/app/data/retail_warehouse.duckdb}"
HISTORY_DB_PATH="${HISTORY_DB_PATH:-/app/data/agent_history.duckdb}"
CSV_PATH="${CSV_PATH:-/app/global_retail_sales.csv}"

export WAREHOUSE_DB_PATH
export HISTORY_DB_PATH

mkdir -p "$(dirname "$WAREHOUSE_DB_PATH")"
mkdir -p "$(dirname "$HISTORY_DB_PATH")"

if [ ! -f "$WAREHOUSE_DB_PATH" ]; then
  echo "Building star schema at $WAREHOUSE_DB_PATH from $CSV_PATH"
  python data_access/build_star_schema.py --db "$WAREHOUSE_DB_PATH" --csv "$CSV_PATH"
fi

exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
