from __future__ import annotations

import sqlite3

REQUIRED_TABLES = (
    "files",
    "folders",
    "conversations",
    "memories",
    "notes",
    "reminders",
    "settings",
    "logs",
)


def initialize_database(path: str) -> None:
    with sqlite3.connect(path) as conn:
        for table in REQUIRED_TABLES:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )
        conn.commit()
