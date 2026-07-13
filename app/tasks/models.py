from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
CANCELLED = "cancelled"


@dataclass(slots=True)
class Task:
    task_id: str
    title: str
    description: str
    priority: int
    status: str
    created_at: str
    updated_at: str
    requested_by: str
    assigned_agent: str
    dependencies: list[str] = field(default_factory=list)
    execution_log: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    citations: list[str] = field(default_factory=list)
    approved: bool = False
    retries: int = 0
    workflow: str = ""

    def to_db_tuple(self) -> tuple[Any, ...]:
        return (
            self.task_id,
            self.title,
            self.description,
            int(self.priority),
            self.status,
            self.created_at,
            self.updated_at,
            self.requested_by,
            self.assigned_agent,
            json.dumps(self.dependencies, ensure_ascii=False),
            json.dumps(self.execution_log, ensure_ascii=False),
            json.dumps(self.result, ensure_ascii=False),
            float(self.confidence),
            json.dumps(self.citations, ensure_ascii=False),
            1 if self.approved else 0,
            int(self.retries),
            self.workflow,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "requested_by": self.requested_by,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "execution_log": self.execution_log,
            "result": self.result,
            "confidence": self.confidence,
            "citations": self.citations,
            "approved": self.approved,
            "retries": self.retries,
            "workflow": self.workflow,
        }

    @classmethod
    def from_db_row(cls, row: tuple[Any, ...]) -> "Task":
        return cls(
            task_id=row[0],
            title=row[1],
            description=row[2],
            priority=int(row[3]),
            status=row[4],
            created_at=row[5],
            updated_at=row[6],
            requested_by=row[7],
            assigned_agent=row[8],
            dependencies=json.loads(row[9] or "[]"),
            execution_log=json.loads(row[10] or "[]"),
            result=json.loads(row[11] or "{}"),
            confidence=float(row[12] or 0.0),
            citations=json.loads(row[13] or "[]"),
            approved=bool(row[14]),
            retries=int(row[15] or 0),
            workflow=row[16] or "",
        )


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
