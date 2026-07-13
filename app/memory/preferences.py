from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class PreferenceMemory:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def set(self, key: str, value: str, confidence: float = 0.8, source_document: str = "") -> None:
        cleaned_key = key.strip().lower()
        if not cleaned_key:
            return
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO preferences (
                    preference_key, preference_value, confidence,
                    source_document, memory_version, updated_at, created_at
                ) VALUES (?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(preference_key) DO UPDATE SET
                    preference_value=excluded.preference_value,
                    confidence=MAX(preferences.confidence, excluded.confidence),
                    source_document=CASE WHEN excluded.source_document != '' THEN excluded.source_document ELSE preferences.source_document END,
                    updated_at=excluded.updated_at
                """,
                (cleaned_key, value, max(0.0, min(1.0, confidence)), source_document, now, now),
            )
            conn.commit()

    def all(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT preference_key, preference_value, confidence, source_document, updated_at FROM preferences ORDER BY preference_key ASC"
            ).fetchall()
        return [
            {
                "key": str(row[0]),
                "value": str(row[1]),
                "confidence": float(row[2] or 0.0),
                "source_document": str(row[3] or ""),
                "updated_at": str(row[4]),
            }
            for row in rows
        ]

    def search(self, query: str) -> list[dict[str, object]]:
        q = query.strip().lower()
        if not q:
            return []
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT preference_key, preference_value, confidence, source_document, updated_at
                FROM preferences
                WHERE lower(preference_key) LIKE ? OR lower(preference_value) LIKE ?
                ORDER BY updated_at DESC
                """,
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        return [
            {
                "key": str(row[0]),
                "value": str(row[1]),
                "confidence": float(row[2] or 0.0),
                "source_document": str(row[3] or ""),
                "updated_at": str(row[4]),
            }
            for row in rows
        ]


__all__ = ["PreferenceMemory"]
