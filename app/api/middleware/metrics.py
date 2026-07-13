from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from fastapi import Request


async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        db_path = request.app.state.system.settings.database
        principal = "anonymous"
        if hasattr(request.state, "api_principal"):
            principal = str(getattr(request.state, "api_principal", {}).get("name", "anonymous"))
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO api_requests (request_id, method, path, status_code, principal, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    getattr(request.state, "request_id", ""),
                    request.method,
                    request.url.path,
                    int(response.status_code),
                    principal,
                    datetime.now(UTC).isoformat(),
                ),
            )
            if request.method in {"POST", "PUT", "DELETE"}:
                conn.execute(
                    """
                    INSERT INTO api_audit_log (request_id, action, resource_type, resource_id, principal, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        getattr(request.state, "request_id", ""),
                        request.method,
                        request.url.path,
                        "",
                        principal,
                        "{}",
                        datetime.now(UTC).isoformat(),
                    ),
                )
            conn.commit()
    except Exception:
        pass
    return response
