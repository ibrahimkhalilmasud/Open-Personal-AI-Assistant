from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

STOP_WORDS = {
    "a",
    "an",
    "and",
    "all",
    "any",
    "are",
    "documents",
    "every",
    "find",
    "from",
    "in",
    "my",
    "of",
    "show",
    "summarize",
    "the",
    "which",
}

FILE_TYPE_ALIASES = {
    "pdf": "pdf",
    "doc": "docx",
    "docx": "docx",
    "text": "txt",
    "txt": "txt",
    "markdown": "md",
    "md": "md",
    "csv": "csv",
    "xlsx": "xlsx",
    "excel": "xlsx",
    "invoice": "pdf",
}


@dataclass(slots=True)
class QueryAnalysis:
    intent: str
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    date_filters: dict[str, str] = field(default_factory=dict)
    folder_filters: list[str] = field(default_factory=list)
    file_type_filters: list[str] = field(default_factory=list)


class QueryAnalyzer:
    def analyze(self, query: str) -> QueryAnalysis:
        cleaned = query.strip()
        lowered = cleaned.lower()

        return QueryAnalysis(
            intent=self._detect_intent(lowered),
            keywords=self._extract_keywords(lowered),
            entities=self._extract_entities(cleaned),
            date_filters=self._extract_date_filters(lowered),
            folder_filters=self._extract_folder_filters(cleaned),
            file_type_filters=self._extract_file_types(lowered),
        )

    def _detect_intent(self, query: str) -> str:
        if any(term in query for term in {"summarize", "summary", "overview"}):
            return "summarize"
        if any(term in query for term in {"which", "where", "what", "mention"}):
            return "lookup"
        return "retrieve"

    def _extract_keywords(self, query: str) -> list[str]:
        tokens = re.findall(r"[a-z0-9]+", query.lower())
        seen: set[str] = set()
        keywords: list[str] = []
        for token in tokens:
            if token in STOP_WORDS or len(token) < 3:
                continue
            if token in seen:
                continue
            seen.add(token)
            keywords.append(token)
        return keywords

    def _extract_entities(self, query: str) -> list[str]:
        entities = re.findall(r"\b[A-Z][a-zA-Z0-9_-]{2,}\b", query)
        seen: set[str] = set()
        result: list[str] = []
        for entity in entities:
            if entity in seen:
                continue
            seen.add(entity)
            result.append(entity)
        return result

    def _extract_date_filters(self, query: str) -> dict[str, str]:
        # Year-only patterns
        year_match = re.search(r"\b(20\d{2})\b", query)
        if year_match:
            year = int(year_match.group(1))
            return {
                "after": f"{year:04d}-01-01T00:00:00+00:00",
                "before": f"{year:04d}-12-31T23:59:59+00:00",
            }

        # Month-year patterns (e.g., october 2024)
        month_names = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}
        month_match = re.search(r"\b(" + "|".join(month_names.keys()) + r")\s+(20\d{2})\b", query)
        if month_match:
            month = month_names[month_match.group(1)]
            year = int(month_match.group(2))
            start = datetime(year, month, 1, tzinfo=UTC)
            days = calendar.monthrange(year, month)[1]
            end = datetime(year, month, days, 23, 59, 59, tzinfo=UTC)
            return {
                "after": start.isoformat(),
                "before": end.isoformat(),
            }

        return {}

    def _extract_folder_filters(self, query: str) -> list[str]:
        results: list[str] = []
        patterns = [
            r"\bfrom\s+([A-Za-z0-9_-]{3,})\b",
            r"\bin\s+([A-Za-z0-9_-]{3,})\b",
        ]
        for pattern in patterns:
            for match in re.findall(pattern, query):
                term = match.strip()
                if term.lower() in STOP_WORDS:
                    continue
                if term not in results:
                    results.append(term)
        return results

    def _extract_file_types(self, query: str) -> list[str]:
        found: list[str] = []
        for key, value in FILE_TYPE_ALIASES.items():
            if re.search(rf"\b{re.escape(key)}\b", query):
                if value not in found:
                    found.append(value)
        return found
