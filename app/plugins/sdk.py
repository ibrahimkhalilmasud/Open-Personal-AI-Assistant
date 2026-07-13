from __future__ import annotations

from abc import ABC, abstractmethod

from app.plugins.manifest import PluginManifest
from app.tools.tool_registry import ToolRegistry


class PluginBase(ABC):
    manifest: PluginManifest

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def register_tools(self, registry: ToolRegistry) -> list[str]:
        ...

    @abstractmethod
    def unregister_tools(self, registry: ToolRegistry) -> None:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...
