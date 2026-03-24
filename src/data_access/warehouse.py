from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb


class StarSchemaWarehouse:
    def __init__(self, db_path: str | Path = "retail_warehouse.duckdb") -> None:
        self.db_path = str(db_path)

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path, read_only=False)

    def fetch_one(self, sql: str, params: tuple[Any, ...] = ()) -> tuple[Any, ...]:
        with self._connect() as con:
            row = con.execute(sql, params).fetchone()
        return row if row is not None else tuple()

    def fetch_all(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._connect() as con:
            result = con.execute(sql, params)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def overview(self) -> dict[str, Any]:
        query = """
        SELECT
          COUNT(*) AS transactions,
          ROUND(SUM(quantity), 2) AS total_quantity,
          ROUND(SUM(revenue), 2) AS total_revenue,
          ROUND(SUM(cost), 2) AS total_cost,
          ROUND(SUM(profit), 2) AS total_profit
        FROM fact_sales
        """
        row = self.fetch_all(query)[0]
        return row

    def revenue_by_period(self) -> list[dict[str, Any]]:
        query = """
        SELECT
          d.year,
          d.quarter,
          d.month,
          ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_date d ON d.date_key = f.date_key
        GROUP BY d.year, d.quarter, d.month
        ORDER BY d.year, d.quarter, d.month
        """
        return self.fetch_all(query)

    def revenue_by_region(self) -> list[dict[str, Any]]:
        query = """
        SELECT
          g.region,
          ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_geography g ON g.geography_key = f.geography_key
        GROUP BY g.region
        ORDER BY revenue DESC
        """
        return self.fetch_all(query)

    def revenue_by_category(self) -> list[dict[str, Any]]:
        query = """
        SELECT
          p.category,
          ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_product p ON p.product_key = f.product_key
        GROUP BY p.category
        ORDER BY revenue DESC
        """
        return self.fetch_all(query)
