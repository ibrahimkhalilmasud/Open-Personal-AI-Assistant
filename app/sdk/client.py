from __future__ import annotations

from typing import Any

import requests

from app.sdk.auth import APIKeyAuth
from app.sdk.errors import APIError
from app.sdk.helpers import join_url
from app.sdk.models import AskResponse, SearchResponse


class Client:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: str | None = None, timeout: int = 30) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.auth = APIKeyAuth(api_key) if api_key else None

    def search(self, query: str, top_k: int = 10) -> SearchResponse:
        payload = self._request("GET", "/api/v1/search", params={"q": query, "top_k": top_k})
        return SearchResponse(query=str(payload.get("query", query)), count=int(payload.get("count", 0)), results=list(payload.get("results", [])))

    def memory(self, query: str) -> dict[str, object]:
        return self._request("GET", "/api/v1/memory/search", params={"q": query})

    def ask(self, question: str, model: str | None = None) -> AskResponse:
        payload = self._request("POST", "/api/v1/rag/ask", json={"question": question, "model": model})
        return AskResponse(
            answer=str(payload.get("answer", "")),
            confidence=float(payload.get("confidence", 0.0)),
            confidence_label=str(payload.get("confidence_label", "Unknown")),
            citations=list(payload.get("citations", [])),
            provider=str(payload.get("provider", "")),
            model=str(payload.get("model", "")),
        )

    def health(self) -> dict[str, object]:
        return self._request("GET", "/health")

    def status(self) -> dict[str, object]:
        return self._request("GET", "/status")

    def metrics(self) -> dict[str, object]:
        return self._request("GET", "/metrics")

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, object]:
        headers = dict(kwargs.pop("headers", {}))
        if self.auth is not None:
            headers.update(self.auth.headers())

        response = requests.request(
            method=method,
            url=join_url(self.base_url, path),
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        if response.status_code >= 400:
            try:
                payload = response.json()
            except Exception:
                payload = response.text
            raise APIError(response.status_code, payload)

        data = response.json()
        if not isinstance(data, dict):
            return {"value": data}
        return data
