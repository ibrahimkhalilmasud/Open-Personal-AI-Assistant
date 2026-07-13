from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from app.tools.tool_context import ToolContext
from app.tools.tool_permissions import ToolPermissionManager
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_result import ToolResult


class ToolExecutor:
    def __init__(self, database_path: str, registry: ToolRegistry, permission_manager: ToolPermissionManager) -> None:
        self.database_path = database_path
        self.registry = registry
        self.permission_manager = permission_manager
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT NOT NULL UNIQUE,
                    tool_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    finish_time TEXT NOT NULL,
                    duration REAL NOT NULL,
                    status TEXT NOT NULL,
                    tool_inputs TEXT NOT NULL,
                    tool_outputs TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    citations TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id TEXT NOT NULL,
                    executions INTEGER NOT NULL DEFAULT 0,
                    failures INTEGER NOT NULL DEFAULT 0,
                    avg_duration REAL NOT NULL DEFAULT 0,
                    last_run_at TEXT NOT NULL,
                    UNIQUE(tool_id)
                )
                """
            )
            conn.commit()

    def execute(
        self,
        tool_name_or_id: str,
        inputs: dict[str, Any],
        *,
        agent_name: str,
        workflow_name: str = "",
    ) -> dict[str, Any]:
        execution_id = str(uuid.uuid4())
        started_at = datetime.now(UTC)
        tool = self.registry.get_tool(tool_name_or_id)
        if tool is None:
            result = ToolResult.failed("TOOL_NOT_FOUND", f"Tool '{tool_name_or_id}' is not registered.")
            return self._finalize(tool_name_or_id, execution_id, agent_name, workflow_name, inputs, started_at, result)

        permission_check = self.permission_manager.validate(agent_name, tool.permissions)
        if not permission_check.allowed:
            result = ToolResult.failed(
                "PERMISSION_DENIED",
                f"Missing permissions: {', '.join(permission_check.missing_permissions)}",
            )
            return self._finalize(tool.tool_id, execution_id, agent_name, workflow_name, inputs, started_at, result)

        context = ToolContext(
            execution_id=execution_id,
            agent_name=agent_name,
            workflow_name=workflow_name,
            permissions=set(self.permission_manager.allowed_permissions(agent_name)),
        )

        validation = tool.validate(inputs, context)
        if not validation.valid:
            result = ToolResult.failed(
                "VALIDATION_ERROR",
                "; ".join(error.message for error in validation.errors),
            )
            return self._finalize(tool.tool_id, execution_id, agent_name, workflow_name, inputs, started_at, result)

        try:
            tool.initialize(context)
            result = tool.execute(inputs, context)
        except Exception as exc:
            result = ToolResult.failed("EXECUTION_ERROR", str(exc))
        finally:
            try:
                tool.cleanup(context)
            except Exception:
                pass

        return self._finalize(tool.tool_id, execution_id, agent_name, workflow_name, inputs, started_at, result)

    def execute_chain(
        self,
        chain: list[dict[str, Any]],
        *,
        agent_name: str,
        workflow_name: str = "",
        initial_payload: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        payload = dict(initial_payload or {})
        history: list[dict[str, Any]] = []

        for step in chain:
            tool_name = str(step.get("tool", "")).strip()
            step_inputs = dict(step.get("inputs", {}))
            for key, value in list(step_inputs.items()):
                if isinstance(value, str) and value.startswith("$"):
                    step_inputs[key] = payload.get(value[1:], "")
            execution = self.execute(tool_name, step_inputs, agent_name=agent_name, workflow_name=workflow_name)
            history.append(execution)
            if execution.get("status") != "completed":
                break
            payload.update(execution.get("tool_outputs", {}))
        return history

    def _finalize(
        self,
        tool_id: str,
        execution_id: str,
        agent_name: str,
        workflow_name: str,
        inputs: dict[str, Any],
        started_at: datetime,
        result: ToolResult,
    ) -> dict[str, Any]:
        finished_at = datetime.now(UTC)
        duration = (finished_at - started_at).total_seconds()
        payload = {
            "execution_id": execution_id,
            "tool_id": tool_id,
            "agent_name": agent_name,
            "workflow_name": workflow_name,
            "start_time": started_at.isoformat(),
            "finish_time": finished_at.isoformat(),
            "duration": duration,
            "status": result.status,
            "tool_inputs": dict(inputs),
            "tool_outputs": dict(result.outputs),
            "confidence": float(result.confidence),
            "citations": list(result.citations),
        }
        if result.error_code:
            payload["error"] = {"code": result.error_code, "message": result.error_message}

        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO tool_history (
                    execution_id, tool_id, agent_name, workflow_name, start_time, finish_time,
                    duration, status, tool_inputs, tool_outputs, confidence, citations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["execution_id"],
                    payload["tool_id"],
                    payload["agent_name"],
                    payload["workflow_name"],
                    payload["start_time"],
                    payload["finish_time"],
                    payload["duration"],
                    payload["status"],
                    json.dumps(payload["tool_inputs"], ensure_ascii=False),
                    json.dumps(payload["tool_outputs"], ensure_ascii=False),
                    payload["confidence"],
                    json.dumps(payload["citations"], ensure_ascii=False),
                ),
            )
            self._update_metrics(conn, tool_id, duration, result.status == "failed")
            conn.commit()
        return payload

    def _update_metrics(self, conn: sqlite3.Connection, tool_id: str, duration: float, failed: bool) -> None:
        row = conn.execute(
            "SELECT executions, failures, avg_duration FROM tool_metrics WHERE tool_id = ?",
            (tool_id,),
        ).fetchone()
        now = datetime.now(UTC).isoformat()
        if row is None:
            conn.execute(
                """
                INSERT INTO tool_metrics (tool_id, executions, failures, avg_duration, last_run_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tool_id, 1, 1 if failed else 0, float(duration), now),
            )
            return

        executions = int(row[0]) + 1
        failures = int(row[1]) + (1 if failed else 0)
        avg_duration = ((float(row[2]) * int(row[0])) + duration) / executions
        conn.execute(
            """
            UPDATE tool_metrics
            SET executions = ?, failures = ?, avg_duration = ?, last_run_at = ?
            WHERE tool_id = ?
            """,
            (executions, failures, avg_duration, now, tool_id),
        )

    def list_history(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT execution_id, tool_id, agent_name, workflow_name, start_time, finish_time,
                       duration, status, tool_inputs, tool_outputs, confidence, citations
                FROM tool_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (max(1, limit),),
            ).fetchall()
        return [
            {
                "execution_id": row[0],
                "tool_id": row[1],
                "agent_name": row[2],
                "workflow_name": row[3],
                "start_time": row[4],
                "finish_time": row[5],
                "duration": float(row[6]),
                "status": row[7],
                "tool_inputs": json.loads(row[8] or "{}"),
                "tool_outputs": json.loads(row[9] or "{}"),
                "confidence": float(row[10] or 0.0),
                "citations": json.loads(row[11] or "[]"),
            }
            for row in rows
        ]
