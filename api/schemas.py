from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=120)
    agent_id: str = Field(..., min_length=1, max_length=80)
    prompt: str = Field(..., min_length=1, max_length=3000)


class AnalyzeResponse(BaseModel):
    history_id: str
    agent_id: str
    agent_label: str
    result: dict[str, Any]


class HistoryResponse(BaseModel):
    items: list[dict[str, Any]]
