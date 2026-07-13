from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.context import ContextChunk


@dataclass(slots=True)
class Citation:
    filename: str
    path: str
    page: int | str
    folder: str
    chunk_reference: str
    score: float


class CitationFormatter:
    def format(self, chunks: list[ContextChunk]) -> list[Citation]:
        citations: list[Citation] = []
        seen: set[str] = set()
        for chunk in chunks:
            key = f"{chunk.path}|{chunk.page}|{chunk.chunk_id}"
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                Citation(
                    filename=chunk.filename,
                    path=chunk.path,
                    page=chunk.page,
                    folder=Path(chunk.path).parent.name if chunk.path else "",
                    chunk_reference=chunk.chunk_id,
                    score=max(0.0, min(1.0, float(chunk.score))),
                )
            )
        return citations

    def as_sources(self, citations: list[Citation]) -> list[dict[str, object]]:
        return [
            {
                "filename": citation.filename,
                "path": citation.path,
                "page": citation.page if citation.page not in {"", -1} else None,
                "score": citation.score,
            }
            for citation in citations
        ]

    def to_display_lines(self, citations: list[Citation]) -> list[str]:
        lines: list[str] = []
        for citation in citations:
            if citation.page not in {"", -1, None}:
                lines.append(f"{citation.filename} (Page {citation.page})")
            else:
                lines.append(citation.filename)
        return lines
