from __future__ import annotations

from app.agents.registry import AgentRegistry
from app.services.base_service import BaseService
from app.tasks.queue import TaskQueue
from app.workflows.engine import WorkflowEngine
from app.workflows.registry import WorkflowRegistry


class WorkflowService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.registry = WorkflowRegistry()
        self.agent_registry = AgentRegistry()
        self.agent_registry.discover()
        self.queue = TaskQueue(self.settings.database)
        self.engine = WorkflowEngine(self.registry, self.agent_registry, self.queue)

    def list_workflows(self) -> list[str]:
        return self.registry.list_workflows()

    def get_workflow(self, name: str) -> list[str] | None:
        return self.registry.get_workflow(name)

    def create_tasks(self, name: str, requested_by: str = "api") -> list[dict[str, object]]:
        tasks = self.engine.create_workflow_tasks(name, requested_by=requested_by)
        return [task.to_dict() for task in tasks]
