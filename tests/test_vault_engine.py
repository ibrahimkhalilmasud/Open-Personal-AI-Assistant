import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.config.settings import load_settings
from app.vault.engine import VaultEngine


class VaultEngineTests(unittest.TestCase):
    def test_full_scan_detects_new_changed_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()
            db_path = Path(tmp) / "data" / "database.db"

            os.environ["VAULT_PATH"] = str(vault)
            os.environ["DATABASE"] = str(db_path)

            settings = load_settings()
            engine = VaultEngine(settings)

            first_file = vault / "report.txt"
            first_file.write_text("version-1", encoding="utf-8")

            first = engine.full_scan()
            self.assertEqual(first["new"], 1)
            self.assertEqual(first["changed"], 0)
            self.assertEqual(first["deleted"], 0)

            first_file.write_text("version-2", encoding="utf-8")
            second = engine.full_scan()
            self.assertEqual(second["new"], 0)
            self.assertEqual(second["changed"], 1)
            self.assertEqual(second["deleted"], 0)

            first_file.unlink()
            third = engine.full_scan()
            self.assertEqual(third["new"], 0)
            self.assertEqual(third["changed"], 0)
            self.assertEqual(third["deleted"], 1)

            with sqlite3.connect(db_path) as conn:
                count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
