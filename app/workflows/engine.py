from __future__ import annotations

import uuid

from app.agents.registry import AgentRegistry
from app.tasks.models import PENDING, Task, now_iso
from app.tasks.queue import TaskQueue
from app.workflows.registry import WorkflowRegistry


class WorkflowEngine:
    def __init__(self, workflow_registry: WorkflowRegistry, agent_registry: AgentRegistry, queue: TaskQueue) -> None:
        self.workflow_registry = workflow_registry
        self.agent_registry = agent_registry
        self.queue = queue

    def create_workflow_tasks(self, workflow_name: str, requested_by: str = "cli") -> list[Task]:
        steps = self.workflow_registry.get_workflow(workflow_name)
        if not steps:
            raise ValueError(f"Workflow '{workflow_name}' is not registered.")

        agents = self.agent_registry.list_agents()
        if not agents:
            raise RuntimeError("No agents are registered.")

        assigned_agent = agents[0]["name"]
        tasks: list[Task] = []
        previous_id = ""
        for index, step in enumerate(steps, start=1):
            task_id = str(uuid.uuid4())
            task = Task(
                task_id=task_id,
                title=f"{workflow_name}: step {index}",
                description=step,
                priority=max(1, len(steps) - index + 1),
                status=PENDING,
                created_at=now_iso(),
                updated_at=now_iso(),
                requested_by=requested_by,
                assigned_agent=assigned_agent,
                dependencies=[previous_id] if previous_id else [],
                execution_log=[{"at": now_iso(), "message": f"Task created from workflow '{workflow_name}'."}],
                result={},
                confidence=0.0,
                citations=[],
                approved=False,
                retries=0,
                workflow=workflow_name,
            )
            tasks.append(task)
            previous_id = task_id

        self.queue.enqueue_many(tasks)
        return tasks
