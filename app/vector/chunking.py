from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DocumentChunk:
    id: str
    text: str
    source_path: str
    filename: str
    chunk_number: int
    page_number: int | None


def chunk_document(
    text: str,
    source_path: str,
    filename: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[DocumentChunk]:
    words = text.split()
    if not words:
        return []

    size = max(1, chunk_size)
    overlap = min(max(0, chunk_overlap), size - 1)
    step = max(1, size - overlap)

    chunks: list[DocumentChunk] = []
    chunk_number = 1

    for start in range(0, len(words), step):
        end = start + size
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunk_text = " ".join(chunk_words).strip()
        if not chunk_text:
            continue

        chunks.append(
            DocumentChunk(
                id=f"{source_path}::chunk::{chunk_number}",
                text=chunk_text,
                source_path=source_path,
                filename=filename,
                chunk_number=chunk_number,
                page_number=None,
            )
        )
        chunk_number += 1

        if end >= len(words):
            break

    return chunks
