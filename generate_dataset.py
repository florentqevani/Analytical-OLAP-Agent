#!/usr/bin/env python3
"""
Generate a synthetic Global Retail Sales dataset.

Spec:
- Records: 10,000 transactions (default)
- Time period: January 2022 - December 2024
- Regions: North America, Europe, Asia Pacific, Latin America
- Categories: Electronics, Furniture, Office Supplies, Clothing
- Dimensions:
  order_date, year, quarter, month, month_name
  region, country
  category, subcategory
  customer_segment
- Measures:
  quantity, unit_price, revenue, cost, profit, profit_margin
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)
DEFAULT_ROWS = 10_000


REGION_COUNTRY_MAP = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["United Kingdom", "Germany", "France", "Spain", "Italy"],
    "Asia Pacific": ["China", "Japan", "India", "Australia", "Singapore"],
    "Latin America": ["Brazil", "Argentina", "Chile", "Colombia", "Peru"],
}

CATEGORY_SUBCATEGORY_MAP = {
    "Electronics": ["Phones", "Laptops", "Accessories", "Wearables"],
    "Furniture": ["Chairs", "Desks", "Tables", "Storage"],
    "Office Supplies": ["Paper", "Binders", "Writing", "Appliances"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
}

CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Small Business", "Home Office"]


@dataclass(frozen=True)
class PriceBand:
    low: float
    high: float


SUBCATEGORY_PRICE_BANDS = {
    "Phones": PriceBand(250, 1200),
    "Laptops": PriceBand(600, 2500),
    "Accessories": PriceBand(10, 150),
    "Wearables": PriceBand(80, 650),
    "Chairs": PriceBand(45, 550),
    "Desks": PriceBand(120, 1400),
    "Tables": PriceBand(80, 1100),
    "Storage": PriceBand(30, 700),
    "Paper": PriceBand(3, 30),
    "Binders": PriceBand(4, 35),
    "Writing": PriceBand(1, 20),
    "Appliances": PriceBand(20, 300),
    "Men": PriceBand(10, 180),
    "Women": PriceBand(10, 220),
    "Kids": PriceBand(8, 120),
    "Footwear": PriceBand(18, 260),
}


CATEGORY_COST_RATIO = {
    "Electronics": (0.62, 0.88),
    "Furniture": (0.55, 0.82),
    "Office Supplies": (0.45, 0.78),
    "Clothing": (0.40, 0.72),
}


def random_order_date(rng: random.Random) -> date:
    span_days = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=rng.randint(0, span_days))


def quarter_from_month(month: int) -> int:
    return (month - 1) // 3 + 1


def weighted_choice(rng: random.Random, items: list[str], weights: list[float]) -> str:
    return rng.choices(items, weights=weights, k=1)[0]


def generate_row(rng: random.Random) -> dict[str, str | int | float]:
    # Slight regional skew to make aggregates more realistic.
    region = weighted_choice(
        rng,
        list(REGION_COUNTRY_MAP.keys()),
        [0.33, 0.27, 0.28, 0.12],
    )
    country = rng.choice(REGION_COUNTRY_MAP[region])

    category = weighted_choice(
        rng,
        list(CATEGORY_SUBCATEGORY_MAP.keys()),
        [0.30, 0.22, 0.24, 0.24],
    )
    subcategory = rng.choice(CATEGORY_SUBCATEGORY_MAP[category])
    customer_segment = weighted_choice(
        rng, CUSTOMER_SEGMENTS, [0.46, 0.26, 0.17, 0.11]
    )

    order_dt = random_order_date(rng)
    month = order_dt.month
    year = order_dt.year
    quarter = quarter_from_month(month)
    month_name = order_dt.strftime("%B")

    # Quantity and price are varied by category/subcategory.
    quantity = rng.randint(1, 18)
    band = SUBCATEGORY_PRICE_BANDS[subcategory]
    unit_price = round(rng.uniform(band.low, band.high), 2)

    revenue = round(quantity * unit_price, 2)
    cost_low, cost_high = CATEGORY_COST_RATIO[category]
    cost_ratio = rng.uniform(cost_low, cost_high)
    cost = round(revenue * cost_ratio, 2)
    profit = round(revenue - cost, 2)
    profit_margin = round((profit / revenue) if revenue else 0.0, 4)

    return {
        "order_date": order_dt.isoformat(),
        "year": year,
        "quarter": quarter,
        "month": month,
        "month_name": month_name,
        "region": region,
        "country": country,
        "category": category,
        "subcategory": subcategory,
        "customer_segment": customer_segment,
        "quantity": quantity,
        "unit_price": unit_price,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "profit_margin": profit_margin,
    }


def generate_dataset(output_path: Path, rows: int, seed: int) -> None:
    rng = random.Random(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "order_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "region",
        "country",
        "category",
        "subcategory",
        "customer_segment",
        "quantity",
        "unit_price",
        "revenue",
        "cost",
        "profit",
        "profit_margin",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(rows):
            writer.writerow(generate_row(rng))

    print(f"Generated {rows:,} rows -> {output_path}")
    print(f"Date range: {START_DATE.isoformat()} to {END_DATE.isoformat()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Global Retail Sales CSV dataset.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("global_retail_sales.csv"),
        help="Output CSV path (default: global_retail_sales.csv)",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help=f"Number of rows to generate (default: {DEFAULT_ROWS})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic output (default: 42)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rows < 1:
        raise SystemExit("--rows must be >= 1")
    generate_dataset(args.output, args.rows, args.seed)


if __name__ == "__main__":
    main()
