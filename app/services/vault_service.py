from __future__ import annotations

import sqlite3

from app.services.base_service import BaseService
from app.vault.engine import VaultEngine


class VaultService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.engine = VaultEngine(self.settings)

    def scan(self) -> dict[str, int]:
        return self.engine.full_scan()

    def stats(self) -> dict[str, int]:
        with sqlite3.connect(self.settings.database) as conn:
            files = int(conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] or 0)
            indexed = int(conn.execute("SELECT COUNT(*) FROM files WHERE indexed = 1").fetchone()[0] or 0)
        return {"files": files, "indexed": indexed}
