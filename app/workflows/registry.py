from __future__ import annotations

from app.workflows.templates import WORKFLOW_TEMPLATES


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows = dict(WORKFLOW_TEMPLATES)

    def register(self, name: str, ordered_tasks: list[str]) -> None:
        self._workflows[name] = list(ordered_tasks)

    def unregister(self, name: str) -> None:
        self._workflows.pop(name, None)

    def list_workflows(self) -> list[str]:
        return sorted(self._workflows.keys())

    def get_workflow(self, name: str) -> list[str] | None:
        workflow = self._workflows.get(name)
        if workflow is None:
            return None
        return list(workflow)
