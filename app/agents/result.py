from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class AgentResult:
    task_id: str
    agent_name: str
    status: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    citations: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    duration_seconds: float = 0.0
    error: dict[str, Any] | None = None

    @property
    def success(self) -> bool:
        return self.status == "completed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "summary": self.summary,
            "data": self.data,
            "confidence": self.confidence,
            "citations": self.citations,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }
