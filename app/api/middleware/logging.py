from __future__ import annotations

from fastapi import Request

from app.logging import get_application_logger


logger = get_application_logger("api")


async def logging_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info(
        "api_request | method=%s path=%s status=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        getattr(request.state, "request_id", ""),
    )
    return response
