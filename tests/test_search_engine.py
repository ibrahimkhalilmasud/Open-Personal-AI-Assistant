import os
import tempfile
import unittest

from app.config.settings import load_settings
from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.search.search_engine import SearchEngine
from app.vector.indexing import VectorIndexer


class SearchEngineTests(unittest.TestCase):
    def test_search_supports_filters_and_normalized_scores(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        os.environ["OPA_FORCE_LOCAL_VECTOR_DB"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            db_path = f"{tmp}/db.sqlite"
            vector_path = f"{tmp}/vector"
            os.environ["DATABASE"] = db_path
            os.environ["VECTOR_DB"] = vector_path
            initialize_database(db_path)

            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Insurance/insurance_notes.txt",
                    "filename": "insurance_notes.txt",
                    "extension": "txt",
                    "file_size": 10,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-01-01T00:00:00+00:00",
                    "sha256": "s1",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "",
                    "last_scan": "2025-01-01T00:00:00+00:00",
                    "extracted_text": "insurance renewal form",
                    "metadata": {"category": "Insurance"},
                },
            )
            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Travel/travel_invoice.pdf",
                    "filename": "travel_invoice.pdf",
                    "extension": "pdf",
                    "file_size": 10,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-01-02T00:00:00+00:00",
                    "sha256": "s2",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "",
                    "last_scan": "2025-01-02T00:00:00+00:00",
                    "extracted_text": "travel invoice receipt",
                    "metadata": {"category": "Travel"},
                },
            )

            settings = load_settings()
            VectorIndexer(settings).index_all()
            engine = SearchEngine(settings)

            insurance = engine.search("insurance", folder="Insurance", top_k=10)
            self.assertEqual(len(insurance), 1)
            self.assertIn("Insurance", insurance[0].path)
            self.assertGreaterEqual(insurance[0].score, 0.0)
            self.assertLessEqual(insurance[0].score, 1.0)

            invoices = engine.search("invoice", file_type="pdf", top_k=10)
            self.assertEqual(len(invoices), 1)
            self.assertEqual(invoices[0].file_type, "pdf")


if __name__ == "__main__":
    unittest.main()
