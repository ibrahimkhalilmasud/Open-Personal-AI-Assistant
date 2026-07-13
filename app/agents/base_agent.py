from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentDescriptor:
    name: str
    description: str
    version: str
    capabilities: list[str]
    supported_tools: list[str]
    supported_tasks: list[str]


class BaseAgent(ABC):
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    capabilities: list[str] = []
    supported_tools: list[str] = []
    supported_tasks: list[str] = []

    def descriptor(self) -> AgentDescriptor:
        return AgentDescriptor(
            name=self.name,
            description=self.description,
            version=self.version,
            capabilities=list(self.capabilities),
            supported_tools=list(self.supported_tools),
            supported_tasks=list(self.supported_tasks),
        )

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def plan(self, request: str) -> list[str]:
        ...

    @abstractmethod
    def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate(self, payload: dict[str, Any]) -> bool:
        ...

    @abstractmethod
    def summarize(self, payload: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...
