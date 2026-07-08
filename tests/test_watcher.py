import unittest
from pathlib import Path
from types import SimpleNamespace

from app.config.settings import Settings
from app.vault.engine import VaultEngine

try:
    from app.vault.watcher import VaultEventHandler
except Exception:  # pragma: no cover
    VaultEventHandler = None


@unittest.skipIf(VaultEventHandler is None, "watchdog is not installed")
class WatcherTests(unittest.TestCase):
    def test_should_process_supported_extension(self) -> None:
        settings = Settings(vault_path="/tmp")
        handler = VaultEventHandler(VaultEngine(settings))
        event = SimpleNamespace(is_directory=False, src_path=str(Path("/tmp/file.txt")))
        self.assertTrue(handler._should_process(event))


if __name__ == "__main__":
    unittest.main()
