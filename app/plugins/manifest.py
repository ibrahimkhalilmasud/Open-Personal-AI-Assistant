from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PluginManifest:
    name: str
    version: str
    author: str
    description: str
    minimum_application_version: str
    supported_platforms: list[str] = field(default_factory=list)
    supported_agents: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "PluginManifest":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            name=str(payload.get("name", "")).strip(),
            version=str(payload.get("version", "")).strip(),
            author=str(payload.get("author", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            minimum_application_version=str(payload.get("minimum_application_version", "")).strip(),
            supported_platforms=list(payload.get("supported_platforms", [])),
            supported_agents=list(payload.get("supported_agents", [])),
            required_permissions=list(payload.get("required_permissions", [])),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "minimum_application_version": self.minimum_application_version,
            "supported_platforms": list(self.supported_platforms),
            "supported_agents": list(self.supported_agents),
            "required_permissions": list(self.required_permissions),
        }
