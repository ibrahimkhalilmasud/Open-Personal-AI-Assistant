from __future__ import annotations

WORKFLOW_TEMPLATES: dict[str, list[str]] = {
    "research_workflow": [
        "Define research objective and expected output.",
        "Collect relevant documents and prior notes.",
        "Analyze findings and extract key facts.",
        "Build a concise evidence-backed summary.",
        "Present plan for approval.",
    ],
    "document_analysis_workflow": [
        "Identify target documents for analysis.",
        "Extract structure, metadata, and key entities.",
        "Highlight risks, gaps, and open questions.",
        "Summarize findings with citations.",
        "Present plan for approval.",
    ],
    "travel_preparation_workflow": [
        "Find passport.",
        "Check passport expiry.",
        "Search previous trips and preferences.",
        "Find travel insurance options.",
        "Estimate budget and itinerary.",
        "Present plan for approval.",
    ],
    "project_summary_workflow": [
        "Collect project documents and notes.",
        "Identify milestones and current status.",
        "Summarize blockers and next steps.",
        "Prepare concise project summary.",
        "Present plan for approval.",
    ],
    "insurance_review_workflow": [
        "Collect current insurance policies.",
        "Extract limits, exclusions, and renewal dates.",
        "Compare alternative options and cost.",
        "Draft recommendation summary.",
        "Present plan for approval.",
    ],
}
