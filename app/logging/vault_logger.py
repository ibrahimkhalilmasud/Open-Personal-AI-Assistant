from __future__ import annotations

import logging
from pathlib import Path


_LOGGERS: dict[str, logging.Logger] = {}


def get_file_logger(name: str, filename: str) -> logging.Logger:
    key = f"{name}:{filename}"
    if key in _LOGGERS:
        return _LOGGERS[key]

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(key)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(logs_dir / filename)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _LOGGERS[key] = logger
    return logger
