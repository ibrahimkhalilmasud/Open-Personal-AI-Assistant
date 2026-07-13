import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database
from app.plugins.loader import PluginLoader
from app.plugins.sandbox import PluginSandbox, SandboxPolicy
from app.tools import ToolRegistry


class Phase7PluginSDKTests(unittest.TestCase):
    def test_plugin_loader_loads_and_unloads_sample_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "plugin.db")
            initialize_database(db_path)

            repo_root = Path(__file__).resolve().parents[1]
            registry = ToolRegistry()
            registry.discover()
            loader = PluginLoader(db_path, registry, plugins_root=str(repo_root / "plugins"))

            valid = loader.validate_plugin("sample_plugin")
            self.assertTrue(valid.valid)

            ok, _ = loader.load_plugin("sample_plugin")
            self.assertTrue(ok)
            self.assertIsNotNone(registry.get_tool("plugin.sample.echo"))

            ok, _ = loader.unload_plugin("sample_plugin")
            self.assertTrue(ok)

    def test_plugin_validator_rejects_missing_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "plugin.db")
            initialize_database(db_path)

            plugins_root = Path(tmp) / "plugins"
            broken = plugins_root / "broken_plugin"
            broken.mkdir(parents=True)
            (broken / "manifest.json").write_text("{}", encoding="utf-8")

            registry = ToolRegistry()
            loader = PluginLoader(db_path, registry, plugins_root=str(plugins_root))
            result = loader.validate_plugin("broken_plugin")
            self.assertFalse(result.valid)
            self.assertTrue(any("Missing required file" in msg for msg in result.errors))

    def test_sandbox_blocks_untrusted_plugin_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "plugin.db")
            initialize_database(db_path)

            plugins_root = Path(tmp) / "plugins"
            plugin_dir = plugins_root / "net_plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "README.md").write_text("test", encoding="utf-8")
            (plugin_dir / "manifest.json").write_text(
                """
                {
                    "name": "net_plugin",
                    "version": "1.0.0",
                    "author": "tests",
                    "description": "blocked plugin",
                    "minimum_application_version": "7.0.0",
                    "supported_platforms": ["linux"],
                    "supported_agents": ["planning-agent"],
                    "required_permissions": ["internet_access"]
                }
                """,
                encoding="utf-8",
            )
            (plugin_dir / "plugin.py").write_text(
                """
from app.plugins.sdk import PluginBase
from app.plugins.manifest import PluginManifest

class P(PluginBase):
    def __init__(self):
        self.manifest = PluginManifest(
            name='net_plugin', version='1.0.0', author='tests', description='blocked plugin',
            minimum_application_version='7.0.0', supported_platforms=['linux'],
            supported_agents=['planning-agent'], required_permissions=['internet_access']
        )
    def initialize(self):
        return
    def register_tools(self, registry):
        return []
    def unregister_tools(self, registry):
        return
    def cleanup(self):
        return

def create_plugin():
    return P()
                """,
                encoding="utf-8",
            )

            policy = SandboxPolicy(allow_internet=False)
            sandbox = PluginSandbox(policy)
            loader = PluginLoader(db_path, ToolRegistry(), plugins_root=str(plugins_root), sandbox=sandbox)
            ok, message = loader.load_plugin("net_plugin")
            self.assertFalse(ok)
            self.assertIn("Sandbox rejected permissions", message)


if __name__ == "__main__":
    unittest.main()
