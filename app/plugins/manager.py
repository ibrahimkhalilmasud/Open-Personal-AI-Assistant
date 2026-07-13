from __future__ import annotations

from app.plugins.loader import PluginLoader


class PluginManager:
    def __init__(self, loader: PluginLoader) -> None:
        self.loader = loader

    def discover_and_load(self) -> list[tuple[str, bool, str]]:
        results: list[tuple[str, bool, str]] = []
        for plugin_name in self.loader.discover():
            ok, message = self.loader.load_plugin(plugin_name)
            results.append((plugin_name, ok, message))
        return results

    def load_plugin(self, plugin_name: str) -> tuple[bool, str]:
        return self.loader.load_plugin(plugin_name)

    def unload_plugin(self, plugin_name: str) -> tuple[bool, str]:
        return self.loader.unload_plugin(plugin_name)

    def reload_plugin(self, plugin_name: str) -> tuple[bool, str]:
        return self.loader.reload_plugin(plugin_name)

    def list_plugins(self) -> list[dict[str, object]]:
        return self.loader.list_plugins()

    def validate_plugin(self, plugin_name: str) -> tuple[bool, list[str]]:
        result = self.loader.validate_plugin(plugin_name)
        return result.valid, result.errors
