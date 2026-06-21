from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings
from app.database.sqlite_db import fetch_file_row, fetch_indexable_text_rows, update_embedding_status
from app.embeddings import EmbeddingEngine
from app.vector import ChromaEngine, chunk_document


@dataclass(slots=True)
class IndexSummary:
    total: int
    indexed: int
    skipped: int
    failed: int


class VectorIndexer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = EmbeddingEngine(settings.embedding_model)
        self.vector_db = ChromaEngine(settings.vector_db)

    def index_all(self) -> IndexSummary:
        rows = fetch_indexable_text_rows(self.settings.database)
        indexed = 0
        skipped = 0
        failed = 0

        for row in rows:
            result = self.index_row(row)
            if result == "indexed":
                indexed += 1
            elif result == "skipped":
                skipped += 1
            else:
                failed += 1

        return IndexSummary(total=len(rows), indexed=indexed, skipped=skipped, failed=failed)

    def index_path(self, source_path: str) -> str:
        row = fetch_file_row(self.settings.database, source_path)
        if row is None:
            self.vector_db.delete_by_source(source_path)
            return "deleted"
        return self.index_row(row)

    def index_row(self, row: dict[str, object]) -> str:
        source_path = str(row.get("path", ""))
        filename = str(row.get("filename", ""))
        text = str(row.get("extracted_text", "") or "")
        sha256 = str(row.get("sha256", ""))

        if not source_path:
            return "failed"

        existing_sha = self.vector_db.get_source_sha(source_path)
        if existing_sha == sha256 and (row.get("embedding_status") == "indexed"):
            return "skipped"

        if not text.strip():
            self.vector_db.delete_by_source(source_path)
            update_embedding_status(self.settings.database, source_path, "indexed", chunk_count=0)
            return "indexed"

        chunks = chunk_document(
            text=text,
            source_path=source_path,
            filename=filename,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        try:
            self.vector_db.delete_by_source(source_path)
            embeddings = self.embedder.embed([chunk.text for chunk in chunks])
            self.vector_db.upsert_chunks(chunks, embeddings, sha256=sha256)
            update_embedding_status(self.settings.database, source_path, "indexed", chunk_count=len(chunks))
            return "indexed"
        except Exception:
            update_embedding_status(self.settings.database, source_path, "error", chunk_count=0)
            return "failed"

    def remove_path(self, source_path: str) -> None:
        self.vector_db.delete_by_source(source_path)
