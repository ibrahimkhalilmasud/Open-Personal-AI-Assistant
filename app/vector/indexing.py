from __future__ import annotations

import time
from dataclasses import dataclass

from app.config.settings import Settings
from app.database.sqlite_db import fetch_file_row, fetch_indexable_text_rows, update_embedding_status
from app.embeddings import EmbeddingEngine
from app.logging import get_error_logger
from app.vector import ChromaEngine, chunk_document


@dataclass(slots=True)
class IndexSummary:
    total: int
    indexed: int
    updated: int
    skipped: int
    failed: int
    duration_seconds: float


class VectorIndexer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = EmbeddingEngine(settings.embedding_model, batch_size=settings.embed_batch_size)
        self.vector_db = ChromaEngine(settings.vector_db)
        self.error_logger = get_error_logger("vector.indexing")

    def index_all(self) -> IndexSummary:
        started = time.perf_counter()
        rows = fetch_indexable_text_rows(self.settings.database)
        indexed = 0
        updated = 0
        skipped = 0
        failed = 0

        for row in rows:
            result = self.index_row(row)
            if result == "indexed":
                indexed += 1
            elif result == "updated":
                updated += 1
            elif result == "skipped":
                skipped += 1
            else:
                failed += 1

        duration = time.perf_counter() - started
        return IndexSummary(
            total=len(rows),
            indexed=indexed,
            updated=updated,
            skipped=skipped,
            failed=failed,
            duration_seconds=duration,
        )

    def index_path(self, source_path: str) -> str:
        row = fetch_file_row(self.settings.database, source_path)
        if row is None:
            self.vector_db.delete_by_source(source_path)
            return "deleted"
        return self.index_row(row)

    def index_row(self, row: dict[str, object]) -> str:
        source_path = str(row.get("path", ""))
        filename = str(row.get("filename", ""))
        file_type = str(row.get("extension", ""))
        text = str(row.get("extracted_text", "") or "")
        sha256 = str(row.get("sha256", ""))
        created_date = str(row.get("created_date", ""))
        modified_date = str(row.get("modified_date", ""))
        current_signature = self._index_signature(sha256, modified_date)
        previous_signature = str(row.get("index_signature", "") or "")

        if not source_path:
            return "failed"

        existing_signature = self.vector_db.get_source_signature(source_path)
        had_existing_vectors = bool(previous_signature or existing_signature)
        if (
            previous_signature == current_signature
            and existing_signature == current_signature
            and (row.get("embedding_status") == "indexed")
        ):
            return "skipped"

        if not text.strip():
            self.vector_db.delete_by_source(source_path)
            update_embedding_status(
                self.settings.database,
                source_path,
                "indexed",
                chunk_count=0,
                index_signature=current_signature,
            )
            return "updated" if had_existing_vectors else "indexed"

        chunks = chunk_document(
            text=text,
            source_path=source_path,
            filename=filename,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        try:
            embeddings = self.embedder.embed([chunk.text for chunk in chunks])
            update_embedding_status(self.settings.database, source_path, "indexing", chunk_count=0)
            self.vector_db.replace_source_chunks(
                source_path,
                chunks,
                embeddings,
                sha256=sha256,
                index_signature=current_signature,
                file_type=file_type,
                created_date=created_date,
                modified_date=modified_date,
            )
            update_embedding_status(
                self.settings.database,
                source_path,
                "indexed",
                chunk_count=len(chunks),
                index_signature=current_signature,
            )
            return "updated" if had_existing_vectors else "indexed"
        except Exception:
            self.error_logger.exception("index_row failed | path=%s", source_path)
            update_embedding_status(self.settings.database, source_path, "error", chunk_count=0)
            return "failed"

    def remove_path(self, source_path: str) -> None:
        self.vector_db.delete_by_source(source_path)

    def _index_signature(self, sha256: str, modified_date: str) -> str:
        return "|".join(
            [
                sha256,
                modified_date,
                self.settings.embedding_model,
                str(self.settings.chunk_size),
                str(self.settings.chunk_overlap),
            ]
        )
