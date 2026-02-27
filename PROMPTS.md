# Prompt Library

This file contains ready-to-use prompts for the agents in this project.

## Quick Start

Use any prompt below in the frontend prompt box or in `POST /analyze`:

```json
{
  "user_id": "demo_user",
  "agent_id": "kpi_calculator",
  "prompt": "Analyze month-over-month and year-over-year revenue and profit trends, then list key risks and recommended actions."
}
```

## Agent-Specific Prompts

### `dimension_navigator`

1. Drill down revenue from year to quarter to month and identify the strongest and weakest periods.
2. Roll up monthly performance to quarter and year; explain whether growth is broad-based or concentrated.
3. Compare category performance across time hierarchy levels and highlight where trends change direction.

### `cube_operations`

1. Slice revenue for one region and summarize category leaders and laggards.
2. Dice by region and category to find combinations with high revenue but low profit.
3. Pivot the analysis from category-first to region-first and explain what decisions change.

### `kpi_calculator`

1. Calculate month-over-month and year-over-year revenue growth, including top positive and negative shifts.
2. Compute profit margin trends and identify periods where margin deteriorates despite revenue growth.
3. Rank top 5 regions by revenue and profit, then state concentration risk.

### `report_generator`

1. Generate an executive business report with summary, key findings, risks, recommendations, and chart-ready data.
2. Create a board-ready quarterly performance report with clear priorities for the next quarter.
3. Produce a concise operations report focused on revenue drivers, profit pressure points, and immediate actions.

### `visualization`

1. Recommend the best chart structure for revenue by region and return chart-ready series values.
2. Build chart data for category contribution and label each point clearly for dashboard use.
3. Return a period-over-period trend chart data series and include an appropriate metric/unit.

### `anomaly_detection`

1. Detect unusual revenue or profit patterns by period and explain potential business impact.
2. Identify outlier regions or categories and classify each anomaly by severity.
3. Flag sudden trend breaks, suggest likely causes, and propose follow-up checks.

## Benchmark Prompt Set

Use this fixed set for LLM vs fallback comparisons (quality, latency, consistency):

1. Analyze MoM and YoY revenue changes and summarize the top 3 movements.
2. Identify the highest and lowest performing regions by revenue and profit.
3. Compare category revenue contribution and highlight concentration risk.
4. Find periods where profit margin drops while revenue grows.
5. Detect anomalous spikes or drops and rank them by potential business impact.
6. Create an executive summary with risks and actionable recommendations.
7. Suggest the best chart for regional comparison and return chart-ready data.
8. Drill down from year to quarter to month to explain a major trend change.
9. Slice to one region and explain what drives performance in that slice.
10. Dice by region and category and highlight weak combinations.

## Prompt Writing Guidelines

1. Include objective + scope + expected output in one request.
2. Ask for explicit comparisons (MoM, YoY, region vs region, category vs category).
3. Request business impact and concrete recommendations, not only description.
4. Keep prompts under the API limit (`3000` characters).
5. If using uploaded CSV context from the frontend, keep sample rows short and relevant.
