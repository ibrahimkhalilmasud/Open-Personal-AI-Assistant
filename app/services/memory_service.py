from __future__ import annotations

from app.knowledge_graph.query import KnowledgeGraphQuery
from app.memory import ConversationMemory, LongTermMemoryEngine, PreferenceMemory, ProjectMemory
from app.services.base_service import BaseService


class MemoryService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.long_term = LongTermMemoryEngine(self.settings.database)
        self.conversations = ConversationMemory(self.settings.database)
        self.preferences = PreferenceMemory(self.settings.database)
        self.projects = ProjectMemory(self.settings.database)
        self.graph = KnowledgeGraphQuery(self.settings.database)

    def refresh(self) -> dict[str, int]:
        return self.long_term.refresh_from_index()

    def overview(self) -> dict[str, object]:
        return {
            "conversations": self.conversations.list_recent(limit=10),
            "preferences": self.preferences.all(),
        }

    def search(self, query: str) -> dict[str, object]:
        return {
            "query": query,
            "conversations": self.conversations.search(query),
            "preferences": self.preferences.search(query),
            "projects": self.projects.search(query),
            "graph": self.graph.related_to(query),
        }

    def add_conversation(
        self,
        question: str,
        answer: str,
        referenced_documents: list[str],
        ai_provider: str,
        confidence: float,
    ) -> None:
        self.conversations.add(
            question=question,
            answer=answer,
            referenced_documents=referenced_documents,
            ai_provider=ai_provider,
            confidence=confidence,
        )

    def set_preference(self, key: str, value: str, confidence: float = 0.8) -> None:
        self.preferences.set(key=key, value=value, confidence=confidence)

    def project(self, name: str) -> dict[str, object]:
        project = self.projects.get(name)
        graph = self.graph.project(name)
        return {"project": project, "graph": graph}

    def person(self, name: str) -> dict[str, object]:
        return self.graph.person(name)
