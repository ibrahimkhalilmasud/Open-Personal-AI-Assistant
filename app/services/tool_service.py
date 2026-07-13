from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from app.services.base_service import BaseService


class ToolService(BaseService):
    def list_tools(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.settings.database) as conn:
            rows = conn.execute(
                "SELECT tool_name, metadata_json, enabled, installed_at, updated_at FROM installed_tools ORDER BY tool_name"
            ).fetchall()
        return [
            {
                "name": str(row[0]),
                "metadata_json": str(row[1] or "{}"),
                "enabled": bool(row[2]),
                "installed_at": str(row[3]),
                "updated_at": str(row[4]),
            }
            for row in rows
        ]

    def upsert_tool(self, name: str, metadata_json: str = "{}", enabled: bool = True) -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.settings.database) as conn:
            conn.execute(
                """
                INSERT INTO installed_tools (tool_name, metadata_json, enabled, installed_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(tool_name) DO UPDATE SET
                    metadata_json=excluded.metadata_json,
                    enabled=excluded.enabled,
                    updated_at=excluded.updated_at
                """,
                (name, metadata_json, int(enabled), now, now),
            )
            conn.commit()

    def remove_tool(self, name: str) -> int:
        with sqlite3.connect(self.settings.database) as conn:
            cursor = conn.execute("DELETE FROM installed_tools WHERE tool_name = ?", (name,))
            conn.commit()
            return int(cursor.rowcount)

    def count(self) -> int:
        with sqlite3.connect(self.settings.database) as conn:
            return int(conn.execute("SELECT COUNT(*) FROM installed_tools").fetchone()[0] or 0)
