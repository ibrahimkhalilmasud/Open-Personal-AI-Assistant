import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from app.config.settings import Settings
from app.database.sqlite_db import initialize_database
from app.services.config_service import ConfigService
from app.services.health_service import HealthService
from app.services.plugin_service import PluginService
from app.services.system_service import SystemService
from app.services.tool_service import ToolService


class Phase8ServiceTests(unittest.TestCase):
    def _fake_system(self, db_path: str):
        settings = Settings(database=db_path, vector_db=str(Path(db_path).parent / "vector"), vault_path=str(Path(db_path).parent))
        Path(settings.vector_db).mkdir(parents=True, exist_ok=True)
        initialize_database(settings.database)
        return SimpleNamespace(
            settings=settings,
            router=SimpleNamespace(available_providers=["ollama"]),
            summary=lambda: "ok",
        )

    def test_tool_and_plugin_services_are_crud_capable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "phase8.db")
            system = self._fake_system(db_path)

            tools = ToolService(system)
            plugins = PluginService(system)

            tools.upsert_tool("calculator", enabled=True)
            plugins.upsert_plugin("notes", enabled=True)

            self.assertEqual(tools.count(), 1)
            self.assertEqual(plugins.count(), 1)

            self.assertEqual(tools.remove_tool("calculator"), 1)
            self.assertEqual(plugins.remove_plugin("notes"), 1)

    def test_health_config_and_system_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "phase8.db")
            system = self._fake_system(db_path)

            health = HealthService(system).health()
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["database"]["status"], "ok")

            config = ConfigService(system).current()
            self.assertIn("settings", config)
            self.assertIn("loaded_providers", config)

            metrics = SystemService(system).metrics()
            self.assertIn("uptime_seconds", metrics)
            self.assertIn("tool_count", metrics)


if __name__ == "__main__":
    unittest.main()
