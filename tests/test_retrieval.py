import os
import tempfile
import unittest

from app.config.settings import load_settings
from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.retrieval.engine import RetrievalEngine
from app.vector.indexing import VectorIndexer


class RetrievalTests(unittest.TestCase):
    def test_retrieve_returns_text_source_score(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            db_path = f"{tmp}/db.sqlite"
            vector_path = f"{tmp}/vector"
            os.environ["DATABASE"] = db_path
            os.environ["VECTOR_DB"] = vector_path
            initialize_database(db_path)

            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/medical.txt",
                    "filename": "medical.txt",
                    "extension": "txt",
                    "file_size": 20,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-01-01T00:00:00+00:00",
                    "sha256": "sha1",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "last_scan": "2025-01-01T00:00:00+00:00",
                    "extracted_text": "Medical assessment and doctor report data",
                    "metadata": {},
                },
            )

            settings = load_settings()
            VectorIndexer(settings).index_all()

            results = RetrievalEngine().retrieve("doctor report", top_k=5)

            self.assertGreaterEqual(len(results), 1)
            self.assertIn("text", results[0])
            self.assertIn("source", results[0])
            self.assertIn("score", results[0])


if __name__ == "__main__":
    unittest.main()
