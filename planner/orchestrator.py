from __future__ import annotations

from typing import Any

from agents import AGENT_REGISTRY
from data_access.history_store import HistoryStore
from data_access.warehouse import StarSchemaWarehouse


class PlannerOrchestrator:
    def __init__(
        self,
        warehouse: StarSchemaWarehouse,
        history_store: HistoryStore,
    ) -> None:
        self.warehouse = warehouse
        self.history_store = history_store

    def list_agents(self) -> list[dict[str, str]]:
        return [
            {"agent_id": agent_id, "label": agent.label}
            for agent_id, agent in AGENT_REGISTRY.items()
        ]

    def run_agent(self, user_id: str, agent_id: str, prompt: str) -> dict[str, Any]:
        if agent_id not in AGENT_REGISTRY:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent = AGENT_REGISTRY[agent_id]
        result = agent.run(prompt=prompt, warehouse=self.warehouse)

        history_id = self.history_store.save(
            user_id=user_id,
            agent_id=agent_id,
            prompt=prompt,
            response=result,
        )

        return {
            "history_id": history_id,
            "agent_id": agent_id,
            "agent_label": agent.label,
            "result": result,
        }

    def history_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self.history_store.list_for_user(user_id=user_id, limit=limit)
