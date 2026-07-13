from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class TaskHistoryStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def record(self, task_id: str, status: str, message: str) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO task_history (task_id, status, message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, status, message, datetime.now(UTC).isoformat()),
            )
            conn.commit()
