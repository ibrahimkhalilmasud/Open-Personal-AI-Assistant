from __future__ import annotations

from app.search import SearchEngine
from app.services.base_service import BaseService


class SearchService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self._engine: SearchEngine | None = None

    @property
    def engine(self) -> SearchEngine:
        if self._engine is None:
            self._engine = SearchEngine(self.settings)
        return self._engine

    def search(
        self,
        query: str,
        top_k: int = 10,
        folder: str | None = None,
        file_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> list[dict[str, object]]:
        results = self.engine.search(
            query=query,
            top_k=max(1, top_k),
            folder=folder,
            file_type=file_type,
            after=after,
            before=before,
        )
        return [
            {
                "score": float(item.score),
                "filename": item.filename,
                "path": item.path,
                "snippet": item.snippet,
                "text": item.text,
                "file_type": item.file_type,
                "page": item.page,
                "chunk_id": item.chunk_id,
                "created_date": item.created_date,
                "modified_date": item.modified_date,
                "source": item.source,
            }
            for item in results
        ]
