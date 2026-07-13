from __future__ import annotations

import os
import sqlite3
import time
from datetime import UTC, datetime

from app.services.base_service import BaseService
from app.services.graph_service import GraphService
from app.services.plugin_service import PluginService
from app.services.tool_service import ToolService
from app.services.vault_service import VaultService


class SystemService(BaseService):
    started_at = time.time()

    def __init__(self, system) -> None:
        super().__init__(system)
        self.tools = ToolService(system)
        self.plugins = PluginService(system)
        self.graph = GraphService(system)
        self.vault = VaultService(system)

    def metrics(self) -> dict[str, object]:
        graph_stats = self.graph.stats()
        vault_stats = self.vault.stats()
        with sqlite3.connect(self.settings.database) as conn:
            vector_count = int(conn.execute("SELECT COALESCE(SUM(chunk_count), 0) FROM files").fetchone()[0] or 0)
            task_count = int(conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] or 0)
        return {
            "uptime_seconds": max(0.0, time.time() - self.started_at),
            "memory_usage_mb": self._memory_usage_mb(),
            "cpu_load": self._cpu_load(),
            "vault_statistics": vault_stats,
            "indexed_documents": vault_stats["indexed"],
            "vector_count": vector_count,
            "entity_count": graph_stats["entity_count"],
            "relationship_count": graph_stats["relationship_count"],
            "task_count": task_count,
            "plugin_count": self.plugins.count(),
            "tool_count": self.tools.count(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _memory_usage_mb(self) -> float:
        try:
            import resource

            rss_kb = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            if os.name == "posix":
                return round(rss_kb / 1024.0, 2)
            return round(rss_kb / (1024.0 * 1024.0), 2)
        except Exception:
            return 0.0

    def _cpu_load(self) -> float:
        try:
            return float(os.getloadavg()[0])
        except Exception:
            return 0.0
