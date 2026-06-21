from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    openai_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    tavily_api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    vault_path: str = ""
    vector_db: str = "data/vector"
    database: str = "data/database.db"
    log_level: str = "INFO"
    default_model: str = "qwen3"
    enable_memory: bool = True
    enable_voice: bool = True
    enable_camera: bool = False
    enable_backups: bool = True
    auto_scan: bool = True
    scan_interval: int = 300
    telegram_token: str = ""
    email_address: str = ""
    email_password: str = ""


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_settings() -> Settings:
    database = os.getenv("DATABASE", "data/database.db")
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    Path(os.getenv("VECTOR_DB", "data/vector")).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        vault_path=os.getenv("VAULT_PATH", ""),
        vector_db=os.getenv("VECTOR_DB", "data/vector"),
        database=database,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_model=os.getenv("DEFAULT_MODEL", "qwen3"),
        enable_memory=_to_bool(os.getenv("ENABLE_MEMORY"), True),
        enable_voice=_to_bool(os.getenv("ENABLE_VOICE"), True),
        enable_camera=_to_bool(os.getenv("ENABLE_CAMERA"), False),
        enable_backups=_to_bool(os.getenv("ENABLE_BACKUPS"), True),
        auto_scan=_to_bool(os.getenv("AUTO_SCAN"), True),
        scan_interval=_to_int(os.getenv("SCAN_INTERVAL"), 300),
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        email_address=os.getenv("EMAIL_ADDRESS", ""),
        email_password=os.getenv("EMAIL_PASSWORD", ""),
    )
