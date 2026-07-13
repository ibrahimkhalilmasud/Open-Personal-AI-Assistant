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
    "index_signature",
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
    "entities",
    "relationships",
    "projects",
    "timelines",
    "preferences",
    "conversation_memory",
    "knowledge_memory",
    "summary_cache",
    "memory_processing_state",
    "tools",
    "tool_history",
    "plugins",
    "plugin_history",
    "permissions",
    "tool_metrics",
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
        index_signature TEXT NOT NULL DEFAULT '',
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
    if "index_signature" not in existing_columns:
        conn.execute("ALTER TABLE files ADD COLUMN index_signature TEXT NOT NULL DEFAULT ''")


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
            if table == "entities":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        canonical_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        aliases_json TEXT NOT NULL DEFAULT '[]',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL DEFAULT '',
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        first_seen_at TEXT NOT NULL,
                        last_seen_at TEXT NOT NULL,
                        UNIQUE(canonical_name, entity_type)
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(canonical_name, entity_type)"
                )
                continue
            if table == "relationships":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_entity_id INTEGER NOT NULL,
                        target_entity_id INTEGER NOT NULL,
                        relationship_type TEXT NOT NULL,
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL DEFAULT '',
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL,
                        UNIQUE(source_entity_id, target_entity_id, relationship_type, source_document),
                        FOREIGN KEY(source_entity_id) REFERENCES entities(id),
                        FOREIGN KEY(target_entity_id) REFERENCES entities(id)
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_entity_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_entity_id)"
                )
                continue
            if table == "projects":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        related_files_json TEXT NOT NULL DEFAULT '[]',
                        related_people_json TEXT NOT NULL DEFAULT '[]',
                        related_conversations_json TEXT NOT NULL DEFAULT '[]',
                        summary TEXT NOT NULL DEFAULT '',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL DEFAULT '',
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        updated_at TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")
                continue
            if table == "timelines":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS timelines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_date TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        project_name TEXT NOT NULL DEFAULT '',
                        entity_name TEXT NOT NULL DEFAULT '',
                        conversation_id INTEGER,
                        document_path TEXT NOT NULL DEFAULT '',
                        summary TEXT NOT NULL DEFAULT '',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timelines_date ON timelines(event_date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timelines_project ON timelines(project_name)")
                continue
            if table == "preferences":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        preference_key TEXT NOT NULL UNIQUE,
                        preference_value TEXT NOT NULL,
                        confidence REAL NOT NULL DEFAULT 0.8,
                        source_document TEXT NOT NULL DEFAULT '',
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        updated_at TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                continue
            if table == "conversation_memory":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        referenced_documents TEXT NOT NULL DEFAULT '[]',
                        ai_provider TEXT NOT NULL DEFAULT '',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL DEFAULT '',
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        timestamp TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversation_memory_timestamp ON conversation_memory(timestamp)"
                )
                continue
            if table == "knowledge_memory":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS knowledge_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fact TEXT NOT NULL,
                        entity_name TEXT NOT NULL DEFAULT '',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        source_document TEXT NOT NULL,
                        memory_version INTEGER NOT NULL DEFAULT 1,
                        timestamp TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_fact ON knowledge_memory(fact)")
                continue
            if table == "summary_cache":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS summary_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        summary_type TEXT NOT NULL,
                        subject_key TEXT NOT NULL,
                        summary_text TEXT NOT NULL,
                        source_signature TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(summary_type, subject_key)
                    )
                    """
                )
                continue
            if table == "memory_processing_state":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memory_processing_state (
                        file_path TEXT PRIMARY KEY,
                        signature TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                continue
            if table == "tools":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tools (
                        tool_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        author TEXT NOT NULL,
                        permissions_json TEXT NOT NULL,
                        input_schema_json TEXT NOT NULL,
                        output_schema_json TEXT NOT NULL,
                        is_builtin INTEGER NOT NULL DEFAULT 1,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                continue
            if table == "tool_history":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tool_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_id TEXT NOT NULL UNIQUE,
                        tool_id TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        workflow_name TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        finish_time TEXT NOT NULL,
                        duration REAL NOT NULL,
                        status TEXT NOT NULL,
                        tool_inputs TEXT NOT NULL,
                        tool_outputs TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        citations TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_history_tool ON tool_history(tool_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_history_agent ON tool_history(agent_name)")
                continue
            if table == "plugins":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plugins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        version TEXT NOT NULL,
                        author TEXT NOT NULL,
                        description TEXT NOT NULL,
                        minimum_application_version TEXT NOT NULL,
                        supported_platforms TEXT NOT NULL,
                        supported_agents TEXT NOT NULL,
                        required_permissions TEXT NOT NULL,
                        status TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                continue
            if table == "plugin_history":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plugin_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_name TEXT NOT NULL,
                        action TEXT NOT NULL,
                        status TEXT NOT NULL,
                        message TEXT,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_plugin_history_name ON plugin_history(plugin_name)")
                continue
            if table == "permissions":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        principal TEXT NOT NULL,
                        permission TEXT NOT NULL,
                        granted INTEGER NOT NULL DEFAULT 1,
                        source TEXT NOT NULL DEFAULT 'system',
                        updated_at TEXT NOT NULL,
                        UNIQUE(principal, permission)
                    )
                    """
                )
                continue
            if table == "tool_metrics":
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tool_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_id TEXT NOT NULL UNIQUE,
                        executions INTEGER NOT NULL DEFAULT 0,
                        failures INTEGER NOT NULL DEFAULT 0,
                        avg_duration REAL NOT NULL DEFAULT 0,
                        last_run_at TEXT NOT NULL
                    )
                    """
                )
                continue
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                assigned_agent TEXT NOT NULL,
                dependencies_json TEXT NOT NULL,
                execution_log_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                citations_json TEXT NOT NULL,
                approved INTEGER NOT NULL DEFAULT 0,
                retries INTEGER NOT NULL DEFAULT 0,
                workflow TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                workflow TEXT,
                duration_seconds REAL NOT NULL,
                status TEXT NOT NULL,
                citations_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
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
                   f.chunk_count, f.created_date, f.modified_date, f.index_signature, t.extracted_text
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
        "created_date": row[7],
        "modified_date": row[8],
        "index_signature": row[9] or "",
        "extracted_text": row[10] or "",
    }


def fetch_indexable_text_rows(path: str) -> list[dict[str, Any]]:
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT f.path, f.filename, f.extension, f.sha256, f.embedding_status,
                   f.indexed_date, COALESCE(f.chunk_count, 0), COALESCE(f.created_date, ''),
                   COALESCE(f.modified_date, ''), COALESCE(f.index_signature, ''),
                   COALESCE(t.extracted_text, '')
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
            "created_date": row[7] or "",
            "modified_date": row[8] or "",
            "index_signature": row[9] or "",
            "extracted_text": row[10] or "",
        }
        for row in rows
    ]


def update_embedding_status(
    path: str, file_path: str, status: str, chunk_count: int = 0, index_signature: str | None = None
) -> None:
    indexed_date = datetime.now(UTC).isoformat() if status == "indexed" else None
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            UPDATE files
            SET embedding_status = ?,
                indexed_date = COALESCE(?, indexed_date),
                chunk_count = ?,
                index_signature = COALESCE(?, index_signature)
            WHERE path = ?
            """,
            (status, indexed_date, chunk_count, index_signature, file_path),
        )
        conn.commit()


