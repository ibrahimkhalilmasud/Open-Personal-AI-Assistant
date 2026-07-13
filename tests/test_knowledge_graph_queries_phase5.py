import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.knowledge_graph.query import KnowledgeGraphQuery
from app.memory.long_term import LongTermMemoryEngine


class KnowledgeGraphQueryPhase5Tests(unittest.TestCase):
    def test_related_queries_return_graph_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "db.sqlite")
            initialize_database(db_path)
            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Insurance/policy.txt",
                    "filename": "policy.txt",
                    "extension": "txt",
                    "file_size": 10,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-07-01T00:00:00+00:00",
                    "sha256": "sha-policy",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "sig-policy",
                    "last_scan": "2025-07-01T00:00:00+00:00",
                    "extracted_text": "Mr. Mike works at Luxoria Company. Insurance renews every July.",
                    "metadata": {},
                },
            )

            LongTermMemoryEngine(db_path).refresh_from_index()
            graph = KnowledgeGraphQuery(db_path).related_to("Mike")
            self.assertGreaterEqual(len(graph["entities"]), 1)
            self.assertGreaterEqual(len(graph["relationships"]), 1)


if __name__ == "__main__":
    unittest.main()
