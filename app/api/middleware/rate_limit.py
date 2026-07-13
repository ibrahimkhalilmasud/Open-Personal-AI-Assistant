from __future__ import annotations

from fastapi import Request


async def rate_limit_middleware(request: Request, call_next):
    # Reserved for future per-user/per-key rate limiting.
    return await call_next(request)
