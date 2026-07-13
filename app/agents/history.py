from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any


class AgentHistoryStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    workflow TEXT,
                    duration_seconds REAL NOT NULL,
                    status TEXT NOT NULL,
                    citations_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def record(
        self,
        task_id: str,
        agent_name: str,
        workflow: str | None,
        duration_seconds: float,
        status: str,
        citations: list[str],
    ) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO agent_history (
                    task_id, agent_name, workflow, duration_seconds, status, citations_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    agent_name,
                    workflow,
                    float(duration_seconds),
                    status,
                    json.dumps(citations, ensure_ascii=False),
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT task_id, agent_name, workflow, duration_seconds, status, citations_json, created_at
                FROM agent_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (max(1, limit),),
            ).fetchall()
        return [
            {
                "task_id": row[0],
                "agent_name": row[1],
                "workflow": row[2] or "",
                "duration_seconds": float(row[3]),
                "status": row[4],
                "citations": json.loads(row[5] or "[]"),
                "created_at": row[6],
            }
            for row in rows
        ]
