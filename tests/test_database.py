import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import FILES_COLUMNS, REQUIRED_TABLES, initialize_database


class DatabaseTests(unittest.TestCase):
    def test_initialize_database_creates_required_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "database.db")
            initialize_database(db_path)

            with sqlite3.connect(db_path) as conn:
                names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                files_cols = tuple(row[1] for row in conn.execute("PRAGMA table_info(files)").fetchall())

            for table in REQUIRED_TABLES:
                self.assertIn(table, names)
            self.assertEqual(files_cols, FILES_COLUMNS)


if __name__ == "__main__":
    unittest.main()
