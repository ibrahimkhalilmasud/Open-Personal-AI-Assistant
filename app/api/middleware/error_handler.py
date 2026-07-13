from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


def error_payload(code: str, message: str, request_id: str | None = None, details: object = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=error_payload(
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                request_id=getattr(request.state, "request_id", None),
                details=str(exc),
            ),
        )
