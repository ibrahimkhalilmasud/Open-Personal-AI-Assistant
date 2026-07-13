from __future__ import annotations

import sqlite3

from app.knowledge_graph.entities import EntityStore
from app.knowledge_graph.relationships import RelationshipStore


class KnowledgeGraphQuery:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.entities = EntityStore(database_path)
        self.relationships = RelationshipStore(database_path)

    def related_to(self, term: str) -> dict[str, object]:
        nodes = self.entities.find(term)
        relationships = self.relationships.connected_to_entity_ids([int(node["id"]) for node in nodes])
        return {"entities": nodes, "relationships": relationships}

    def project(self, project_name: str) -> dict[str, object]:
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT name, related_files_json, related_people_json, related_conversations_json, summary, confidence, source_document FROM projects WHERE lower(name)=lower(?)",
                (project_name,),
            ).fetchone()
        if row is None:
            return {"project": None, "relationships": []}
        graph = self.related_to(str(row[0]))
        return {
            "project": {
                "name": str(row[0]),
                "related_files_json": str(row[1]),
                "related_people_json": str(row[2]),
                "related_conversations_json": str(row[3]),
                "summary": str(row[4]),
                "confidence": float(row[5] or 0.0),
                "source_document": str(row[6] or ""),
            },
            "relationships": graph["relationships"],
            "entities": graph["entities"],
        }

    def person(self, person_name: str) -> dict[str, object]:
        nodes = self.entities.find(person_name, entity_type="person")
        relationships = self.relationships.connected_to_entity_ids([int(node["id"]) for node in nodes])
        with sqlite3.connect(self.database_path) as conn:
            facts = conn.execute(
                "SELECT fact, confidence, source_document, timestamp FROM knowledge_memory WHERE lower(entity_name) LIKE lower(?) ORDER BY id DESC LIMIT 100",
                (f"%{person_name}%",),
            ).fetchall()
        return {
            "entities": nodes,
            "relationships": relationships,
            "facts": [
                {
                    "fact": str(row[0]),
                    "confidence": float(row[1] or 0.0),
                    "source_document": str(row[2] or ""),
                    "timestamp": str(row[3]),
                }
                for row in facts
            ],
        }


__all__ = ["KnowledgeGraphQuery"]
