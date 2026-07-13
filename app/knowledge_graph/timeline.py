from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class TimelineEngine:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def add_event(
        self,
        event_date: str,
        event_type: str,
        summary: str,
        source_document: str,
        project_name: str = "",
        entity_name: str = "",
        confidence: float = 0.5,
    ) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO timelines (
                    event_date, event_type, project_name, entity_name,
                    document_path, summary, confidence, source_document, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_date,
                    event_type,
                    project_name,
                    entity_name,
                    source_document,
                    summary,
                    max(0.0, min(1.0, confidence)),
                    source_document,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()

    def query(self, period: str) -> list[dict[str, object]]:
        raw = period.strip()
        if not raw:
            return []
        like = f"{raw}%"
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT event_date, event_type, project_name, entity_name, summary, source_document, confidence
                FROM timelines
                WHERE event_date LIKE ?
                ORDER BY event_date ASC, id ASC
                LIMIT 500
                """,
                (like,),
            ).fetchall()
        return [
            {
                "event_date": str(row[0]),
                "event_type": str(row[1]),
                "project_name": str(row[2] or ""),
                "entity_name": str(row[3] or ""),
                "summary": str(row[4] or ""),
                "source_document": str(row[5] or ""),
                "confidence": float(row[6] or 0.0),
            }
            for row in rows
        ]


__all__ = ["TimelineEngine"]
