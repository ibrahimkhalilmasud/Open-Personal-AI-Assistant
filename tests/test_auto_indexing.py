import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.config.settings import load_settings
from app.database.sqlite_db import fetch_file_row
from app.vault.engine import VaultEngine


class AutoIndexingTests(unittest.TestCase):
    def test_add_modify_delete_file_updates_db_and_vectors(self) -> None:
        os.environ["OPA_DISABLE_REMOTE_EMBEDDINGS"] = "true"
        os.environ["OPA_FORCE_LOCAL_VECTOR_DB"] = "true"
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()
            db = Path(tmp) / "db.sqlite"
            vector = Path(tmp) / "vector"
            os.environ["VAULT_PATH"] = str(vault)
            os.environ["DATABASE"] = str(db)
            os.environ["VECTOR_DB"] = str(vector)

            settings = load_settings()
            engine = VaultEngine(settings)
            engine.full_scan()

            file_path = vault / "auto.txt"
            file_path.write_text("insurance alpha", encoding="utf-8")
            engine.index_single_path(file_path)
            row = fetch_file_row(str(db), str(file_path.resolve()))
            self.assertIsNotNone(row)
            self.assertEqual(row["embedding_status"], "indexed")

            file_path.write_text("insurance beta", encoding="utf-8")
            engine.index_single_path(file_path)
            row_after = fetch_file_row(str(db), str(file_path.resolve()))
            self.assertIsNotNone(row_after)
            self.assertEqual(row_after["embedding_status"], "indexed")

            engine.remove_single_path(file_path)
            with sqlite3.connect(db) as conn:
                count = conn.execute("SELECT COUNT(*) FROM files WHERE path = ?", (str(file_path.resolve()),)).fetchone()[0]
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
