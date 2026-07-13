from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class ProjectMemory:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def detect_name(self, source_path: str) -> str:
        parent = Path(source_path).parent.name.strip()
        return parent or "General"

    def upsert(
        self,
        name: str,
        related_files: list[str],
        related_people: list[str],
        related_conversations: list[str],
        summary: str,
        confidence: float,
        source_document: str,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            existing = conn.execute(
                "SELECT related_files_json, related_people_json, related_conversations_json FROM projects WHERE name = ?",
                (name,),
            ).fetchone()

            current_files = set(json.loads(existing[0])) if existing else set()
            current_people = set(json.loads(existing[1])) if existing else set()
            current_conversations = set(json.loads(existing[2])) if existing else set()

            merged_files = sorted(current_files.union(related_files))
            merged_people = sorted(current_people.union(related_people))
            merged_conversations = sorted(current_conversations.union(related_conversations))

            conn.execute(
                """
                INSERT INTO projects (
                    name, related_files_json, related_people_json, related_conversations_json,
                    summary, confidence, source_document, memory_version, updated_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    related_files_json=excluded.related_files_json,
                    related_people_json=excluded.related_people_json,
                    related_conversations_json=excluded.related_conversations_json,
                    summary=excluded.summary,
                    confidence=MAX(projects.confidence, excluded.confidence),
                    source_document=CASE WHEN excluded.source_document != '' THEN excluded.source_document ELSE projects.source_document END,
                    updated_at=excluded.updated_at
                """,
                (
                    name,
                    json.dumps(merged_files, ensure_ascii=False),
                    json.dumps(merged_people, ensure_ascii=False),
                    json.dumps(merged_conversations, ensure_ascii=False),
                    summary,
                    max(0.0, min(1.0, confidence)),
                    source_document,
                    now,
                    now,
                ),
            )
            conn.commit()

    def get(self, name: str) -> dict[str, object] | None:
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT name, related_files_json, related_people_json, related_conversations_json, summary, confidence, source_document, updated_at FROM projects WHERE lower(name)=lower(?)",
                (name,),
            ).fetchone()
        if row is None:
            return None
        return {
            "name": str(row[0]),
            "related_files": json.loads(row[1] or "[]"),
            "related_people": json.loads(row[2] or "[]"),
            "related_conversations": json.loads(row[3] or "[]"),
            "summary": str(row[4] or ""),
            "confidence": float(row[5] or 0.0),
            "source_document": str(row[6] or ""),
            "updated_at": str(row[7]),
        }

    def search(self, query: str) -> list[dict[str, object]]:
        q = query.strip().lower()
        if not q:
            return []
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT name, summary, confidence, source_document, updated_at FROM projects WHERE lower(name) LIKE ? OR lower(summary) LIKE ? ORDER BY updated_at DESC",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        return [
            {
                "name": str(row[0]),
                "summary": str(row[1] or ""),
                "confidence": float(row[2] or 0.0),
                "source_document": str(row[3] or ""),
                "updated_at": str(row[4]),
            }
            for row in rows
        ]


__all__ = ["ProjectMemory"]
