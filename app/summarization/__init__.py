from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime


class SummaryGenerator:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def get_or_refresh(self, summary_type: str, subject_key: str, source_rows: list[dict[str, object]]) -> str:
        signature = self._signature(source_rows)
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT summary_text, source_signature FROM summary_cache WHERE summary_type = ? AND subject_key = ?",
                (summary_type, subject_key),
            ).fetchone()
            if row is not None and row[1] == signature:
                return str(row[0])

            summary = self._build_summary(summary_type, subject_key, source_rows)
            conn.execute(
                """
                INSERT INTO summary_cache (summary_type, subject_key, summary_text, source_signature, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(summary_type, subject_key) DO UPDATE SET
                    summary_text=excluded.summary_text,
                    source_signature=excluded.source_signature,
                    updated_at=excluded.updated_at
                """,
                (summary_type, subject_key, summary, signature, now),
            )
            conn.commit()
            return summary

    def _build_summary(self, summary_type: str, subject_key: str, source_rows: list[dict[str, object]]) -> str:
        count = len(source_rows)
        docs = sorted({str(item.get("source_document", "")) for item in source_rows if str(item.get("source_document", ""))})
        docs_text = ", ".join(docs[:5]) if docs else "no source documents"
        return f"{summary_type.title()} summary for {subject_key}: {count} supporting records from {docs_text}."

    def _signature(self, source_rows: list[dict[str, object]]) -> str:
        payload = json.dumps(source_rows, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = ["SummaryGenerator"]
