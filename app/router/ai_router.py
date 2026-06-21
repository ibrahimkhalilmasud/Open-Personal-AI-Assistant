from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import Settings


@dataclass(slots=True)
class AIRouter:
    available_providers: list[str]

    @classmethod
    def from_settings(cls, settings: Settings) -> "AIRouter":
        providers = ["local"]
        if settings.google_api_key:
            providers.append("gemini")
        if settings.groq_api_key:
            providers.append("groq")
        if settings.openai_api_key:
            providers.append("openai")
        return cls(available_providers=providers)

    def preferred_provider(self) -> str:
        return self.available_providers[0]
