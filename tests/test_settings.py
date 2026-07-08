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
            env_file = Path(tmp) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        f"DATABASE={db_path}",
                        f"VECTOR_DB={vector_path}",
                        "ENABLE_CAMERA=true",
                        "AUTO_SCAN=false",
                        "SCAN_INTERVAL=120",
                        "EMBEDDING_MODEL=all-MiniLM-L6-v2",
                        "CHUNK_SIZE=500",
                        "CHUNK_OVERLAP=100",
                        "EMBED_BATCH_SIZE=32",
                    ]
                ),
                encoding="utf-8",
            )

            os.environ["OPA_ENV_FILE"] = str(env_file)
            os.environ.pop("DATABASE", None)
            os.environ.pop("VECTOR_DB", None)

            settings = load_settings()

            self.assertEqual(settings.database, db_path)
            self.assertEqual(settings.vector_db, vector_path)
            self.assertTrue(settings.enable_camera)
            self.assertFalse(settings.auto_scan)
            self.assertEqual(settings.scan_interval, 120)
            self.assertEqual(settings.embedding_model, "all-MiniLM-L6-v2")
            self.assertEqual(settings.chunk_size, 500)
            self.assertEqual(settings.chunk_overlap, 100)
            self.assertEqual(settings.embed_batch_size, 32)
            self.assertIn("status=ok", settings.settings_validation_report)
            self.assertTrue(Path(db_path).parent.exists())
            self.assertTrue(Path(vector_path).exists())


if __name__ == "__main__":
    unittest.main()
