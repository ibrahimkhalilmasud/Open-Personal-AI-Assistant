from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.plugins.manifest import PluginManifest


@dataclass(slots=True)
class PluginValidationResult:
    valid: bool
    errors: list[str]


def validate_plugin_directory(plugin_dir: Path) -> PluginValidationResult:
    errors: list[str] = []
    required = ["manifest.json", "plugin.py", "README.md"]
    for item in required:
        if not (plugin_dir / item).exists():
            errors.append(f"Missing required file: {item}")

    manifest_path = plugin_dir / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = PluginManifest.from_file(manifest_path)
            if not manifest.name:
                errors.append("manifest.name is required")
            if not manifest.version:
                errors.append("manifest.version is required")
            if not manifest.author:
                errors.append("manifest.author is required")
            if not manifest.description:
                errors.append("manifest.description is required")
            if not manifest.minimum_application_version:
                errors.append("manifest.minimum_application_version is required")
        except Exception as exc:
            errors.append(f"Invalid manifest.json: {exc}")

    return PluginValidationResult(valid=not errors, errors=errors)
