import os
import unittest

from app.embeddings import EmbeddingEngine


class EmbeddingTests(unittest.TestCase):
    def test_fallback_embedding_returns_vectors(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        engine = EmbeddingEngine("all-MiniLM-L6-v2")

        vectors = engine.embed(["medical assessment", "doctor report"])
        query = engine.embed_query("doctor report")

        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), engine.dimension)
        self.assertEqual(len(query), engine.dimension)
        self.assertNotEqual(vectors[0], vectors[1])


if __name__ == "__main__":
    unittest.main()
