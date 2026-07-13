from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/system", tags=["system"], dependencies=[Depends(api_key_auth)])


@router.get("")
def system_summary(request: Request) -> dict[str, object]:
    return {
        "summary": request.app.state.system.summary(),
        "metrics": request.app.state.services.system.metrics(),
    }


@router.get("/config")
def system_config(request: Request) -> dict[str, object]:
    return request.app.state.services.config.current()
