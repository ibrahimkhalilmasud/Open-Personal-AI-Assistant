from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime


class PermissionLevels:
    READ_VAULT = "read_vault"
    WRITE_VAULT = "write_vault"
    DELETE_FILES = "delete_files"
    INTERNET_ACCESS = "internet_access"
    EXECUTE_COMMANDS = "execute_commands"
    EXTERNAL_API_ACCESS = "external_api_access"


@dataclass(slots=True)
class PermissionCheckResult:
    allowed: bool
    missing_permissions: list[str]


class ToolPermissionManager:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
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
            conn.commit()

    def grant(self, principal: str, permission: str, source: str = "system") -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO permissions (principal, permission, granted, source, updated_at)
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(principal, permission) DO UPDATE SET
                    granted=excluded.granted,
                    source=excluded.source,
                    updated_at=excluded.updated_at
                """,
                (principal, permission, source, now),
            )
            conn.commit()

    def revoke(self, principal: str, permission: str, source: str = "system") -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO permissions (principal, permission, granted, source, updated_at)
                VALUES (?, ?, 0, ?, ?)
                ON CONFLICT(principal, permission) DO UPDATE SET
                    granted=excluded.granted,
                    source=excluded.source,
                    updated_at=excluded.updated_at
                """,
                (principal, permission, source, now),
            )
            conn.commit()

    def allowed_permissions(self, principal: str) -> set[str]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT permission FROM permissions WHERE principal = ? AND granted = 1",
                (principal,),
            ).fetchall()
        return {str(row[0]) for row in rows}

    def validate(self, principal: str, required_permissions: list[str]) -> PermissionCheckResult:
        allowed = self.allowed_permissions(principal)
        missing = sorted({perm for perm in required_permissions if perm not in allowed})
        return PermissionCheckResult(allowed=not missing, missing_permissions=missing)
