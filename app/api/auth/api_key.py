from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime

from fastapi import Header, HTTPException, Request, status


def hash_api_key(raw_key: str, pepper: str = "open-personal-ai-assistant-api-key-v1") -> str:
    pepper_value = pepper.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", raw_key.encode("utf-8"), pepper_value, 600_000, dklen=32).hex()


def create_api_key(database_path: str, name: str, pepper: str = "open-personal-ai-assistant-api-key-v1") -> str:
    raw_key = f"opa_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(raw_key, pepper=pepper)
    now = datetime.now(UTC).isoformat()
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            INSERT INTO api_keys (key_hash, name, is_active, created_at, last_used_at)
            VALUES (?, ?, 1, ?, NULL)
            """,
            (key_hash, name, now),
        )
        conn.commit()
    return raw_key


def validate_api_key(
    database_path: str,
    raw_key: str,
    pepper: str = "open-personal-ai-assistant-api-key-v1",
) -> dict[str, object] | None:
    if not raw_key.strip():
        return None
    key_hash = hash_api_key(raw_key, pepper=pepper)
    with sqlite3.connect(database_path) as conn:
        row = conn.execute(
            "SELECT id, name, is_active FROM api_keys WHERE key_hash = ?",
            (key_hash,),
        ).fetchone()
        if row is None:
            return None
        if int(row[2]) != 1:
            return None
        conn.execute(
            "UPDATE api_keys SET last_used_at = ? WHERE id = ?",
            (datetime.now(UTC).isoformat(), int(row[0])),
        )
        conn.commit()
    return {"id": int(row[0]), "name": str(row[1])}


async def api_key_auth(request: Request, x_api_key: str | None = Header(default=None)) -> str:
    if request.url.path in {"/", "/docs", "/openapi.json", "/health", "/status", "/metrics"}:
        return "public"

    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    settings = request.app.state.system.settings
    key = validate_api_key(settings.database, x_api_key, pepper=settings.api_key_hash_pepper)
    if key is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    request.state.api_principal = key
    return str(key["name"])
