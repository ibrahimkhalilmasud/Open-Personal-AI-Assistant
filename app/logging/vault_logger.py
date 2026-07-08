from __future__ import annotations

from app.logging.central import get_logger


def get_file_logger(name: str, filename: str):
    return get_logger(name, filename)
