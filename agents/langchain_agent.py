from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.base import AnalyticsAgent
from agents.models import AgentRunResult
from data_access.warehouse import StarSchemaWarehouse


class LangChainAnalyticsAgent(AnalyticsAgent):
    def __init__(self, agent_id: str, label: str, specialization: list[str]) -> None:
        self.agent_id = agent_id
        self.label = label
        self.specialization = specialization

    def _fallback(self, prompt: str, warehouse: StarSchemaWarehouse) -> AgentRunResult:
        overview = warehouse.overview()
        by_region = warehouse.revenue_by_region()[:8]

        return {
            "message": (
                f"{self.label} fallback response. OPENAI_API_KEY is missing or invalid; "
                "returning deterministic warehouse summary."
            ),
            "report": {
                "title": f"{self.label} Report",
                "executiveSummary": (
                    f"Transactions: {overview['transactions']}, total revenue: {overview['total_revenue']}, "
                    f"total profit: {overview['total_profit']}. Prompt: {prompt}"
                ),
                "keyFindings": [
                    f"Agent specialization: {item}" for item in self.specialization[:3]
                ],
                "risks": [
                    "LLM not available; insights are deterministic only.",
                    "Narrative quality is reduced without model generation.",
                ],
                "recommendations": [
                    "Set OPENAI_API_KEY for richer natural-language analysis.",
                    "Use history endpoint to compare outputs over time.",
                ],
                "chartHint": {"dimension": "region", "metric": "revenue"},
                "chartData": {
                    "title": "Revenue by Region",
                    "unit": "USD",
                    "series": [
                        {"label": row["region"], "value": row["revenue"]}
                        for row in by_region
                    ],
                },
            },
        }

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    return {}
            return {}

    def run(self, prompt: str, warehouse: StarSchemaWarehouse) -> AgentRunResult:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return self._fallback(prompt, warehouse)

        overview = warehouse.overview()
        by_region = warehouse.revenue_by_region()[:8]
        by_category = warehouse.revenue_by_category()[:8]
        by_period = warehouse.revenue_by_period()[:18]

        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            api_key=api_key,
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are {label}. You are part of a multi-agent analytics system built with LangChain. "
                        "Apply your specialization strictly.\n"
                        "Specialization:\n{specialization}\n\n"
                        "Return valid JSON only with this schema:\n"
                        "{{\n"
                        '  "message": string,\n'
                        '  "report": {{\n'
                        '    "title": string,\n'
                        '    "executiveSummary": string,\n'
                        '    "keyFindings": string[],\n'
                        '    "risks": string[],\n'
                        '    "recommendations": string[],\n'
                        '    "chartHint": {{"dimension": string, "metric": string}},\n'
                        '    "chartData": {{\n'
                        '      "title": string,\n'
                        '      "unit": string,\n'
                        '      "series": [{{"label": string, "value": number}}]\n'
                        "    }}\n"
                        "  }}\n"
                        "}}\n"
                        "Rules: keep lists 3-6 items; keep business language concise; chartData series 4-12 points."
                    ),
                ),
                (
                    "human",
                    (
                        "User prompt: {user_prompt}\n\n"
                        "Warehouse overview: {overview}\n"
                        "Revenue by region: {by_region}\n"
                        "Revenue by category: {by_category}\n"
                        "Revenue by period sample: {by_period}\n"
                    ),
                ),
            ]
        )

        specialization_lines = "\n".join(f"- {line}" for line in self.specialization)
        chain = prompt_template | llm
        ai_message = chain.invoke(
            {
                "label": self.label,
                "specialization": specialization_lines,
                "user_prompt": prompt,
                "overview": json.dumps(overview),
                "by_region": json.dumps(by_region),
                "by_category": json.dumps(by_category),
                "by_period": json.dumps(by_period),
            }
        )

        parsed = self._parse_json(str(ai_message.content))
        if not parsed or "report" not in parsed:
            return self._fallback(prompt, warehouse)

        message = str(parsed.get("message", f"{self.label} completed analysis."))
        report = parsed.get("report", {})
        if not isinstance(report, dict):
            return self._fallback(prompt, warehouse)

        return {
            "message": message,
            "report": {
                "title": str(report.get("title", f"{self.label} Report")),
                "executiveSummary": str(report.get("executiveSummary", message)),
                "keyFindings": [str(x) for x in report.get("keyFindings", [])][:8],
                "risks": [str(x) for x in report.get("risks", [])][:8],
                "recommendations": [str(x) for x in report.get("recommendations", [])][
                    :8
                ],
                "chartHint": {
                    "dimension": str(
                        (report.get("chartHint") or {}).get("dimension", "region")
                    ),
                    "metric": str(
                        (report.get("chartHint") or {}).get("metric", "revenue")
                    ),
                },
                "chartData": {
                    "title": str((report.get("chartData") or {}).get("title", "Chart")),
                    "unit": str((report.get("chartData") or {}).get("unit", "USD")),
                    "series": [
                        {
                            "label": str(item.get("label", "")),
                            "value": float(item.get("value", 0)),
                        }
                        for item in (report.get("chartData") or {}).get("series", [])
                        if isinstance(item, dict)
                    ][:12],
                },
            },
        }
