import os
import tempfile
import unittest
from pathlib import Path

from app.config.settings import load_settings


class SettingsTests(unittest.TestCase):
    def test_load_settings_defaults_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "state" / "db.sqlite")
            vector_path = str(Path(tmp) / "vector")

            os.environ["DATABASE"] = db_path
            os.environ["VECTOR_DB"] = vector_path
            os.environ["ENABLE_CAMERA"] = "true"
            os.environ["AUTO_SCAN"] = "false"
            os.environ["SCAN_INTERVAL"] = "120"
            os.environ["EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"
            os.environ["CHUNK_SIZE"] = "500"
            os.environ["CHUNK_OVERLAP"] = "100"

            settings = load_settings()

            self.assertEqual(settings.database, db_path)
            self.assertEqual(settings.vector_db, vector_path)
            self.assertTrue(settings.enable_camera)
            self.assertFalse(settings.auto_scan)
            self.assertEqual(settings.scan_interval, 120)
            self.assertEqual(settings.embedding_model, "all-MiniLM-L6-v2")
            self.assertEqual(settings.chunk_size, 500)
            self.assertEqual(settings.chunk_overlap, 100)
            self.assertTrue(Path(db_path).parent.exists())
            self.assertTrue(Path(vector_path).exists())


if __name__ == "__main__":
    unittest.main()
