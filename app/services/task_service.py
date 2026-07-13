from __future__ import annotations

from app.agents.context import ContextEngine
from app.agents.executor import AgentExecutor
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.services.base_service import BaseService
from app.tasks.executor import TaskExecutionEngine
from app.tasks.history import TaskHistoryStore
from app.tasks.queue import TaskQueue
from app.tasks.planner import TaskPlanner


class TaskService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.registry = AgentRegistry()
        self.registry.discover()
        self.queue = TaskQueue(self.settings.database)
        self.planner = TaskPlanner(self.registry)
        self.history = TaskHistoryStore(self.settings.database)
        self.agent_history = AgentHistoryStore(self.settings.database)
        self._executor: TaskExecutionEngine | None = None

    @property
    def executor(self) -> TaskExecutionEngine:
        if self._executor is None:
            self._executor = TaskExecutionEngine(
                self.queue,
                AgentExecutor(self.registry, ContextEngine(self.settings), self.agent_history),
                self.history,
            )
        return self._executor

    def list_agents(self) -> list[dict[str, object]]:
        return self.registry.list_agents()

    def list_tasks(self, status: str | None = None) -> list[dict[str, object]]:
        return [item.to_dict() for item in self.queue.list_tasks(status=status)]

    def plan(self, request: str, requested_by: str = "api", workflow: str = "") -> list[dict[str, object]]:
        tasks = self.planner.plan(request=request, requested_by=requested_by, workflow=workflow)
        self.queue.enqueue_many(tasks)
        return [task.to_dict() for task in tasks]

    def execute(self, approve_pending: bool = True) -> list[dict[str, object]]:
        return [result.to_dict() for result in self.executor.execute(approve_pending=approve_pending)]

    def statuses(self) -> dict[str, int]:
        return self.queue.statuses()
