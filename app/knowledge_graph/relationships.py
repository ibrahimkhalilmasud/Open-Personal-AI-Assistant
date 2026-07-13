from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class RelationshipStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def upsert(
        self,
        source_entity_id: int,
        target_entity_id: int,
        relationship_type: str,
        confidence: float,
        source_document: str,
    ) -> None:
        if source_entity_id == target_entity_id:
            return
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO relationships (
                    source_entity_id, target_entity_id, relationship_type, confidence,
                    source_document, memory_version, created_at
                ) VALUES (?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(source_entity_id, target_entity_id, relationship_type, source_document)
                DO UPDATE SET confidence = MAX(relationships.confidence, excluded.confidence)
                """,
                (
                    source_entity_id,
                    target_entity_id,
                    relationship_type,
                    max(0.0, min(1.0, confidence)),
                    source_document,
                    now,
                ),
            )
            conn.commit()

    def connected_to_entity_ids(self, entity_ids: list[int]) -> list[dict[str, object]]:
        if not entity_ids:
            return []
        placeholders = ",".join(["?"] * len(entity_ids))
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                f"""
                SELECT r.relationship_type, r.confidence, r.source_document,
                       e1.canonical_name, e1.entity_type,
                       e2.canonical_name, e2.entity_type
                FROM relationships r
                JOIN entities e1 ON e1.id = r.source_entity_id
                JOIN entities e2 ON e2.id = r.target_entity_id
                WHERE r.source_entity_id IN ({placeholders}) OR r.target_entity_id IN ({placeholders})
                ORDER BY r.id DESC
                LIMIT 300
                """,
                tuple(entity_ids + entity_ids),
            ).fetchall()

        return [
            {
                "relationship_type": str(row[0]),
                "confidence": float(row[1] or 0.0),
                "source_document": str(row[2] or ""),
                "source": {"name": str(row[3]), "type": str(row[4])},
                "target": {"name": str(row[5]), "type": str(row[6])},
            }
            for row in rows
        ]


__all__ = ["RelationshipStore"]
