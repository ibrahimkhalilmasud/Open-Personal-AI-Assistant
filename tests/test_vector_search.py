import os
import tempfile
import unittest

from app.embeddings import EmbeddingEngine
from app.vector.chroma_engine import ChromaEngine
from app.vector.chunking import DocumentChunk


class VectorSearchTests(unittest.TestCase):
    def test_chroma_upsert_and_query(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
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
            engine.upsert_chunks(chunks, embeddings, sha256="abc")

            results = engine.query(embedder.embed_query("insurance renewal"), top_k=1)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].path, "/vault/a.txt")
            self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
