from __future__ import annotations

from app.core.system import PersonalAIOS


class BaseService:
    def __init__(self, system: PersonalAIOS) -> None:
        self.system = system
        self.settings = system.settings
