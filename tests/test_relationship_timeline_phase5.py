import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.knowledge_graph.timeline import TimelineEngine
from app.memory.long_term import LongTermMemoryEngine


class RelationshipTimelinePhase5Tests(unittest.TestCase):
    def test_timeline_query_returns_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "db.sqlite")
            initialize_database(db_path)
            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Travel/trip.txt",
                    "filename": "trip.txt",
                    "extension": "txt",
                    "file_size": 12,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-03-05T00:00:00+00:00",
                    "sha256": "sha-trip",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "sig-trip",
                    "last_scan": "2025-03-05T00:00:00+00:00",
                    "extracted_text": "Mike travel to Brussels with airline booking.",
                    "metadata": {},
                },
            )

            LongTermMemoryEngine(db_path).refresh_from_index()
            events = TimelineEngine(db_path).query("2025-03")
            self.assertGreaterEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "document_indexed")


if __name__ == "__main__":
    unittest.main()
