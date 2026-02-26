# Star Schema

This project materializes `global_retail_sales.csv` into a star schema in DuckDB.

## Model Summary

- Fact table: `fact_sales`
- Dimensions: `dim_date`, `dim_geography`, `dim_product`, `dim_customer`
- Staging table: `stg_sales` (rebuilt during load)

## Grain and Keys

### Fact grain
- One row per source transaction row.

### Surrogate keys
- `date_key` -> `dim_date.date_key`
- `geography_key` -> `dim_geography.geography_key`
- `product_key` -> `dim_product.product_key`
- `customer_key` -> `dim_customer.customer_key`

### Measures
- `quantity` (INTEGER)
- `revenue` (DOUBLE)
- `cost` (DOUBLE)
- `profit` (DOUBLE)

## Dimension Semantics

- `dim_date`: distinct `order_date` with calendar rollups (`year`, `quarter`, `month`, `day`, `month_name`)
- `dim_geography`: distinct `(region, country)`
- `dim_product`: distinct `(category, subcategory)`
- `dim_customer`: distinct customer segment values (`segment`)

## Build Pipeline

Command:
```bash
python data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv
```

What it does:
1. Loads and parameterizes `data_access/star_schema.sql` with absolute CSV path.
2. Drops and recreates all schema tables.
3. Prints row counts for `fact_sales` and each dimension.

Important behavior:
- Build is destructive for schema tables (`DROP TABLE IF EXISTS ...` in SQL).
- Re-running rebuilds the model from source CSV.

## Query Surface Used by the App

The runtime app currently relies on these aggregate shapes:
- overall totals from `fact_sales`
- revenue by `region`
- revenue by `category`
- revenue by `year/quarter/month`

Those are implemented in `data_access/warehouse.py` and consumed by agents.

## Validation Queries

```sql
SELECT COUNT(*) FROM fact_sales;
SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM dim_geography;
SELECT COUNT(*) FROM dim_product;
SELECT COUNT(*) FROM dim_customer;
```

```sql
SELECT
  ROUND(SUM(revenue), 2) AS total_revenue,
  ROUND(SUM(profit), 2) AS total_profit
FROM fact_sales;
```

## Modification Guidelines

- If you add a new dimension or measure, update:
  - `data_access/star_schema.sql`
  - `data_access/warehouse.py` query helpers
  - any agent prompts/logic that reference available aggregates
- Keep schema rebuild deterministic and idempotent with respect to source CSV content.
