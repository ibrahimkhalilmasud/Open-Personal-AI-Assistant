from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ContextChunk:
    rank: int
    score: float
    text: str
    filename: str
    path: str
    page: int | str
    chunk_id: str
    modified_date: str


@dataclass(slots=True)
class ContextBundle:
    chunks: list[ContextChunk]
    estimated_tokens: int
    truncated: bool


class ContextBuilder:
    def __init__(self, max_chunks: int = 12, max_tokens: int = 12000) -> None:
        self.max_chunks = max(1, max_chunks)
        self.max_tokens = max(200, max_tokens)

    def build(self, retrieved: list[dict[str, object]]) -> ContextBundle:
        ranked = self._rank_records(retrieved)

        selected: list[ContextChunk] = []
        seen: set[str] = set()
        tokens = 0
        truncated = False

        for index, row in enumerate(ranked, start=1):
            dedupe_key = self._dedupe_key(row)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            text = str(row.get("text", "") or "").strip()
            if not text:
                continue

            estimated = self._estimate_tokens(text)
            if len(selected) >= self.max_chunks or tokens + estimated > self.max_tokens:
                truncated = True
                continue

            selected.append(
                ContextChunk(
                    rank=index,
                    score=float(row.get("score", 0.0) or 0.0),
                    text=text,
                    filename=str(row.get("filename", "")),
                    path=str(row.get("path", "")),
                    page=row.get("page", ""),
                    chunk_id=str(row.get("chunk_id", "")),
                    modified_date=str(row.get("modified_date", "")),
                )
            )
            tokens += estimated

        return ContextBundle(chunks=selected, estimated_tokens=tokens, truncated=truncated)

    def _rank_records(self, retrieved: list[dict[str, object]]) -> list[dict[str, object]]:
        return sorted(retrieved, key=self._sort_key, reverse=True)

    def _sort_key(self, row: dict[str, object]) -> tuple[float, float]:
        score = float(row.get("score", 0.0) or 0.0)
        modified = str(row.get("modified_date", "") or "")
        timestamp = self._to_timestamp(modified)
        return score, timestamp

    def _to_timestamp(self, value: str) -> float:
        if not value:
            return 0.0
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    def _estimate_tokens(self, text: str) -> int:
        # simple approximation suitable for context budgeting
        return max(1, int(len(text.split()) * 1.3))

    def _dedupe_key(self, row: dict[str, object]) -> str:
        return "|".join(
            [
                str(row.get("path", "")),
                str(row.get("chunk_id", "")),
                str(row.get("text", ""))[:120],
            ]
        )
