from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime


class ConversationMemory:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def add(
        self,
        question: str,
        answer: str,
        referenced_documents: list[str],
        ai_provider: str,
        confidence: float,
        source_document: str = "",
    ) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO conversation_memory (
                    question, answer, referenced_documents, ai_provider,
                    confidence, source_document, memory_version, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    question,
                    answer,
                    json.dumps(referenced_documents, ensure_ascii=False),
                    ai_provider,
                    max(0.0, min(1.0, confidence)),
                    source_document,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()

    def list_recent(self, limit: int = 20) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT question, answer, referenced_documents, ai_provider, confidence, source_document, timestamp FROM conversation_memory ORDER BY id DESC LIMIT ?",
                (max(1, limit),),
            ).fetchall()
        return [
            {
                "question": str(row[0]),
                "answer": str(row[1]),
                "referenced_documents": json.loads(row[2] or "[]"),
                "ai_provider": str(row[3]),
                "confidence": float(row[4] or 0.0),
                "source_document": str(row[5] or ""),
                "timestamp": str(row[6]),
            }
            for row in rows
        ]

    def search(self, query: str, limit: int = 50) -> list[dict[str, object]]:
        q = query.strip().lower()
        if not q:
            return []
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT question, answer, referenced_documents, ai_provider, confidence, source_document, timestamp
                FROM conversation_memory
                WHERE lower(question) LIKE ? OR lower(answer) LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (f"%{q}%", f"%{q}%", max(1, limit)),
            ).fetchall()
        return [
            {
                "question": str(row[0]),
                "answer": str(row[1]),
                "referenced_documents": json.loads(row[2] or "[]"),
                "ai_provider": str(row[3]),
                "confidence": float(row[4] or 0.0),
                "source_document": str(row[5] or ""),
                "timestamp": str(row[6]),
            }
            for row in rows
        ]


__all__ = ["ConversationMemory"]
