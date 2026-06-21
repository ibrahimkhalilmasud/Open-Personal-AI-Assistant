from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings
from app.database.sqlite_db import keyword_search_rows
from app.embeddings import EmbeddingEngine
from app.logging.vault_logger import get_file_logger
from app.vector import ChromaEngine


@dataclass(slots=True)
class SearchResult:
    score: float
    filename: str
    path: str
    snippet: str
    text: str


class SearchEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = EmbeddingEngine(settings.embedding_model)
        self.vector_db = ChromaEngine(settings.vector_db)
        self.search_logger = get_file_logger("search", "search.log")

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        q = query.strip()
        if not q:
            self._log_search(q, 0)
            return []

        vector_results = self.vector_db.query(self.embedder.embed_query(q), top_k=top_k)
        keyword_results = keyword_search_rows(self.settings.database, q, limit=top_k)

        merged: dict[str, SearchResult] = {}

        for rank, result in enumerate(vector_results):
            base_score = float(result.score)
            rank_boost = 1.0 - (rank * 0.03)
            merged[result.path] = SearchResult(
                score=max(0.0, base_score * max(0.5, rank_boost)),
                filename=result.filename,
                path=result.path,
                snippet=result.snippet,
                text=result.text,
            )

        for rank, result in enumerate(keyword_results):
            path = str(result["path"])
            keyword_score = max(0.35, 0.85 - (rank * 0.05))
            existing = merged.get(path)
            if existing is None:
                merged[path] = SearchResult(
                    score=keyword_score,
                    filename=str(result["filename"]),
                    path=path,
                    snippet=str(result["snippet"]),
                    text=str(result["text"]),
                )
                continue

            existing.score = min(1.0, existing.score + (keyword_score * 0.35))
            if len(existing.snippet.strip()) < 10:
                existing.snippet = str(result["snippet"])

        ranked = sorted(merged.values(), key=lambda item: item.score, reverse=True)[: max(1, top_k)]
        self._log_search(q, len(ranked))
        return ranked

    def _log_search(self, query: str, result_count: int) -> None:
        self.search_logger.info("query=%s | result_count=%s", query, result_count)


def keyword_search(files: list[Any], query: str) -> list[Any]:
    q = query.lower().strip()
    if not q:
        return []
    return [path for path in files if q in str(getattr(path, "name", path)).lower()]
