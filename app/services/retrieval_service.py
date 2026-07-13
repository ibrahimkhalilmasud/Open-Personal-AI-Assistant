from __future__ import annotations

from app.retrieval import RetrievalEngine
from app.services.base_service import BaseService


class RetrievalService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self._engine: RetrievalEngine | None = None

    @property
    def engine(self) -> RetrievalEngine:
        if self._engine is None:
            self._engine = RetrievalEngine()
        return self._engine

    def retrieve(self, query: str, top_k: int = 10) -> list[dict[str, object]]:
        return self.engine.retrieve(query=query, top_k=max(1, top_k))
