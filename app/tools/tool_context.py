from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolContext:
    execution_id: str
    agent_name: str
    workflow_name: str = ""
    permissions: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "agent_name": self.agent_name,
            "workflow_name": self.workflow_name,
            "permissions": sorted(self.permissions),
            "metadata": dict(self.metadata),
        }
