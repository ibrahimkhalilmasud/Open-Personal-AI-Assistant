from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchResponse:
    query: str
    count: int
    results: list[dict[str, object]]


@dataclass(slots=True)
class AskResponse:
    answer: str
    confidence: float
    confidence_label: str
    citations: list[str]
    provider: str
    model: str
