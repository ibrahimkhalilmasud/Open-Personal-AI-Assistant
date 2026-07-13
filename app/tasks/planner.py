from __future__ import annotations

import uuid

from app.agents.registry import AgentRegistry
from app.tasks.models import PENDING, Task, now_iso


class TaskPlanner:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def plan(self, request: str, requested_by: str = "cli", workflow: str = "") -> list[Task]:
        planner_agent = self._select_planner_agent()
        steps = planner_agent.plan(request)
        if not steps:
            return []

        tasks: list[Task] = []
        previous_id = ""
        for index, step in enumerate(steps, start=1):
            task_id = str(uuid.uuid4())
            dependencies = [previous_id] if previous_id else []
            task = Task(
                task_id=task_id,
                title=f"Step {index}",
                description=step,
                priority=max(1, len(steps) - index + 1),
                status=PENDING,
                created_at=now_iso(),
                updated_at=now_iso(),
                requested_by=requested_by,
                assigned_agent=planner_agent.name,
                dependencies=dependencies,
                execution_log=[{"at": now_iso(), "message": "Task created from planner output."}],
                result={},
                confidence=0.0,
                citations=[],
                approved=False,
                retries=0,
                workflow=workflow,
            )
            tasks.append(task)
            previous_id = task_id
        return tasks

    def _select_planner_agent(self):
        candidates = [
            self.registry.get_agent(item["name"])
            for item in self.registry.list_agents()
            if "planning" in item.get("capabilities", [])
        ]
        if not candidates or candidates[0] is None:
            raise RuntimeError("No planning-capable agent is registered.")
        return candidates[0]
