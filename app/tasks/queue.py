from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from app.tasks.models import COMPLETED, PENDING, Task


class TaskQueue:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    assigned_agent TEXT NOT NULL,
                    dependencies_json TEXT NOT NULL,
                    execution_log_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    citations_json TEXT NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    retries INTEGER NOT NULL DEFAULT 0,
                    workflow TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.commit()

    def enqueue(self, task: Task) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    task_id, title, description, priority, status, created_at, updated_at, requested_by,
                    assigned_agent, dependencies_json, execution_log_json, result_json, confidence,
                    citations_json, approved, retries, workflow
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                task.to_db_tuple(),
            )
            conn.commit()

    def enqueue_many(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.enqueue(task)

    def get_task(self, task_id: str) -> Task | None:
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                """
                SELECT task_id, title, description, priority, status, created_at, updated_at, requested_by,
                       assigned_agent, dependencies_json, execution_log_json, result_json, confidence,
                       citations_json, approved, retries, workflow
                FROM tasks
                WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return Task.from_db_row(row)

    def list_tasks(self, status: str | None = None) -> list[Task]:
        query = (
            """
            SELECT task_id, title, description, priority, status, created_at, updated_at, requested_by,
                   assigned_agent, dependencies_json, execution_log_json, result_json, confidence,
                   citations_json, approved, retries, workflow
            FROM tasks
            """
        )
        params: tuple[str, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY priority DESC, created_at ASC"
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [Task.from_db_row(row) for row in rows]

    def approve_pending(self) -> int:
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.execute("UPDATE tasks SET approved = 1, updated_at = ? WHERE status = ?", (now_iso(), PENDING))
            conn.commit()
            return cursor.rowcount

    def update_task(self, task: Task) -> None:
        task.updated_at = now_iso()
        self.enqueue(task)

    def next_ready_tasks(self) -> list[Task]:
        pending = [task for task in self.list_tasks(PENDING) if task.approved]
        completed_ids = {task.task_id for task in self.list_tasks(COMPLETED)}
        ready: list[Task] = []
        for task in pending:
            if all(dep in completed_ids for dep in task.dependencies):
                ready.append(task)
        return sorted(ready, key=lambda item: (-item.priority, item.created_at))

    def append_execution_log(self, task_id: str, message: str) -> None:
        task = self.get_task(task_id)
        if task is None:
            return
        logs = list(task.execution_log)
        logs.append({"at": now_iso(), "message": message})
        task.execution_log = logs
        task.updated_at = now_iso()
        self.update_task(task)

    def statuses(self) -> dict[str, int]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status").fetchall()
        return {str(row[0]): int(row[1]) for row in rows}



def now_iso() -> str:
    return datetime.now(UTC).isoformat()
