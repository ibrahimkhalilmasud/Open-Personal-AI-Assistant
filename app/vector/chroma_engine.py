from __future__ import annotations

import json
import math
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover
    chromadb = None

from app.vector.chunking import DocumentChunk


@dataclass(slots=True)
class VectorResult:
    score: float
    text: str
    filename: str
    path: str
    snippet: str
    file_type: str
    page: int | str
    chunk_id: str
    created_date: str
    modified_date: str
    source: str


class _PersistentLocalCollection:
    def __init__(self, db_path: str, collection_name: str) -> None:
        base = Path(db_path)
        base.mkdir(parents=True, exist_ok=True)
        self._db = base / f"{collection_name}_vectors.sqlite"
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    chunk_number INTEGER NOT NULL,
                    page_number INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    index_signature TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    modified_date TEXT NOT NULL,
                    document TEXT NOT NULL,
                    embedding_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vectors_source ON vectors(source_path)")
            conn.commit()

    def delete(self, where: dict[str, Any]) -> None:
        source = where.get("source_path")
        if source is None:
            return
        with sqlite3.connect(self._db) as conn:
            conn.execute("DELETE FROM vectors WHERE source_path = ?", (source,))
            conn.commit()

    def get(self, where: dict[str, Any], limit: int, include: list[str]) -> dict[str, Any]:
        source = where.get("source_path")
        if source is None:
            return {"metadatas": []}
        with sqlite3.connect(self._db) as conn:
            rows = conn.execute(
                """
                SELECT source_path, filename, file_type, chunk_number, page_number,
                       sha256, index_signature, created_date, modified_date
                FROM vectors
                WHERE source_path = ?
                ORDER BY chunk_number ASC
                LIMIT ?
                """,
                (source, max(1, limit)),
            ).fetchall()
        return {
            "metadatas": [
                {
                    "source_path": row[0],
                    "filename": row[1],
                    "file_type": row[2],
                    "chunk_number": row[3],
                    "page_number": row[4],
                    "sha256": row[5],
                    "index_signature": row[6],
                    "created_date": row[7],
                    "modified_date": row[8],
                }
                for row in rows
            ]
        }

    def upsert(self, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        with sqlite3.connect(self._db) as conn:
            for record_id, doc, metadata, embedding in zip(ids, documents, metadatas, embeddings, strict=False):
                conn.execute(
                    """
                    INSERT INTO vectors (
                        id, source_path, filename, file_type, chunk_number, page_number, sha256,
                        index_signature, created_date, modified_date, document, embedding_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        source_path=excluded.source_path,
                        filename=excluded.filename,
                        file_type=excluded.file_type,
                        chunk_number=excluded.chunk_number,
                        page_number=excluded.page_number,
                        sha256=excluded.sha256,
                        index_signature=excluded.index_signature,
                        created_date=excluded.created_date,
                        modified_date=excluded.modified_date,
                        document=excluded.document,
                        embedding_json=excluded.embedding_json
                    """,
                    (
                        record_id,
                        str(metadata.get("source_path", "")),
                        str(metadata.get("filename", "")),
                        str(metadata.get("file_type", "")),
                        int(metadata.get("chunk_number", 0) or 0),
                        int(metadata.get("page_number", -1) or -1),
                        str(metadata.get("sha256", "")),
                        str(metadata.get("index_signature", "")),
                        str(metadata.get("created_date", "")),
                        str(metadata.get("modified_date", "")),
                        doc,
                        json.dumps(embedding),
                    ),
                )
            conn.commit()

    def query(self, query_embeddings: list[list[float]], n_results: int, include: list[str]) -> dict[str, Any]:
        query = query_embeddings[0] if query_embeddings else []
        with sqlite3.connect(self._db) as conn:
            rows = conn.execute(
                """
                SELECT id, source_path, filename, file_type, chunk_number, page_number, sha256,
                       index_signature, created_date, modified_date, document, embedding_json
                FROM vectors
                """
            ).fetchall()

        scored: list[tuple[float, tuple[Any, ...]]] = []
        for row in rows:
            embedding = json.loads(row[11])
            scored.append((self._distance(query, embedding), row))
        scored.sort(key=lambda item: item[0])
        top = scored[: max(1, n_results)]

        return {
            "documents": [[item[1][10] for item in top]],
            "metadatas": [
                [
                    {
                        "id": item[1][0],
                        "source_path": item[1][1],
                        "filename": item[1][2],
                        "file_type": item[1][3],
                        "chunk_number": item[1][4],
                        "page_number": item[1][5],
                        "sha256": item[1][6],
                        "index_signature": item[1][7],
                        "created_date": item[1][8],
                        "modified_date": item[1][9],
                    }
                    for item in top
                ]
            ],
            "distances": [[item[0] for item in top]],
        }

    def _distance(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 1.0
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 1.0
        similarity = dot / (norm_a * norm_b)
        return 1.0 - similarity

    def count(self) -> int:
        with sqlite3.connect(self._db) as conn:
            return int(conn.execute("SELECT COUNT(*) FROM vectors").fetchone()[0])


class ChromaEngine:
    def __init__(self, db_path: str, collection_name: str = "vault_chunks") -> None:
        self._local = bool(os.getenv("OPA_FORCE_LOCAL_VECTOR_DB", "").strip().lower() in {"1", "true", "yes"})
        self._db_path = db_path
        Path(db_path).mkdir(parents=True, exist_ok=True)

        if chromadb is not None and not self._local:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            return

        self.collection = _PersistentLocalCollection(db_path, collection_name)
        self._local = True

    def delete_by_source(self, source_path: str) -> None:
        self.collection.delete(where={"source_path": source_path})

    def get_source_sha(self, source_path: str) -> str | None:
        result = self.collection.get(where={"source_path": source_path}, limit=1, include=["metadatas"])
        metadatas = result.get("metadatas") or []
        if not metadatas:
            return None
        metadata = metadatas[0] or {}
        return str(metadata.get("sha256", "")) or None

    def get_source_signature(self, source_path: str) -> str | None:
        result = self.collection.get(where={"source_path": source_path}, limit=1, include=["metadatas"])
        metadatas = result.get("metadatas") or []
        if not metadatas:
            return None
        metadata = metadatas[0] or {}
        return str(metadata.get("index_signature", "")) or None

    def replace_source_chunks(
        self,
        source_path: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
        *,
        sha256: str,
        index_signature: str,
        file_type: str,
        created_date: str,
        modified_date: str,
    ) -> None:
        self.delete_by_source(source_path)
        self.upsert_chunks(
            chunks=chunks,
            embeddings=embeddings,
            sha256=sha256,
            index_signature=index_signature,
            file_type=file_type,
            created_date=created_date,
            modified_date=modified_date,
        )

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
        *,
        sha256: str,
        index_signature: str,
        file_type: str,
        created_date: str,
        modified_date: str,
    ) -> None:
        if not chunks:
            return
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "source_path": chunk.source_path,
                "filename": chunk.filename,
                "file_type": file_type,
                "chunk_number": chunk.chunk_number,
                "page_number": chunk.page_number if chunk.page_number is not None else -1,
                "sha256": sha256,
                "index_signature": index_signature,
                "created_date": created_date,
                "modified_date": modified_date,
            }
            for chunk in chunks
        ]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def query(self, embedding: list[float], top_k: int = 10) -> list[VectorResult]:
        top = max(1, top_k)
        raw = self.collection.query(query_embeddings=[embedding], n_results=top, include=["documents", "metadatas", "distances"])
        docs = (raw.get("documents") or [[]])[0]
        metadatas = (raw.get("metadatas") or [[]])[0]
        distances = (raw.get("distances") or [[]])[0]

        results: list[VectorResult] = []
        for doc, metadata, distance in zip(docs, metadatas, distances, strict=False):
            data = metadata or {}
            similarity = 1.0 / (1.0 + float(distance))
            text = str(doc or "")
            results.append(
                VectorResult(
                    score=max(0.0, min(1.0, similarity)),
                    text=text,
                    filename=str(data.get("filename", "")),
                    path=str(data.get("source_path", "")),
                    snippet=text[:220],
                    file_type=str(data.get("file_type", "")),
                    page=int(data.get("page_number", -1) or -1),
                    chunk_id=str(data.get("id", "")),
                    created_date=str(data.get("created_date", "")),
                    modified_date=str(data.get("modified_date", "")),
                    source=str(data.get("source_path", "")),
                )
            )
        return results

    def count(self) -> int:
        if hasattr(self.collection, "count"):
            return int(self.collection.count())  # type: ignore[arg-type]
        return 0
