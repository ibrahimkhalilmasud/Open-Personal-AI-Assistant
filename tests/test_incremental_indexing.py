import os
import tempfile
import unittest

from app.config.settings import load_settings
from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.vector.indexing import VectorIndexer


class IncrementalIndexingTests(unittest.TestCase):
    def test_indexing_skips_when_signature_unchanged(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        os.environ["OPA_FORCE_LOCAL_VECTOR_DB"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            db_path = f"{tmp}/db.sqlite"
            vector_path = f"{tmp}/vector"
            os.environ["DATABASE"] = db_path
            os.environ["VECTOR_DB"] = vector_path
            initialize_database(db_path)

            payload = {
                "path": "/vault/file.txt",
                "filename": "file.txt",
                "extension": "txt",
                "file_size": 100,
                "created_date": "2025-01-01T00:00:00+00:00",
                "modified_date": "2025-01-01T00:00:00+00:00",
                "sha256": "hash-1",
                "indexed": 1,
                "embedding_status": "pending",
                "indexed_date": None,
                "chunk_count": 0,
                "index_signature": "",
                "last_scan": "2025-01-01T00:00:00+00:00",
                "extracted_text": "insurance claim details",
                "metadata": {},
            }
            upsert_indexed_file(db_path, payload)

            settings = load_settings()
            indexer = VectorIndexer(settings)

            first = indexer.index_all()
            self.assertEqual(first.indexed, 1)
            self.assertEqual(first.updated, 0)
            self.assertEqual(first.skipped, 0)

            second = indexer.index_all()
            self.assertEqual(second.skipped, 1)

            payload["sha256"] = "hash-2"
            payload["modified_date"] = "2025-02-01T00:00:00+00:00"
            upsert_indexed_file(db_path, payload)
            third = indexer.index_all()
            self.assertEqual(third.updated, 1)


if __name__ == "__main__":
    unittest.main()
