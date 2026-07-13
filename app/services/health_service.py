from __future__ import annotations

import sqlite3
from pathlib import Path

from app.services.base_service import BaseService
from app.services.plugin_service import PluginService
from app.services.tool_service import ToolService


class HealthService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.plugins = PluginService(system)
        self.tools = ToolService(system)

    def health(self) -> dict[str, object]:
        return {
            "status": "ok",
            "database": self._database_status(),
            "vector_database": self._vector_status(),
            "memory": self._memory_status(),
            "plugin": {"status": "ok", "count": self.plugins.count()},
            "tool": {"status": "ok", "count": self.tools.count()},
        }

    def status(self) -> dict[str, object]:
        payload = self.health()
        payload["application"] = {
            "name": "Open-Personal-AI-Assistant",
            "settings_validation": self.settings.settings_validation_report,
        }
        return payload

    def metrics(self) -> dict[str, object]:
        with sqlite3.connect(self.settings.database) as conn:
            api_requests = int(conn.execute("SELECT COUNT(*) FROM api_requests").fetchone()[0] or 0)
        return {
            "api_requests": api_requests,
            "plugin_count": self.plugins.count(),
            "tool_count": self.tools.count(),
        }

    def _database_status(self) -> dict[str, object]:
        try:
            with sqlite3.connect(self.settings.database) as conn:
                conn.execute("SELECT 1").fetchone()
            return {"status": "ok", "path": self.settings.database}
        except Exception as exc:
            return {"status": "error", "path": self.settings.database, "error": str(exc)}

    def _vector_status(self) -> dict[str, object]:
        path = Path(self.settings.vector_db)
        return {
            "status": "ok" if path.exists() else "warning",
            "path": str(path),
            "exists": path.exists(),
        }

    def _memory_status(self) -> dict[str, object]:
        try:
            with sqlite3.connect(self.settings.database) as conn:
                conversations = int(conn.execute("SELECT COUNT(*) FROM conversation_memory").fetchone()[0] or 0)
                entities = int(conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0] or 0)
            return {"status": "ok", "conversation_count": conversations, "entity_count": entities}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
