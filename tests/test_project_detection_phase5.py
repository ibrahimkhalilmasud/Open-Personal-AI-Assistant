import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database, upsert_indexed_file
from app.memory.long_term import LongTermMemoryEngine
from app.memory.projects import ProjectMemory


class ProjectDetectionPhase5Tests(unittest.TestCase):
    def test_project_is_detected_from_path_and_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "db.sqlite")
            initialize_database(db_path)
            upsert_indexed_file(
                db_path,
                {
                    "path": "/vault/Luxoria/invoice.txt",
                    "filename": "invoice.txt",
                    "extension": "txt",
                    "file_size": 10,
                    "created_date": "2025-01-01T00:00:00+00:00",
                    "modified_date": "2025-02-01T00:00:00+00:00",
                    "sha256": "sha-project",
                    "indexed": 1,
                    "embedding_status": "pending",
                    "indexed_date": None,
                    "chunk_count": 0,
                    "index_signature": "sig-project",
                    "last_scan": "2025-02-01T00:00:00+00:00",
                    "extracted_text": "Project: Luxoria and Mr. Mike approved invoice.",
                    "metadata": {},
                },
            )

            LongTermMemoryEngine(db_path).refresh_from_index()
            project = ProjectMemory(db_path).get("Luxoria")
            self.assertIsNotNone(project)
            self.assertIn("/vault/Luxoria/invoice.txt", project["related_files"])


if __name__ == "__main__":
    unittest.main()
