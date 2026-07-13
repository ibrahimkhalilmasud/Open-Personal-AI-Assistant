import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.database.sqlite_db import initialize_database


class Phase8APITests(unittest.TestCase):
    def _fake_system(self, db_path: str):
        settings = Settings(database=db_path, vector_db=str(Path(db_path).parent / "vector"), vault_path=str(Path(db_path).parent))
        Path(settings.vector_db).mkdir(parents=True, exist_ok=True)
        initialize_database(settings.database)
        return SimpleNamespace(
            settings=settings,
            router=SimpleNamespace(available_providers=["ollama"]),
            summary=lambda: "ok",
            bootstrap=lambda: None,
        )

    def test_health_and_api_key_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "phase8.db")
            fake_system = self._fake_system(db_path)

            with patch("app.api.server.create_system", return_value=fake_system):
                from app.api.server import create_app

                client = TestClient(create_app())

                health_response = client.get("/health")
                self.assertEqual(health_response.status_code, 200)
                self.assertEqual(health_response.json()["status"], "ok")
                self.assertIn("X-Request-ID", health_response.headers)

                status_response = client.get("/status")
                self.assertEqual(status_response.status_code, 200)

                metrics_response = client.get("/metrics")
                self.assertEqual(metrics_response.status_code, 200)

                unauthorized = client.get("/api/v1/tools")
                self.assertEqual(unauthorized.status_code, 401)

                key_response = client.post("/api/v1/system/api-keys", json={"name": "test-sdk"})
                self.assertEqual(key_response.status_code, 200)
                api_key = key_response.json()["api_key"]

                authorized = client.get("/api/v1/tools", headers={"X-API-Key": api_key})
                self.assertEqual(authorized.status_code, 200)
                self.assertIn("tools", authorized.json())


if __name__ == "__main__":
    unittest.main()
