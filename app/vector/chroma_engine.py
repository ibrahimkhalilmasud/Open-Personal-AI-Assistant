from __future__ import annotations

import math
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
    chunk_number: int


class _LocalCollection:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def delete(self, where: dict[str, Any]) -> None:
        source = where.get("source_path")
        if source is None:
            return
        to_delete = [record_id for record_id, payload in self.records.items() if payload["metadata"].get("source_path") == source]
        for record_id in to_delete:
            self.records.pop(record_id, None)

    def get(self, where: dict[str, Any], limit: int, include: list[str]) -> dict[str, Any]:
        source = where.get("source_path")
        selected = [payload for payload in self.records.values() if payload["metadata"].get("source_path") == source]
        selected = selected[: max(1, limit)]
        return {
            "metadatas": [payload["metadata"] for payload in selected],
        }

    def upsert(self, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        for record_id, doc, metadata, embedding in zip(ids, documents, metadatas, embeddings, strict=False):
            self.records[record_id] = {
                "document": doc,
                "metadata": metadata,
                "embedding": embedding,
            }

    def query(self, query_embeddings: list[list[float]], n_results: int, include: list[str]) -> dict[str, Any]:
        query = query_embeddings[0] if query_embeddings else []
        scored: list[tuple[float, dict[str, Any]]] = []
        for payload in self.records.values():
            scored.append((self._distance(query, payload["embedding"]), payload))
        scored.sort(key=lambda item: item[0])
        top = scored[: max(1, n_results)]
        return {
            "documents": [[item[1]["document"] for item in top]],
            "metadatas": [[item[1]["metadata"] for item in top]],
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


_LOCAL_COLLECTIONS: dict[str, _LocalCollection] = {}


class ChromaEngine:
    def __init__(self, db_path: str, collection_name: str = "vault_chunks") -> None:
        if chromadb is not None:
            Path(db_path).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            self._local = False
            return

        key = f"{db_path}:{collection_name}"
        self.collection = _LOCAL_COLLECTIONS.setdefault(key, _LocalCollection())
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

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]], sha256: str) -> None:
        if not chunks:
            return

        ids = [chunk.id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "source_path": chunk.source_path,
                "filename": chunk.filename,
                "chunk_number": chunk.chunk_number,
                "page_number": chunk.page_number if chunk.page_number is not None else -1,
                "sha256": sha256,
            }
            for chunk in chunks
        ]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def query(self, embedding: list[float], top_k: int = 10) -> list[VectorResult]:
        top = max(1, top_k)
        raw = self.collection.query(
            query_embeddings=[embedding],
            n_results=top,
            include=["documents", "metadatas", "distances"],
        )

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
                    score=similarity,
                    text=text,
                    filename=str(data.get("filename", "")),
                    path=str(data.get("source_path", "")),
                    snippet=text[:220],
                    chunk_number=int(data.get("chunk_number", 0) or 0),
                )
            )
        return results
