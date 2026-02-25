from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


class HistoryStore:
    def __init__(self, db_path: str | Path = "agent_history.duckdb") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path, read_only=False)

    def _init_schema(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_history (
                  history_id VARCHAR PRIMARY KEY,
                  created_at TIMESTAMP,
                  user_id VARCHAR,
                  agent_id VARCHAR,
                  prompt VARCHAR,
                  response_json VARCHAR
                )
                """
            )
            con.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_history_user_created
                ON agent_history(user_id, created_at)
                """
            )

    def save(
        self,
        user_id: str,
        agent_id: str,
        prompt: str,
        response: dict[str, Any],
    ) -> str:
        history_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(response)

        with self._connect() as con:
            con.execute(
                """
                INSERT INTO agent_history (
                  history_id, created_at, user_id, agent_id, prompt, response_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [history_id, created_at, user_id, agent_id, prompt, payload],
            )
        return history_id

    def list_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 200))
        with self._connect() as con:
            query = con.execute(
                """
                SELECT history_id, created_at, user_id, agent_id, prompt, response_json
                FROM agent_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                [user_id, safe_limit],
            )
            columns = [desc[0] for desc in query.description]
            fetched_rows = query.fetchall()
        rows = [dict(zip(columns, row)) for row in fetched_rows]

        result: list[dict[str, Any]] = []
        for row in rows:
            try:
                response = json.loads(row["response_json"])
            except json.JSONDecodeError:
                response = {}

            result.append(
                {
                    "history_id": row["history_id"],
                    "created_at": str(row["created_at"]),
                    "user_id": row["user_id"],
                    "agent_id": row["agent_id"],
                    "prompt": row["prompt"],
                    "response": response,
                }
            )
        return result
