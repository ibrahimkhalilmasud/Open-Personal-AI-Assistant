from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.config.settings import Settings
from app.memory.memory_engine import MemoryEngine
from app.retrieval.engine import RetrievalEngine


@dataclass(slots=True)
class TaskContext:
    relevant_memories: list[str] = field(default_factory=list)
    related_entities: list[str] = field(default_factory=list)
    project_context: str = ""
    retrieved_documents: list[dict[str, Any]] = field(default_factory=list)
    conversation_context: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relevant_memories": self.relevant_memories,
            "related_entities": self.related_entities,
            "project_context": self.project_context,
            "retrieved_documents": self.retrieved_documents,
            "conversation_context": self.conversation_context,
        }


class ContextEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.memory_engine = MemoryEngine(settings.database)
        try:
            self.retrieval_engine = RetrievalEngine()
        except Exception:
            self.retrieval_engine = None

    def build(self, title: str, description: str, conversation_context: list[str] | None = None) -> TaskContext:
        memories: list[str] = []
        if self.settings.enable_memory:
            try:
                memories = self.memory_engine.get_notes()[:5]
            except Exception:
                memories = []

        retrieved = []
        if self.retrieval_engine is not None:
            try:
                retrieved = self.retrieval_engine.retrieve(description or title, top_k=5)
            except Exception:
                retrieved = []
        entities = sorted({str(item.get("filename", "")).strip() for item in retrieved if item.get("filename")})
        return TaskContext(
            relevant_memories=memories,
            related_entities=entities,
            project_context=f"vault={self.settings.vault_path} default_model={self.settings.default_model}",
            retrieved_documents=retrieved,
            conversation_context=conversation_context or [],
        )
