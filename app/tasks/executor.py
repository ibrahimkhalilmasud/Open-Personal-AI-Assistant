from __future__ import annotations

from app.agents.executor import AgentExecutor
from app.agents.result import AgentResult
from app.tasks.history import TaskHistoryStore
from app.tasks.models import FAILED, RUNNING
from app.tasks.queue import TaskQueue


class TaskExecutionEngine:
    def __init__(self, queue: TaskQueue, agent_executor: AgentExecutor, history_store: TaskHistoryStore) -> None:
        self.queue = queue
        self.agent_executor = agent_executor
        self.history_store = history_store

    def execute(self, approve_pending: bool = False) -> list[AgentResult]:
        if approve_pending:
            self.queue.approve_pending()

        results: list[AgentResult] = []
        while True:
            ready_tasks = self.queue.next_ready_tasks()
            if not ready_tasks:
                break

            for task in ready_tasks:
                task.status = RUNNING
                self.queue.update_task(task)
                self.history_store.record(task.task_id, RUNNING, "Task execution started.")

                result = self.agent_executor.execute(task, workflow=task.workflow or None)
                results.append(result)

                task.result = result.to_dict()
                task.confidence = result.confidence
                task.citations = result.citations
                task.execution_log = list(task.execution_log) + [
                    {"at": result.finished_at, "message": result.summary}
                ]
                if result.success:
                    task.status = "completed"
                    self.history_store.record(task.task_id, "completed", result.summary)
                else:
                    task.status = FAILED
                    task.retries += 1
                    error_code = result.error.get("code") if result.error else "UNKNOWN"
                    self.history_store.record(task.task_id, FAILED, f"Execution failed: {error_code}")
                self.queue.update_task(task)

        return results
