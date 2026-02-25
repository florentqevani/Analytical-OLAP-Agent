from agents.langchain_agent import LangChainAnalyticsAgent

AGENT_REGISTRY = {
    "dimension_navigator": LangChainAnalyticsAgent(
        agent_id="dimension_navigator",
        label="Dimension Navigator Agent",
        specialization=[
            "Drill-down: Year -> Quarter -> Month",
            "Roll-up: Day -> Month -> Quarter",
            "Hierarchy navigation",
        ],
    ),
    "cube_operations": LangChainAnalyticsAgent(
        agent_id="cube_operations",
        label="Cube Operations Agent",
        specialization=[
            "Slice: filter on single dimension",
            "Dice: filter on multiple dimensions",
            "Pivot: reorganize analytical perspective",
        ],
    ),
    "kpi_calculator": LangChainAnalyticsAgent(
        agent_id="kpi_calculator",
        label="KPI Calculator Agent",
        specialization=[
            "Year-over-year growth",
            "Month-over-month change",
            "Profit margins",
            "Top-N rankings",
        ],
    ),
    "report_generator": LangChainAnalyticsAgent(
        agent_id="report_generator",
        label="Report Generator Agent",
        specialization=[
            "Formatted tables with totals",
            "Conditional formatting hints",
            "Executive summaries",
        ],
    ),
    "visualization": LangChainAnalyticsAgent(
        agent_id="visualization",
        label="Visualization Agent",
        specialization=[
            "Select appropriate chart types",
            "Return chart-ready data",
        ],
    ),
    "anomaly_detection": LangChainAnalyticsAgent(
        agent_id="anomaly_detection",
        label="Anomaly Detection Agent",
        specialization=[
            "Identify unusual patterns and outliers",
            "Flag anomalies by business impact",
        ],
    ),
}

__all__ = ["AGENT_REGISTRY"]
