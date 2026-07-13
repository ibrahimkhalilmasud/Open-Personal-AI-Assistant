from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SandboxPolicy:
    allow_database_write: bool = False
    allow_filesystem_write: bool = False
    allow_internet: bool = False
    trusted_plugins: set[str] = field(default_factory=set)


class PluginSandbox:
    def __init__(self, policy: SandboxPolicy | None = None) -> None:
        self.policy = policy or SandboxPolicy()

    def is_trusted(self, plugin_name: str) -> bool:
        return plugin_name in self.policy.trusted_plugins

    def enforce(self, plugin_name: str, required_permissions: list[str]) -> tuple[bool, list[str]]:
        if self.is_trusted(plugin_name):
            return True, []

        blocked: list[str] = []
        if not self.policy.allow_database_write and "write_vault" in required_permissions:
            blocked.append("write_vault")
        if not self.policy.allow_filesystem_write and "delete_files" in required_permissions:
            blocked.append("delete_files")
        if not self.policy.allow_internet and "internet_access" in required_permissions:
            blocked.append("internet_access")
        if not self.policy.allow_internet and "external_api_access" in required_permissions:
            blocked.append("external_api_access")
        return not blocked, blocked
