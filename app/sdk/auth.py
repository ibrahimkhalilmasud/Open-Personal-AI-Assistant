from __future__ import annotations


class APIKeyAuth:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key}
