from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


@dataclass(slots=True)
class Settings:
    openai_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    tavily_api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    vault_path: str = ""
    vector_db: str = "data/vector"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 100
    database: str = "data/database.db"
    log_level: str = "INFO"
    default_model: str = "qwen3"
    enable_memory: bool = True
    enable_voice: bool = True
    enable_camera: bool = False
    enable_backups: bool = True
    auto_scan: bool = True
    scan_interval: int = 300
    embed_batch_size: int = 64
    telegram_token: str = ""
    email_address: str = ""
    email_password: str = ""
    settings_validation_report: str = ""


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


def _load_env_file() -> None:
    env_file = os.getenv("OPA_ENV_FILE", ".env")
    path = Path(env_file)
    if load_dotenv is not None:
        load_dotenv(dotenv_path=env_file, override=False)
        return
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _validate_settings(settings: Settings) -> str:
    warnings: list[str] = []
    errors: list[str] = []

    if settings.chunk_size <= 0:
        errors.append("CHUNK_SIZE must be > 0")
    if settings.chunk_overlap < 0:
        errors.append("CHUNK_OVERLAP must be >= 0")
    if settings.chunk_overlap >= settings.chunk_size:
        errors.append("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
    if settings.embed_batch_size <= 0:
        errors.append("EMBED_BATCH_SIZE must be > 0")
    if settings.scan_interval <= 0:
        warnings.append("SCAN_INTERVAL should be > 0; using defaults is recommended")
    if not settings.vault_path.strip():
        warnings.append("VAULT_PATH is not set; scan/watch/index commands will fail until provided")
    if not settings.embedding_model.strip():
        warnings.append("EMBEDDING_MODEL is empty; fallback defaults may be used")

    status = "ok" if not errors else "error"
    details = []
    if errors:
        details.append("errors=" + "; ".join(errors))
    if warnings:
        details.append("warnings=" + "; ".join(warnings))
    return f"status={status}" + (f" | {' | '.join(details)}" if details else "")


def load_settings() -> Settings:
    _load_env_file()
    database = os.getenv("DATABASE", "data/database.db")
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    Path(os.getenv("VECTOR_DB", "data/vector")).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    settings = Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        vault_path=os.getenv("VAULT_PATH", ""),
        vector_db=os.getenv("VECTOR_DB", "data/vector"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        chunk_size=_to_int(os.getenv("CHUNK_SIZE"), 500),
        chunk_overlap=_to_int(os.getenv("CHUNK_OVERLAP"), 100),
        database=database,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_model=os.getenv("DEFAULT_MODEL", "qwen3"),
        enable_memory=_to_bool(os.getenv("ENABLE_MEMORY"), True),
        enable_voice=_to_bool(os.getenv("ENABLE_VOICE"), True),
        enable_camera=_to_bool(os.getenv("ENABLE_CAMERA"), False),
        enable_backups=_to_bool(os.getenv("ENABLE_BACKUPS"), True),
        auto_scan=_to_bool(os.getenv("AUTO_SCAN"), True),
        scan_interval=_to_int(os.getenv("SCAN_INTERVAL"), 300),
        embed_batch_size=_to_int(os.getenv("EMBED_BATCH_SIZE"), 64),
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        email_address=os.getenv("EMAIL_ADDRESS", ""),
        email_password=os.getenv("EMAIL_PASSWORD", ""),
    )
    settings.settings_validation_report = _validate_settings(settings)
    return settings
