import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database
from app.summarization import SummaryGenerator


class SummaryGenerationPhase5Tests(unittest.TestCase):
    def test_summary_cache_updates_only_on_source_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "db.sqlite")
            initialize_database(db_path)
            generator = SummaryGenerator(db_path)

            source_rows = [{"source_document": "/vault/Luxoria/a.txt", "confidence": 0.7}]
            first = generator.get_or_refresh("project", "Luxoria", source_rows)
            second = generator.get_or_refresh("project", "Luxoria", source_rows)
            self.assertEqual(first, second)

            changed = generator.get_or_refresh(
                "project",
                "Luxoria",
                [{"source_document": "/vault/Luxoria/b.txt", "confidence": 0.8}],
            )
            self.assertNotEqual(first, changed)

            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT COUNT(*) FROM summary_cache").fetchone()[0]
            self.assertEqual(rows, 1)


if __name__ == "__main__":
    unittest.main()
