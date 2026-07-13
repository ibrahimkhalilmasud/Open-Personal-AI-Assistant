from __future__ import annotations

from app.rag import RAGEngine
from app.services.base_service import BaseService


class RAGService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self._engine: RAGEngine | None = None

    @property
    def engine(self) -> RAGEngine:
        if self._engine is None:
            self._engine = RAGEngine(self.system.settings, self.system.router)
        return self._engine

    def ask(self, question: str, model: str | None = None, stream: bool = False) -> dict[str, object]:
        return self.engine.ask(question=question, model=model, stream=stream)
