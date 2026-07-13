from __future__ import annotations

import re
from typing import Any

from app.agents.base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    name = "planning-agent"
    description = "Builds and executes structured step-by-step plans"
    version = "1.0.0"
    capabilities = ["planning", "sequential_execution", "validation", "summarization"]
    supported_tools = ["memory", "retrieval", "search", "sqlite"]
    supported_tasks = ["research", "travel", "document_analysis", "project_summary", "insurance_review"]

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def plan(self, request: str) -> list[str]:
        lowered = request.lower()
        destination = self._extract_destination(request)
        if "trip" in lowered or "travel" in lowered:
            return [
                "Find passport.",
                "Check passport expiry.",
                f"Search previous trips related to {destination}." if destination else "Search previous similar trips.",
                "Find travel insurance options.",
                "Estimate trip budget.",
                "Summarize itinerary.",
                "Present plan for approval.",
            ]
        if "insurance" in lowered:
            return [
                "Collect existing policy documents.",
                "Extract coverage details and limits.",
                "Identify exclusions and renewal dates.",
                "Compare at least three available options.",
                "Estimate expected annual cost.",
                "Draft recommendation summary.",
                "Present plan for approval.",
            ]
        return [
            "Clarify objective and required deliverables.",
            "Gather relevant memories and retrieved documents.",
            "Identify dependencies and constraints.",
            "Execute required analysis steps in order.",
            "Validate completeness and evidence.",
            "Summarize findings and action items.",
            "Present plan for approval.",
        ]

    def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        citations = self._collect_citations(context)
        output = {
            "task_id": task.get("task_id", ""),
            "title": task.get("title", ""),
            "details": f"Completed step: {task.get('description', '').strip()}",
            "citations": citations,
            "confidence": self._calculate_confidence(citations),
        }
        return output

    def validate(self, payload: dict[str, Any]) -> bool:
        citations = payload.get("citations") or []
        confidence = float(payload.get("confidence", 0.0))
        if not payload.get("details"):
            return False
        if not citations:
            return False
        return 0.0 <= confidence <= 1.0

    def summarize(self, payload: dict[str, Any]) -> str:
        return str(payload.get("details", "Task execution completed."))

    def cleanup(self) -> None:
        self._initialized = False

    def _extract_destination(self, request: str) -> str:
        match = re.search(r"(?:to|for)\s+([A-Za-z\s]{2,30})", request)
        if not match:
            return ""
        return match.group(1).strip().rstrip(".")

    def _collect_citations(self, context: dict[str, Any]) -> list[str]:
        citations = []
        for item in context.get("retrieved_documents", []):
            path = str(item.get("path", "")).strip()
            if path:
                citations.append(path)
        if not citations:
            citations.append("internal:memory")
        return citations[:5]

    def _calculate_confidence(self, citations: list[str]) -> float:
        base = 0.55
        boost = min(0.4, 0.08 * len(citations))
        return round(min(0.99, base + boost), 2)
