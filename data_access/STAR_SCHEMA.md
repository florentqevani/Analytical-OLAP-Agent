# Star Schema Design

This project transforms `global_retail_sales.csv` into a dimensional model with one fact table and four dimensions.

## Tables

### `fact_sales`
- Grain: one transaction row from source CSV
- Foreign keys:
  - `date_key` -> `dim_date.date_key`
  - `geography_key` -> `dim_geography.geography_key`
  - `product_key` -> `dim_product.product_key`
  - `customer_key` -> `dim_customer.customer_key`
- Measures:
  - `quantity`
  - `revenue`
  - `cost`
  - `profit`

### `dim_date`
- `year`, `quarter`, `month`, `day`
- Additional: `full_date`, `month_name`

### `dim_geography`
- `region`, `country`

### `dim_product`
- `category`, `subcategory`

### `dim_customer`
- `segment` (from `customer_segment`)

## Build

```bash
python data_access/build_star_schema.py --db retail_warehouse.duckdb --csv global_retail_sales.csv
```

The SQL model is in `data_access/star_schema.sql`.
