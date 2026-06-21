import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import REQUIRED_TABLES, initialize_database


class DatabaseTests(unittest.TestCase):
    def test_initialize_database_creates_required_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "database.db")
            initialize_database(db_path)

            with sqlite3.connect(db_path) as conn:
                names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

            for table in REQUIRED_TABLES:
                self.assertIn(table, names)


if __name__ == "__main__":
    unittest.main()
