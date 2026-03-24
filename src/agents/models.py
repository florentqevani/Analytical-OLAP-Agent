from __future__ import annotations

from typing import Any, TypedDict


class AgentRunResult(TypedDict):
    message: str
    report: dict[str, Any]
