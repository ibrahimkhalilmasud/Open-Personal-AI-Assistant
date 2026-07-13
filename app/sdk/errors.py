from __future__ import annotations


class SDKError(Exception):
    pass


class APIError(SDKError):
    def __init__(self, status_code: int, payload: object) -> None:
        super().__init__(f"API error ({status_code}): {payload}")
        self.status_code = status_code
        self.payload = payload
