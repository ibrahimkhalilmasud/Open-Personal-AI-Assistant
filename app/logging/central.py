from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGERS: dict[str, logging.Logger] = {}
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 5


def _build_handler(file_path: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(file_path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    return handler


def get_logger(module_name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
    key = f"{module_name}:{filename}"
    if key in _LOGGERS:
        return _LOGGERS[key]

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"opa.{module_name}")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(_build_handler(logs_dir / filename))

    _LOGGERS[key] = logger
    return logger


def get_application_logger(module_name: str) -> logging.Logger:
    return get_logger(module_name, "application.log")


def get_error_logger(module_name: str) -> logging.Logger:
    return get_logger(module_name, "error.log", level=logging.ERROR)
