from __future__ import annotations

import sqlite3

from app.knowledge_graph.query import KnowledgeGraphQuery
from app.services.base_service import BaseService


class GraphService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.query = KnowledgeGraphQuery(self.settings.database)

    def related(self, term: str) -> dict[str, object]:
        return self.query.related_to(term)

    def person(self, name: str) -> dict[str, object]:
        return self.query.person(name)

    def project(self, name: str) -> dict[str, object]:
        return self.query.project(name)

    def stats(self) -> dict[str, int]:
        with sqlite3.connect(self.settings.database) as conn:
            entity_count = int(conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0] or 0)
            relationship_count = int(conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0] or 0)
        return {"entity_count": entity_count, "relationship_count": relationship_count}
