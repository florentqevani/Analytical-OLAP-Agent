from __future__ import annotations

from abc import ABC, abstractmethod

from src.agents.models import AgentRunResult
from src.data_access.warehouse import StarSchemaWarehouse


class AnalyticsAgent(ABC):
    agent_id: str
    label: str

    @abstractmethod
    def run(self, prompt: str, warehouse: StarSchemaWarehouse) -> AgentRunResult:
        raise NotImplementedError
