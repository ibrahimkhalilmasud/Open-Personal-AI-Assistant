from __future__ import annotations

from datetime import UTC, datetime

from app.agents.context import ContextEngine
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.agents.result import AgentResult
from app.tasks.models import Task
from app.tools.tool_executor import ToolExecutor


class AgentExecutor:
    def __init__(
        self,
        registry: AgentRegistry,
        context_engine: ContextEngine,
        history_store: AgentHistoryStore,
        tool_executor: ToolExecutor | None = None,
    ) -> None:
        self.registry = registry
        self.context_engine = context_engine
        self.history_store = history_store
        self.tool_executor = tool_executor

    def execute(self, task: Task, workflow: str | None = None) -> AgentResult:
        started_at = datetime.now(UTC)
        agent = self.registry.get_agent(task.assigned_agent)
        if agent is None:
            return self._error_result(
                task=task,
                started_at=started_at,
                code="AGENT_NOT_FOUND",
                message=f"Assigned agent '{task.assigned_agent}' is not registered.",
            )

        try:
            agent.initialize()
            context = self.context_engine.build(task.title, task.description).to_dict()
            if self.tool_executor is not None:
                context["tool_executor_available"] = True
                context["tool_executor_mode"] = "registry"
            payload = agent.execute(task.to_dict(), context)
            payload = self._apply_tool_chain(task, payload)

            if not self._validate_payload(payload):
                return self._error_result(
                    task=task,
                    started_at=started_at,
                    code="VALIDATION_ERROR",
                    message="Result validation failed: missing required details, citations, or confidence.",
                )

            if not agent.validate(payload):
                return self._error_result(
                    task=task,
                    started_at=started_at,
                    code="AGENT_VALIDATION_FAILED",
                    message="Agent validation failed due to inconsistent output.",
                )

            finished_at = datetime.now(UTC)
            duration = (finished_at - started_at).total_seconds()
            result = AgentResult(
                task_id=task.task_id,
                agent_name=agent.name,
                status="completed",
                summary=agent.summarize(payload),
                data=payload,
                confidence=float(payload.get("confidence", 0.0)),
                citations=list(payload.get("citations", [])),
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
                duration_seconds=duration,
            )
            self.history_store.record(
                task_id=task.task_id,
                agent_name=agent.name,
                workflow=workflow,
                duration_seconds=duration,
                status=result.status,
                citations=result.citations,
            )
            return result

    def _apply_tool_chain(self, task: Task, payload: dict[str, object]) -> dict[str, object]:
            if self.tool_executor is None:
                return payload
            chain = payload.get("tool_chain")
            if not isinstance(chain, list) or not chain:
                return payload

            history = self.tool_executor.execute_chain(
                chain=chain,
                agent_name=task.assigned_agent,
                workflow_name=task.workflow,
                initial_payload={"question": task.description},
            )
            payload = dict(payload)
            payload["tool_history"] = history
            if history and history[-1].get("status") == "completed":
                final_outputs = history[-1].get("tool_outputs", {})
                if isinstance(final_outputs, dict):
                    details = final_outputs.get("summary") or final_outputs.get("answer")
                    if details:
                        payload["details"] = str(details)
                citations: list[str] = []
                for item in history:
                    citations.extend([str(source) for source in item.get("citations", []) if str(source).strip()])
                if citations:
                    payload["citations"] = citations[:10]
                payload["confidence"] = max(
                    float(payload.get("confidence", 0.0)),
                    float(history[-1].get("confidence", 0.0)),
                )
            return payload
        except Exception as exc:
            return self._error_result(
                task=task,
                started_at=started_at,
                code="EXECUTION_ERROR",
                message=str(exc),
            )
        finally:
            try:
                agent.cleanup()
            except Exception:
                pass

    def _validate_payload(self, payload: dict[str, object]) -> bool:
        details = payload.get("details")
        citations = payload.get("citations")
        confidence = payload.get("confidence")
        if not details:
            return False
        if not isinstance(citations, list) or not citations:
            return False
        if confidence is None:
            return False
        score = float(confidence)
        return 0.0 <= score <= 1.0

    def _error_result(self, task: Task, started_at: datetime, code: str, message: str) -> AgentResult:
        finished_at = datetime.now(UTC)
        duration = (finished_at - started_at).total_seconds()
        result = AgentResult(
            task_id=task.task_id,
            agent_name=task.assigned_agent,
            status="failed",
            summary=message,
            confidence=0.0,
            citations=[],
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration_seconds=duration,
            error={"code": code, "message": message},
        )
        self.history_store.record(
            task_id=task.task_id,
            agent_name=task.assigned_agent,
            workflow=None,
            duration_seconds=duration,
            status=result.status,
            citations=[],
        )
        return result
