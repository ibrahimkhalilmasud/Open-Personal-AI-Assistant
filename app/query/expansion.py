from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SYNONYMS: dict[str, list[str]] = {
    "medical": ["doctor", "hospital", "diagnosis", "health", "patient", "report"],
    "insurance": ["policy", "renewal", "coverage", "claim", "premium"],
    "travel": ["flight", "hotel", "boarding", "reservation", "invoice"],
    "research": ["paper", "study", "thesis", "publication", "phd"],
}


@dataclass(slots=True)
class QueryExpansionResult:
    expanded_terms: list[str]


class QueryExpander:
    def __init__(self, synonyms: dict[str, list[str]] | None = None, synonyms_file: str = "") -> None:
        file_synonyms = self._load_synonyms_file(synonyms_file)
        combined = {**DEFAULT_SYNONYMS, **file_synonyms}
        if synonyms:
            combined.update(synonyms)
        self.synonyms = {key.lower(): [value.lower() for value in values] for key, values in combined.items()}

    def expand(self, query: str, keywords: list[str] | None = None) -> QueryExpansionResult:
        terms: list[str] = []
        for token in (keywords or query.lower().split()):
            normalized = token.strip().lower()
            if not normalized:
                continue
            if normalized not in terms:
                terms.append(normalized)
            for synonym in self.synonyms.get(normalized, []):
                if synonym not in terms:
                    terms.append(synonym)
        return QueryExpansionResult(expanded_terms=terms)

    def _load_synonyms_file(self, synonyms_file: str) -> dict[str, list[str]]:
        if not synonyms_file.strip():
            return {}
        path = Path(synonyms_file)
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}

        normalized: dict[str, list[str]] = {}
        for key, value in payload.items():
            if not isinstance(key, str) or not isinstance(value, list):
                continue
            normalized[key] = [str(item) for item in value if str(item).strip()]
        return normalized
