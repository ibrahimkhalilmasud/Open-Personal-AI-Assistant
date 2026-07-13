from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable

import requests

from app.ai.providers import LOCAL_MODELS
from app.config.settings import Settings


class RouterGenerationError(RuntimeError):
    pass


@dataclass(slots=True)
class AIRouter:
    settings: Settings
    available_providers: list[str]

    @classmethod
    def from_settings(cls, settings: Settings) -> "AIRouter":
        providers = ["ollama"]
        if settings.google_api_key:
            providers.append("gemini")
        if settings.groq_api_key:
            providers.append("groq")
        if settings.openai_api_key:
            providers.append("openai")
        return cls(settings=settings, available_providers=providers)

    def preferred_provider(self) -> str:
        return self.available_providers[0]

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        selected_model: str | None = None,
        stream: bool = False,
        on_token: Callable[[str], None] | None = None,
    ) -> dict[str, str | bool]:
        model = (selected_model or self.settings.default_model).strip() or self.settings.default_model
        providers = self._provider_chain(model)

        failures: list[str] = []
        for provider in providers:
            try:
                answer, streamed = self._generate_with_provider(
                    provider=provider,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    stream=stream,
                    on_token=on_token,
                )
                return {
                    "answer": answer,
                    "provider": provider,
                    "model": model,
                    "streamed": streamed,
                }
            except Exception as exc:
                failures.append(f"{provider}: {exc}")

        raise RouterGenerationError("All providers failed | " + " | ".join(failures))

    def _provider_chain(self, model: str) -> list[str]:
        value = model.lower()
        if value.startswith("gemini"):
            prioritized = ["gemini"]
        elif value.startswith("gpt") or value.startswith("o"):
            prioritized = ["openai"]
        elif value.startswith("llama") or value.startswith("mixtral"):
            prioritized = ["groq"]
        elif any(value.startswith(local) for local in LOCAL_MODELS):
            prioritized = ["ollama"]
        else:
            prioritized = []

        for provider in self.available_providers:
            if provider not in prioritized:
                prioritized.append(provider)
        return prioritized

    def _generate_with_provider(
        self,
        *,
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        stream: bool,
        on_token: Callable[[str], None] | None,
    ) -> tuple[str, bool]:
        if provider == "ollama":
            return self._generate_ollama(model, system_prompt, user_prompt, stream, on_token)
        if provider == "gemini":
            return self._generate_gemini(model, system_prompt, user_prompt)
        if provider == "groq":
            return self._generate_openai_compatible(
                base_url="https://api.groq.com/openai/v1/chat/completions",
                api_key=self.settings.groq_api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                stream=stream,
                on_token=on_token,
            )
        if provider == "openai":
            return self._generate_openai_compatible(
                base_url="https://api.openai.com/v1/chat/completions",
                api_key=self.settings.openai_api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                stream=stream,
                on_token=on_token,
            )
        raise RouterGenerationError(f"Unsupported provider: {provider}")

    def _generate_ollama(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        stream: bool,
        on_token: Callable[[str], None] | None,
    ) -> tuple[str, bool]:
        response = requests.post(
            f"{self.settings.ollama_url.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": stream,
            },
            stream=stream,
            timeout=self.settings.model_timeout_seconds,
        )
        response.raise_for_status()

        if not stream:
            payload = response.json()
            return str(payload.get("response", "")).strip(), False

        collected: list[str] = []
        for raw in response.iter_lines(decode_unicode=True):
            if not raw:
                continue
            chunk = json.loads(raw)
            token = str(chunk.get("response", ""))
            if token:
                collected.append(token)
                if on_token is not None:
                    on_token(token)
        return "".join(collected).strip(), True

    def _generate_openai_compatible(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        stream: bool,
        on_token: Callable[[str], None] | None,
    ) -> tuple[str, bool]:
        headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": stream,
        }

        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            stream=stream,
            timeout=self.settings.model_timeout_seconds,
        )
        response.raise_for_status()

        if not stream:
            body = response.json()
            choices = body.get("choices") or []
            if not choices:
                return "", False
            message = choices[0].get("message") or {}
            return str(message.get("content", "")).strip(), False

        tokens: list[str] = []
        for raw in response.iter_lines(decode_unicode=True):
            if not raw:
                continue
            line = raw.strip()
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line or line == "[DONE]":
                continue
            chunk = json.loads(line)
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            token = str(delta.get("content", ""))
            if token:
                tokens.append(token)
                if on_token is not None:
                    on_token(token)
        return "".join(tokens).strip(), True

    def _generate_gemini(self, model: str, system_prompt: str, user_prompt: str) -> tuple[str, bool]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        response = requests.post(
            endpoint,
            params={"key": self.settings.google_api_key},
            json={
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_prompt}]}],
            },
            timeout=self.settings.model_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        candidates = body.get("candidates") or []
        if not candidates:
            return "", False
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        text = "".join(str(part.get("text", "")) for part in parts)
        return text.strip(), False
