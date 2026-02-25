#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


def run_schema_build(db_path: Path, csv_path: Path, sql_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL model not found: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")
    csv_literal = str(csv_path.resolve()).replace("\\", "/").replace("'", "''")
    sql_text = sql_text.replace("$csv_path", f"'{csv_literal}'")

    con = duckdb.connect(str(db_path))
    try:
        con.execute(sql_text)

        checks = {
            "fact_sales": "SELECT COUNT(*) FROM fact_sales",
            "dim_date": "SELECT COUNT(*) FROM dim_date",
            "dim_geography": "SELECT COUNT(*) FROM dim_geography",
            "dim_product": "SELECT COUNT(*) FROM dim_product",
            "dim_customer": "SELECT COUNT(*) FROM dim_customer",
        }

        print(f"Star schema built at: {db_path.resolve()}")
        for table, query in checks.items():
            count = con.execute(query).fetchone()[0]
            print(f"{table}: {count:,}")
    finally:
        con.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build DuckDB star schema from Global Retail Sales CSV."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("retail_warehouse.duckdb"),
        help="DuckDB database output path (default: retail_warehouse.duckdb)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("global_retail_sales.csv"),
        help="Input flat CSV path (default: global_retail_sales.csv)",
    )
    parser.add_argument(
        "--sql",
        type=Path,
        default=Path("data_access/star_schema.sql"),
        help="SQL schema file path (default: data_access/star_schema.sql)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_schema_build(db_path=args.db, csv_path=args.csv, sql_path=args.sql)


if __name__ == "__main__":
    main()
