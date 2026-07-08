from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings
from app.database.sqlite_db import keyword_search_rows, metadata_search_rows
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
    file_type: str
    page: int | str
    chunk_id: str
    created_date: str
    modified_date: str
    source: str


class SearchEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = EmbeddingEngine(settings.embedding_model, batch_size=settings.embed_batch_size)
        self.vector_db = ChromaEngine(settings.vector_db)
        self.search_logger = get_file_logger("search", "search.log")

    def search(
        self,
        query: str,
        top_k: int = 10,
        folder: str | None = None,
        file_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> list[SearchResult]:
        q = query.strip()
        if not q:
            self._log_search(q, 0)
            return []

        vector_results = self.vector_db.query(self.embedder.embed_query(q), top_k=top_k)
        after_value, before_value = self._normalize_date_filters(after, before)
        keyword_results = keyword_search_rows(
            self.settings.database,
            q,
            limit=top_k,
            folder=folder,
            file_type=file_type,
            after=after_value,
            before=before_value,
        )
        metadata_results = metadata_search_rows(
            self.settings.database,
            q,
            limit=top_k,
            folder=folder,
            file_type=file_type,
            after=after_value,
            before=before_value,
        )

        merged: dict[str, SearchResult] = {}

        for rank, result in enumerate(vector_results):
            base_score = float(result.score)
            rank_boost = 1.0 - (rank * 0.03)
            if not self._matches_filters(result.path, result.file_type, folder, file_type):
                continue
            merged[result.path] = SearchResult(
                score=max(0.0, min(1.0, base_score * max(0.5, rank_boost))),
                filename=result.filename,
                path=result.path,
                snippet=result.snippet,
                text=result.text,
                file_type=result.file_type,
                page=result.page,
                chunk_id=result.chunk_id,
                created_date=result.created_date,
                modified_date=result.modified_date,
                source=result.source,
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
                    file_type=str(result.get("file_type", "")),
                    page="",
                    chunk_id="",
                    created_date=str(result.get("created_date", "")),
                    modified_date=str(result.get("modified_date", "")),
                    source=path,
                )
                continue

            existing.score = min(1.0, existing.score + (keyword_score * 0.35))
            if len(existing.snippet.strip()) < 10:
                existing.snippet = str(result["snippet"])

        for rank, result in enumerate(metadata_results):
            path = str(result["path"])
            metadata_score = max(0.25, 0.7 - (rank * 0.04))
            existing = merged.get(path)
            if existing is None:
                merged[path] = SearchResult(
                    score=metadata_score,
                    filename=str(result["filename"]),
                    path=path,
                    snippet=str(result["snippet"]),
                    text=str(result["text"]),
                    file_type=str(result.get("file_type", "")),
                    page="",
                    chunk_id="",
                    created_date=str(result.get("created_date", "")),
                    modified_date=str(result.get("modified_date", "")),
                    source=path,
                )
                continue
            existing.score = min(1.0, existing.score + (metadata_score * 0.2))

        ranked = sorted(merged.values(), key=lambda item: item.score, reverse=True)[: max(1, top_k)]
        self._log_search(q, len(ranked))
        return ranked

    def _log_search(self, query: str, result_count: int) -> None:
        self.search_logger.info("query=%s | result_count=%s", query, result_count)

    def _matches_filters(
        self, path: str, file_type: str, folder: str | None, requested_type: str | None
    ) -> bool:
        if folder and folder.lower() not in path.lower():
            return False
        if requested_type:
            normalized = requested_type.lower().lstrip(".")
            if file_type.lower().lstrip(".") != normalized:
                return False
        return True

    def _normalize_date_filters(self, after: str | None, before: str | None) -> tuple[str | None, str | None]:
        return self._normalize_after(after), self._normalize_before(before)

    def _normalize_after(self, value: str | None) -> str | None:
        if not value:
            return None
        raw = value.strip()
        if len(raw) == 4 and raw.isdigit():
            return f"{raw}-01-01T00:00:00+00:00"
        return raw

    def _normalize_before(self, value: str | None) -> str | None:
        if not value:
            return None
        raw = value.strip()
        if len(raw) == 4 and raw.isdigit():
            return f"{raw}-12-31T23:59:59+00:00"
        return raw


def keyword_search(files: list[Any], query: str) -> list[Any]:
    q = query.lower().strip()
    if not q:
        return []
    return [path for path in files if q in str(getattr(path, "name", path)).lower()]
