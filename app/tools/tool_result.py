from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolResult:
    status: str
    outputs: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    citations: list[str] = field(default_factory=list)
    error_code: str = ""
    error_message: str = ""

    @property
    def success(self) -> bool:
        return self.status == "completed"

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status,
            "outputs": dict(self.outputs),
            "confidence": float(self.confidence),
            "citations": list(self.citations),
        }
        if self.error_code:
            payload["error"] = {
                "code": self.error_code,
                "message": self.error_message,
            }
        return payload

    @classmethod
    def completed(
        cls,
        outputs: dict[str, Any],
        confidence: float = 0.0,
        citations: list[str] | None = None,
    ) -> "ToolResult":
        return cls(
            status="completed",
            outputs=outputs,
            confidence=max(0.0, min(1.0, float(confidence))),
            citations=list(citations or []),
        )

    @classmethod
    def failed(cls, code: str, message: str) -> "ToolResult":
        return cls(status="failed", outputs={}, confidence=0.0, citations=[], error_code=code, error_message=message)
