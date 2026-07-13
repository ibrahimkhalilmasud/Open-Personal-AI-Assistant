from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime


class EntityStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def upsert(
        self,
        canonical_name: str,
        entity_type: str,
        aliases: list[str],
        confidence: float,
        source_document: str,
    ) -> int:
        now = datetime.now(UTC).isoformat()
        normalized = canonical_name.strip()
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT id, aliases_json, confidence FROM entities WHERE canonical_name = ? AND entity_type = ?",
                (normalized, entity_type),
            ).fetchone()
            if row is None:
                cursor = conn.execute(
                    """
                    INSERT INTO entities (
                        canonical_name, entity_type, aliases_json, confidence,
                        source_document, memory_version, first_seen_at, last_seen_at
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        normalized,
                        entity_type,
                        json.dumps(sorted(set(aliases))),
                        max(0.0, min(1.0, confidence)),
                        source_document,
                        now,
                        now,
                    ),
                )
                conn.commit()
                return int(cursor.lastrowid)

            entity_id = int(row[0])
            existing_aliases = set(json.loads(row[1] or "[]"))
            merged_aliases = sorted(existing_aliases.union(aliases))
            merged_confidence = max(float(row[2] or 0.0), max(0.0, min(1.0, confidence)))
            conn.execute(
                """
                UPDATE entities
                SET aliases_json = ?,
                    confidence = ?,
                    source_document = CASE WHEN source_document = '' THEN ? ELSE source_document END,
                    last_seen_at = ?
                WHERE id = ?
                """,
                (json.dumps(merged_aliases), merged_confidence, source_document, now, entity_id),
            )
            conn.commit()
            return entity_id

    def find(self, query: str, entity_type: str | None = None) -> list[dict[str, object]]:
        q = query.strip().lower()
        if not q:
            return []

        clauses = ["lower(canonical_name) LIKE ?"]
        params: list[object] = [f"%{q}%"]
        if entity_type:
            clauses.append("entity_type = ?")
            params.append(entity_type)

        sql = "SELECT id, canonical_name, entity_type, aliases_json, confidence, source_document FROM entities WHERE " + " AND ".join(
            clauses
        )
        sql += " ORDER BY canonical_name ASC LIMIT 100"
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [
            {
                "id": int(row[0]),
                "name": str(row[1]),
                "type": str(row[2]),
                "aliases": json.loads(row[3] or "[]"),
                "confidence": float(row[4] or 0.0),
                "source_document": str(row[5] or ""),
            }
            for row in rows
        ]


__all__ = ["EntityStore"]
