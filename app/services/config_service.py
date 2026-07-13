from __future__ import annotations

from dataclasses import asdict

from app.ai.providers import PROVIDER_PRIORITY
from app.services.base_service import BaseService
from app.services.plugin_service import PluginService
from app.services.tool_service import ToolService


class ConfigService(BaseService):
    def __init__(self, system) -> None:
        super().__init__(system)
        self.plugins = PluginService(system)
        self.tools = ToolService(system)

    def current(self) -> dict[str, object]:
        settings = asdict(self.settings)
        settings.pop("openai_api_key", None)
        settings.pop("google_api_key", None)
        settings.pop("groq_api_key", None)
        settings.pop("tavily_api_key", None)
        settings.pop("telegram_token", None)
        settings.pop("email_password", None)
        return {
            "settings": settings,
            "loaded_providers": list(self.system.router.available_providers),
            "provider_priority": list(PROVIDER_PRIORITY),
            "enabled_plugins": [item for item in self.plugins.list_plugins() if item["enabled"]],
            "installed_tools": self.tools.list_tools(),
            "active_model": self.settings.default_model,
            "vector_db": {
                "path": self.settings.vector_db,
                "embedding_model": self.settings.embedding_model,
            },
        }
