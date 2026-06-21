from __future__ import annotations

from pathlib import Path


def keyword_search(files: list[Path], query: str) -> list[Path]:
    q = query.lower().strip()
    if not q:
        return []
    return [path for path in files if q in path.name.lower()]
