-- Star schema transformation for Global Retail Sales
-- Input: flat CSV with transaction-level rows
-- Output:
--   dim_date(year, quarter, month, day)
--   dim_geography(region, country)
--   dim_product(category, subcategory)
--   dim_customer(segment)
--   fact_sales(quantity, revenue, cost, profit)

DROP TABLE IF EXISTS stg_sales;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;

CREATE TABLE stg_sales AS
SELECT
  CAST(order_date AS DATE) AS order_date,
  CAST(year AS INTEGER) AS year,
  CAST(quarter AS INTEGER) AS quarter,
  CAST(month AS INTEGER) AS month,
  CAST(month_name AS VARCHAR) AS month_name,
  CAST(region AS VARCHAR) AS region,
  CAST(country AS VARCHAR) AS country,
  CAST(category AS VARCHAR) AS category,
  CAST(subcategory AS VARCHAR) AS subcategory,
  CAST(customer_segment AS VARCHAR) AS customer_segment,
  CAST(quantity AS INTEGER) AS quantity,
  CAST(revenue AS DOUBLE) AS revenue,
  CAST(cost AS DOUBLE) AS cost,
  CAST(profit AS DOUBLE) AS profit
FROM read_csv_auto($csv_path, header=true);

CREATE TABLE dim_date AS
SELECT
  ROW_NUMBER() OVER (ORDER BY order_date) AS date_key,
  order_date AS full_date,
  EXTRACT(YEAR FROM order_date)::INTEGER AS year,
  EXTRACT(QUARTER FROM order_date)::INTEGER AS quarter,
  EXTRACT(MONTH FROM order_date)::INTEGER AS month,
  EXTRACT(DAY FROM order_date)::INTEGER AS day,
  STRFTIME(order_date, '%B') AS month_name
FROM (
  SELECT DISTINCT order_date
  FROM stg_sales
) d;

CREATE TABLE dim_geography AS
SELECT
  ROW_NUMBER() OVER (ORDER BY region, country) AS geography_key,
  region,
  country
FROM (
  SELECT DISTINCT region, country
  FROM stg_sales
) g;

CREATE TABLE dim_product AS
SELECT
  ROW_NUMBER() OVER (ORDER BY category, subcategory) AS product_key,
  category,
  subcategory
FROM (
  SELECT DISTINCT category, subcategory
  FROM stg_sales
) p;

CREATE TABLE dim_customer AS
SELECT
  ROW_NUMBER() OVER (ORDER BY customer_segment) AS customer_key,
  customer_segment AS segment
FROM (
  SELECT DISTINCT customer_segment
  FROM stg_sales
) c;

CREATE TABLE fact_sales AS
SELECT
  ROW_NUMBER() OVER () AS sales_key,
  d.date_key,
  g.geography_key,
  p.product_key,
  c.customer_key,
  s.quantity,
  s.revenue,
  s.cost,
  s.profit
FROM stg_sales s
JOIN dim_date d
  ON d.full_date = s.order_date
JOIN dim_geography g
  ON g.region = s.region
 AND g.country = s.country
JOIN dim_product p
  ON p.category = s.category
 AND p.subcategory = s.subcategory
JOIN dim_customer c
  ON c.segment = s.customer_segment;
