from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import asdict
from typing import Any

from app.agents.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def discover(self) -> None:
        import app.agents as agents_pkg

        for module_info in pkgutil.iter_modules(agents_pkg.__path__):
            if module_info.name in {"base_agent", "registry", "executor", "context", "history", "result"}:
                continue
            module = importlib.import_module(f"app.agents.{module_info.name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj is BaseAgent or not issubclass(obj, BaseAgent):
                    continue
                instance = obj()
                self.register(instance)

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def list_agents(self) -> list[dict[str, Any]]:
        return [asdict(agent.descriptor()) for agent in sorted(self._agents.values(), key=lambda item: item.name)]

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)
