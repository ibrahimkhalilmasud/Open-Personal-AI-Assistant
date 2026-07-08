from __future__ import annotations

from app.config.settings import load_settings
from app.search import SearchEngine


class RetrievalEngine:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.search_engine = SearchEngine(self.settings)

    def retrieve(self, query: str, top_k: int = 10) -> list[dict[str, str | float | int]]:
        results = self.search_engine.search(query, top_k=top_k)
        return [
            {
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
            for result in results
        ]


def retrieve(query: str, top_k: int = 10) -> list[dict[str, str | float | int]]:
    engine = RetrievalEngine()
    return engine.retrieve(query=query, top_k=top_k)
