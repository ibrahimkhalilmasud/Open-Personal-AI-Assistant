from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings
from app.search import SearchEngine


@dataclass(slots=True)
class RetrievalOutput:
    results: list[dict[str, object]]


class HybridRetriever:
    def __init__(self, settings: Settings) -> None:
        self.search_engine = SearchEngine(settings)

    def retrieve(
        self,
        query_terms: list[str],
        *,
        top_k: int,
        folder: str | None = None,
        file_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> RetrievalOutput:
        merged: dict[str, dict[str, object]] = {}

        for term in query_terms:
            for result in self.search_engine.search(
                term,
                top_k=top_k,
                folder=folder,
                file_type=file_type,
                after=after,
                before=before,
            ):
                key = f"{result.path}|{result.chunk_id}|{result.snippet[:40]}"
                existing = merged.get(key)
                candidate = {
                    "filename": result.filename,
                    "path": result.path,
                    "file_type": result.file_type,
                    "page": result.page,
                    "chunk_id": result.chunk_id,
                    "created_date": result.created_date,
                    "modified_date": result.modified_date,
                    "score": max(0.0, min(1.0, float(result.score))),
                    "text": result.text,
                    "source": result.source,
                }
                if existing is None or float(candidate["score"]) > float(existing["score"]):
                    merged[key] = candidate

        ranked = sorted(merged.values(), key=lambda item: float(item["score"]), reverse=True)
        return RetrievalOutput(results=ranked[: max(1, top_k)])
