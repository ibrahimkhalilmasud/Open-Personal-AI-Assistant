from __future__ import annotations

import hashlib
import math
import os
from typing import Sequence


def _normalize_model_name(model_name: str) -> str:
    value = model_name.strip()
    if not value:
        return "sentence-transformers/all-MiniLM-L6-v2"
    if "/" in value:
        return value
    return f"sentence-transformers/{value}"


class EmbeddingEngine:
    def __init__(self, model_name: str) -> None:
        self.model_name = _normalize_model_name(model_name)
        self._model = None
        self._dimension = 384

        if os.getenv("OPA_DISABLE_REMOTE_EMBEDDINGS", "").strip().lower() in {"1", "true", "yes"}:
            return

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer(self.model_name)
        except Exception:
            self._model = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._model is not None:
            vectors = self._model.encode(list(texts), normalize_embeddings=True)
            return [list(map(float, vector)) for vector in vectors]
        return [self._fallback_embed(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        vectors = self.embed([query])
        return vectors[0] if vectors else [0.0] * self._dimension

    def _fallback_embed(self, text: str) -> list[float]:
        words = text.lower().split()
        vector = [0.0] * self._dimension
        if not words:
            return vector

        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self._dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]
