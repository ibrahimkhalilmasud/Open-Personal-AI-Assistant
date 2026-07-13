from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.prompts import PromptPackage
from app.router.ai_router import AIRouter


@dataclass(slots=True)
class GeneratedAnswer:
    answer: str
    provider: str
    model: str
    streamed: bool


class AnswerGenerator:
    def __init__(self, router: AIRouter) -> None:
        self.router = router

    def generate(
        self,
        prompts: PromptPackage,
        *,
        model: str | None = None,
        stream: bool = False,
        on_token: Callable[[str], None] | None = None,
    ) -> GeneratedAnswer:
        result = self.router.generate(
            system_prompt=prompts.system_prompt,
            user_prompt=prompts.user_prompt,
            selected_model=model,
            stream=stream,
            on_token=on_token,
        )
        return GeneratedAnswer(
            answer=result["answer"],
            provider=result["provider"],
            model=result["model"],
            streamed=bool(result.get("streamed", False)),
        )
