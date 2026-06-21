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
        last_scan TEXT NOT NULL
    )
    """


def _ensure_files_table_schema(conn: sqlite3.Connection) -> None:
    conn.execute(_files_schema_sql())
    existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(files)").fetchall()]
    if tuple(existing_columns) == FILES_COLUMNS:
        return

    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    conn.execute(f"ALTER TABLE files RENAME TO files_legacy_{timestamp}")
    conn.execute(_files_schema_sql())


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


def upsert_indexed_file(path: str, file_payload: dict[str, Any]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO files (
                path, filename, extension, file_size, created_date,
                modified_date, sha256, indexed, last_scan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                filename=excluded.filename,
                extension=excluded.extension,
                file_size=excluded.file_size,
                created_date=excluded.created_date,
                modified_date=excluded.modified_date,
                sha256=excluded.sha256,
                indexed=excluded.indexed,
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


def remove_file(path: str, file_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM files WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_text WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_metadata WHERE path = ?", (file_path,))
        conn.commit()