def mark_embedding_pending(path: str, file_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            UPDATE files
            SET embedding_status = 'pending',
                indexed_date = NULL,
                chunk_count = 0,
                index_signature = ''
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
                modified_date, sha256, indexed, embedding_status, indexed_date, chunk_count, index_signature, last_scan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                index_signature=excluded.index_signature,
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
                file_payload.get("index_signature", ""),
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


def keyword_search_rows(
    path: str,
    query: str,
    limit: int = 10,
    folder: str | None = None,
    file_type: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return []

    filters: list[str] = []
    params: list[Any] = [f"%{q}%", f"%{q}%"]

    if folder:
        filters.append("f.path LIKE ?")
        params.append(f"%{folder}%")
    if file_type:
        normalized = file_type.lower().lstrip(".")
        filters.append("f.extension = ?")
        params.append(normalized)
    if after:
        filters.append("f.modified_date >= ?")
        params.append(after)
    if before:
        filters.append("f.modified_date <= ?")
        params.append(before)

    where_extra = ""
    if filters:
        where_extra = " AND " + " AND ".join(filters)

    params.append(max(1, limit))

    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            f"""
            SELECT f.path, f.filename, f.extension, f.created_date, f.modified_date,
                   COALESCE(t.extracted_text, ''), COALESCE(m.metadata_json, '{{}}')
            FROM files f
            LEFT JOIN file_text t ON t.path = f.path
            LEFT JOIN file_metadata m ON m.path = f.path
            WHERE (lower(f.filename) LIKE ? OR lower(COALESCE(t.extracted_text, '')) LIKE ?)
            {where_extra}
            ORDER BY f.path ASC
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        text = row[5] or ""
        snippet = text[:220] if text else row[1]
        results.append(
            {
                "path": row[0],
                "filename": row[1],
                "file_type": row[2],
                "created_date": row[3],
                "modified_date": row[4],
                "text": text,
                "snippet": snippet,
                "metadata_json": row[6] or "{}",
            }
        )
    return results


def metadata_search_rows(
    path: str,
    query: str,
    limit: int = 10,
    folder: str | None = None,
    file_type: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return []

    filters: list[str] = []
    params: list[Any] = [f"%{q}%", f"%{q}%", f"%{q}%"]
    if folder:
        filters.append("f.path LIKE ?")
        params.append(f"%{folder}%")
    if file_type:
        filters.append("f.extension = ?")
        params.append(file_type.lower().lstrip("."))
    if after:
        filters.append("f.modified_date >= ?")
        params.append(after)
    if before:
        filters.append("f.modified_date <= ?")
        params.append(before)
    where_extra = ""
    if filters:
        where_extra = " AND " + " AND ".join(filters)
    params.append(max(1, limit))

    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            f"""
            SELECT f.path, f.filename, f.extension, f.created_date, f.modified_date,
                   COALESCE(m.metadata_json, '{{}}')
            FROM files f
            LEFT JOIN file_metadata m ON m.path = f.path
            WHERE (lower(f.filename) LIKE ? OR lower(f.path) LIKE ? OR lower(COALESCE(m.metadata_json, '')) LIKE ?)
            {where_extra}
            ORDER BY f.path ASC
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()

    return [
        {
            "path": row[0],
            "filename": row[1],
            "file_type": row[2],
            "created_date": row[3],
            "modified_date": row[4],
            "metadata_json": row[5] or "{}",
            "text": "",
            "snippet": row[1],
        }
        for row in rows
    ]


def remove_file(path: str, file_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM files WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_text WHERE path = ?", (file_path,))
        conn.execute("DELETE FROM file_metadata WHERE path = ?", (file_path,))
        conn.commit()
