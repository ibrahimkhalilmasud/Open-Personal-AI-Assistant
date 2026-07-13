from __future__ import annotations

import importlib.util
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

from app.database.sqlite_db import initialize_database
from app.plugins.manifest import PluginManifest
from app.plugins.sandbox import PluginSandbox
from app.plugins.sdk import PluginBase
from app.plugins.validator import PluginValidationResult, validate_plugin_directory
from app.tools.tool_registry import ToolRegistry


@dataclass(slots=True)
class LoadedPlugin:
    manifest: PluginManifest
    plugin: PluginBase
    module: ModuleType
    path: Path


class PluginLoader:
    def __init__(
        self,
        database_path: str,
        tool_registry: ToolRegistry,
        plugins_root: str = "plugins",
        sandbox: PluginSandbox | None = None,
    ) -> None:
        self.database_path = database_path
        self.tool_registry = tool_registry
        self.plugins_root = Path(plugins_root)
        self.plugins_root.mkdir(parents=True, exist_ok=True)
        self.sandbox = sandbox or PluginSandbox()
        self._loaded: dict[str, LoadedPlugin] = {}
        self._initialize()

    def _initialize(self) -> None:
        initialize_database(self.database_path)

    def discover(self) -> list[str]:
        candidates = []
        for child in sorted(self.plugins_root.iterdir(), key=lambda item: item.name):
            if child.is_dir() and (child / "manifest.json").exists():
                candidates.append(child.name)
        return candidates

    def validate_plugin(self, plugin_name: str) -> PluginValidationResult:
        plugin_dir = self.plugins_root / plugin_name
        if not plugin_dir.exists():
            return PluginValidationResult(valid=False, errors=[f"Plugin not found: {plugin_name}"])
        return validate_plugin_directory(plugin_dir)

    def load_plugin(self, plugin_name: str) -> tuple[bool, str]:
        validation = self.validate_plugin(plugin_name)
        if not validation.valid:
            message = "; ".join(validation.errors)
            self._record(plugin_name, "load", "failed", message)
            return False, message

        plugin_dir = self.plugins_root / plugin_name
        manifest = PluginManifest.from_file(plugin_dir / "manifest.json")
        allowed, blocked = self.sandbox.enforce(manifest.name, manifest.required_permissions)
        if not allowed:
            message = f"Sandbox rejected permissions: {', '.join(blocked)}"
            self._record(plugin_name, "load", "failed", message)
            return False, message

        spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}.plugin", plugin_dir / "plugin.py")
        if spec is None or spec.loader is None:
            message = "Unable to import plugin module"
            self._record(plugin_name, "load", "failed", message)
            return False, message
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        factory = getattr(module, "create_plugin", None)
        if factory is None:
            message = "plugin.py must expose create_plugin()"
            self._record(plugin_name, "load", "failed", message)
            return False, message

        plugin = factory()
        if not isinstance(plugin, PluginBase):
            message = "create_plugin() must return PluginBase"
            self._record(plugin_name, "load", "failed", message)
            return False, message

        plugin.initialize()
        registered = plugin.register_tools(self.tool_registry)
        self._loaded[manifest.name] = LoadedPlugin(manifest=manifest, plugin=plugin, module=module, path=plugin_dir)
        self._upsert_plugin(manifest, status="loaded")
        self._record(plugin_name, "load", "completed", f"registered_tools={len(registered)}")
        return True, f"Plugin '{manifest.name}' loaded"

    def unload_plugin(self, plugin_name: str) -> tuple[bool, str]:
        loaded = self._loaded.get(plugin_name)
        if loaded is None:
            return False, f"Plugin '{plugin_name}' is not loaded"

        loaded.plugin.unregister_tools(self.tool_registry)
        loaded.plugin.cleanup()
        self._loaded.pop(plugin_name, None)
        self._upsert_plugin(loaded.manifest, status="unloaded")
        self._record(plugin_name, "unload", "completed", "plugin unloaded")
        return True, f"Plugin '{plugin_name}' unloaded"

    def reload_plugin(self, plugin_name: str) -> tuple[bool, str]:
        if plugin_name in self._loaded:
            self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)

    def list_plugins(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                """
                SELECT name, version, author, description, minimum_application_version,
                       supported_platforms, supported_agents, required_permissions, status, updated_at
                FROM plugins
                ORDER BY name ASC
                """
            ).fetchall()
        return [
            {
                "name": row[0],
                "version": row[1],
                "author": row[2],
                "description": row[3],
                "minimum_application_version": row[4],
                "supported_platforms": row[5],
                "supported_agents": row[6],
                "required_permissions": row[7],
                "status": row[8],
                "updated_at": row[9],
            }
            for row in rows
        ]

    def _upsert_plugin(self, manifest: PluginManifest, status: str) -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO plugins (
                    name, version, author, description, minimum_application_version,
                    supported_platforms, supported_agents, required_permissions, status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    version=excluded.version,
                    author=excluded.author,
                    description=excluded.description,
                    minimum_application_version=excluded.minimum_application_version,
                    supported_platforms=excluded.supported_platforms,
                    supported_agents=excluded.supported_agents,
                    required_permissions=excluded.required_permissions,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    manifest.name,
                    manifest.version,
                    manifest.author,
                    manifest.description,
                    manifest.minimum_application_version,
                    ",".join(manifest.supported_platforms),
                    ",".join(manifest.supported_agents),
                    ",".join(manifest.required_permissions),
                    status,
                    now,
                ),
            )
            conn.commit()

    def _record(self, plugin_name: str, action: str, status: str, message: str) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO plugin_history (plugin_name, action, status, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (plugin_name, action, status, message, datetime.now(UTC).isoformat()),
            )
            conn.commit()
