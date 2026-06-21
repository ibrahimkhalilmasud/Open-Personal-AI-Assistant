from __future__ import annotations

from app.config.settings import load_settings
from app.search import SearchEngine


class RetrievalEngine:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.search_engine = SearchEngine(self.settings)

    def retrieve(self, query: str, top_k: int = 10) -> list[dict[str, str | float]]:
        results = self.search_engine.search(query, top_k=top_k)
        return [
            {
                "text": result.text,
                "source": result.path,
                "score": float(result.score),
            }
            for result in results
        ]


def retrieve(query: str, top_k: int = 10) -> list[dict[str, str | float]]:
    engine = RetrievalEngine()
    return engine.retrieve(query=query, top_k=top_k)
