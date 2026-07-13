import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.memory.long_term import LongTermMemoryEngine


class MemoryPersistencePhase5Tests(unittest.TestCase):
    def test_long_term_memory_persists_entities_relationships_and_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "db.sqlite")
            initialize_database(db_path)

            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Luxoria/travel_notes.txt",
                    "filename": "travel_notes.txt",
                    "extension": "txt",
                    "file_size": 20,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-03-01T00:00:00+00:00",
                    "sha256": "sha-memory",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "sig-memory",
                    "last_scan": "2025-03-01T00:00:00+00:00",
                    "extracted_text": "Mr. Mike works at Luxoria Company. Passport expires 2029.",
                    "metadata": {},
                },
            )

            summary = LongTermMemoryEngine(db_path).refresh_from_index()
            self.assertEqual(summary["processed_files"], 1)

            with sqlite3.connect(db_path) as conn:
                entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
                relationship_count = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
                fact_count = conn.execute("SELECT COUNT(*) FROM knowledge_memory").fetchone()[0]
                state_count = conn.execute("SELECT COUNT(*) FROM memory_processing_state").fetchone()[0]

            self.assertGreater(entity_count, 0)
            self.assertGreater(relationship_count, 0)
            self.assertGreater(fact_count, 0)
            self.assertEqual(state_count, 1)


if __name__ == "__main__":
    unittest.main()
