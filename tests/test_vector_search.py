import os
import tempfile
import unittest

from app.embeddings import EmbeddingEngine
from app.vector.chroma_engine import ChromaEngine
from app.vector.chunking import DocumentChunk


class VectorSearchTests(unittest.TestCase):
    def test_chroma_upsert_and_query(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        os.environ["OPA_FORCE_LOCAL_VECTOR_DB"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            embedder = EmbeddingEngine("all-MiniLM-L6-v2")
            engine = ChromaEngine(tmp, collection_name="test_chunks")

            chunks = [
                DocumentChunk(
                    id="/vault/a.txt::chunk::1",
                    text="Insurance renewal reminder for 2025",
                    source_path="/vault/a.txt",
                    filename="a.txt",
                    chunk_number=1,
                    page_number=None,
                )
            ]
            embeddings = embedder.embed([chunk.text for chunk in chunks])
            engine.upsert_chunks(
                chunks,
                embeddings,
                sha256="abc",
                index_signature="abc|sig",
                file_type="txt",
                created_date="2025-01-01T00:00:00+00:00",
                modified_date="2025-01-01T00:00:00+00:00",
            )

            results = engine.query(embedder.embed_query("insurance renewal"), top_k=1)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].path, "/vault/a.txt")
            self.assertGreater(results[0].score, 0)

    def test_local_persistence_survives_restart(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        os.environ["OPA_FORCE_LOCAL_VECTOR_DB"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            embedder = EmbeddingEngine("all-MiniLM-L6-v2")
            first = ChromaEngine(tmp, collection_name="persist_chunks")
            chunk = DocumentChunk(
                id="/vault/persist.txt::chunk::1",
                text="medical report persistence check",
                source_path="/vault/persist.txt",
                filename="persist.txt",
                chunk_number=1,
                page_number=None,
            )
            first.upsert_chunks(
                [chunk],
                embedder.embed([chunk.text]),
                sha256="sha",
                index_signature="sig",
                file_type="txt",
                created_date="2025-01-01T00:00:00+00:00",
                modified_date="2025-01-01T00:00:00+00:00",
            )

            second = ChromaEngine(tmp, collection_name="persist_chunks")
            results = second.query(embedder.embed_query("medical report"), top_k=1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].filename, "persist.txt")


if __name__ == "__main__":
    unittest.main()
