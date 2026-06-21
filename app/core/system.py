from dataclasses import dataclass

from app.ai.providers import PROVIDER_PRIORITY
from app.config.settings import Settings, load_settings
from app.database.sqlite_db import initialize_database
from app.router.ai_router import AIRouter


@dataclass(slots=True)
class PersonalAIOS:
    settings: Settings
    router: AIRouter

    def bootstrap(self) -> None:
        initialize_database(self.settings.database)

    def summary(self) -> str:
        return (
            f"AI-Personal-OS initialized | vault={self.settings.vault_path} "
            f"| default_model={self.settings.default_model} "
            f"| providers={','.join(self.router.available_providers)} "
            f"| priority={','.join(PROVIDER_PRIORITY)}"
        )


def create_system() -> PersonalAIOS:
    settings = load_settings()
    router = AIRouter.from_settings(settings)
    system = PersonalAIOS(settings=settings, router=router)
    system.bootstrap()
    return system
