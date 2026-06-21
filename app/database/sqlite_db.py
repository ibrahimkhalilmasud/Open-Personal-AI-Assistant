from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

FILES_COLUMNS = (
    "id",
    "path",
    "filename",
    "extension",
    "file_size",
    "created_date",
    "modified_date",
    "sha256",
    "indexed",
    "embedding_status",
    "indexed_date",
    "chunk_count",
    "last_scan",
)

REQUIRED_TABLES = (
    "files",
    "folders",
    "conversations",
    "memories",
    "notes",
    "reminders",
    "settings",
    "logs",
    "file_text",
    "file_metadata",
)


def _files_schema_sql() -> str:
    return """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        filename TEXT NOT NULL,
        extension TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        created_date TEXT NOT NULL,
        modified_date TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        indexed INTEGER NOT NULL DEFAULT 0,
        embedding_status TEXT NOT NULL DEFAULT 'pending',
        indexed_date TEXT,
        chunk_count INTEGER NOT NULL DEFAULT 0,
        last_scan TEXT NOT NULL
    )
    """


def _ensure_files_table_schema(conn: sqlite3.Connection) -> None:
    conn.execute(_files_schema_sql())
    existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(files)").fetchall()]

    if "embedding_status" not in existing_columns:
        conn.execute("ALTER TABLE files ADD COLUMN embedding_status TEXT NOT NULL DEFAULT 'pending'")
    if "indexed_date" not in existing_columns:
        conn.execute("ALTER TABLE files ADD COLUMN indexed_date TEXT")
    if "chunk_count" not in existing_columns:
        conn.execute("ALTER TABLE files ADD COLUMN chunk_count INTEGER NOT NULL DEFAULT 0")


def initialize_database(path: str) -> None:
    with sqlite3.connect(path) as conn:
        _ensure_files_table_schema(conn)
        for table in REQUIRED_TABLES:
            if table == "files":
                continue
            if table == "file_text":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS file_text (
                        path TEXT PRIMARY KEY,
                        extracted_text TEXT,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                continue
            if table == "file_metadata":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS file_metadata (
                        path TEXT PRIMARY KEY,
                        metadata_json TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                continue
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )
        conn.commit()


def fetch_file_hashes(path: str) -> dict[str, str]:
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT path, sha256 FROM files").fetchall()
    return {row[0]: row[1] for row in rows}


def fetch_file_row(path: str, file_path: str) -> dict[str, Any] | None:
    with sqlite3.connect(path) as conn:
        row = conn.execute(
            """
            SELECT f.path, f.filename, f.extension, f.sha256, f.embedding_status, f.indexed_date,
                   f.chunk_count, t.extracted_text
            FROM files f
            LEFT JOIN file_text t ON t.path = f.path
            WHERE f.path = ?
            """,
            (file_path,),
        ).fetchone()
    if row is None:
        return None
    return {
        "path": row[0],
        "filename": row[1],
        "extension": row[2],
        "sha256": row[3],
        "embedding_status": row[4],
        "indexed_date": row[5],
        "chunk_count": row[6],
        "extracted_text": row[7] or "",
    }


def fetch_indexable_text_rows(path: str) -> list[dict[str, Any]]:
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT f.path, f.filename, f.extension, f.sha256, f.embedding_status,
                   f.indexed_date, COALESCE(f.chunk_count, 0), COALESCE(t.extracted_text, '')
            FROM files f
            LEFT JOIN file_text t ON t.path = f.path
            WHERE f.indexed = 1
            ORDER BY f.path ASC
            """
        ).fetchall()
    return [
        {
            "path": row[0],
            "filename": row[1],
            "extension": row[2],
            "sha256": row[3],
            "embedding_status": row[4],
            "indexed_date": row[5],
            "chunk_count": int(row[6] or 0),
            "extracted_text": row[7] or "",
        }
        for row in rows
    ]


def update_embedding_status(path: str, file_path: str, status: str, chunk_count: int = 0) -> None:
    indexed_date = datetime.now(UTC).isoformat() if status == "indexed" else None
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            UPDATE files
            SET embedding_status = ?,
                indexed_date = COALESCE(?, indexed_date),
                chunk_count = ?
            WHERE path = ?
            """,
            (status, indexed_date, chunk_count, file_path),
        )
        conn.commit()


def mark_embedding_pending(path: str, file_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            UPDATE files
            SET embedding_status = 'pending',
                indexed_date = NULL,
                chunk_count = 0
            WHERE path = ?
            """,
            (file_path,),
        )
        conn.commit()


def upsert_indexed_file(path: str, file_payload: dict[str, Any]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO files (
                path, filename, extension, file_size, created_date,
                modified_date, sha256, indexed, embedding_status, indexed_date, chunk_count, last_scan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                filename=excluded.filename,
                extension=excluded.extension,
                file_size=excluded.file_size,
                created_date=excluded.created_date,
                modified_date=excluded.modified_date,
                sha256=excluded.sha256,
                indexed=excluded.indexed,
                embedding_status=excluded.embedding_status,
                indexed_date=excluded.indexed_date,
                chunk_count=excluded.chunk_count,
                last_scan=excluded.last_scan
            """,
            (
                file_payload["path"],
                file_payload["filename"],
                file_payload["extension"],
                file_payload["file_size"],
                file_payload["created_date"],
                file_payload["modified_date"],
                file_payload["sha256"],
                file_payload["indexed"],
                file_payload.get("embedding_status", "pending"),
                file_payload.get("indexed_date"),
                int(file_payload.get("chunk_count", 0)),
                file_payload["last_scan"],
            ),
        )

        conn.execute(
            """
            INSERT INTO file_text (path, extracted_text, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                extracted_text=excluded.extracted_text,
                updated_at=excluded.updated_at
            """,
            (
                file_payload["path"],
                file_payload.get("extracted_text", ""),
                file_payload["last_scan"],
            ),
        )

        conn.execute(
            """
            INSERT INTO file_metadata (path, metadata_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                metadata_json=excluded.metadata_json,
                updated_at=excluded.updated_at
            """,
            (
                file_payload["path"],
                json.dumps(file_payload.get("metadata", {}), ensure_ascii=False),
                file_payload["last_scan"],
            ),
        )
        conn.commit()


def keyword_search_rows(path: str, query: str, limit: int = 10) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return []
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT f.path, f.filename, COALESCE(t.extracted_text, '')
            FROM files f
            LEFT JOIN file_text t ON t.path = f.path
            WHERE lower(f.filename) LIKE ? OR lower(COALESCE(t.extracted_text, '')) LIKE ?
            ORDER BY f.path ASC
            LIMIT ?
            """,
            (f"%{q}%", f"%{q}%", max(1, limit)),
        ).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        text = row[2] or ""
        snippet = text[:220] if text else row[1]
        results.append(
            {
                "path": row[0],
                "filename": row[1],
                "text": text,
                "snippet": snippet,
            }
        )
    return results


def remove_file(path: str, file_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM files WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_text WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_metadata WHERE path = ?", (file_path,))
        conn.commit()
