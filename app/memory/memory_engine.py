from __future__ import annotations

import sqlite3


class MemoryEngine:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def save_note(self, content: str) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("INSERT INTO notes (payload) VALUES (?)", (content,))
            conn.commit()

    def get_notes(self) -> list[str]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute("SELECT payload FROM notes ORDER BY id DESC").fetchall()
        return [row[0] for row in rows]
