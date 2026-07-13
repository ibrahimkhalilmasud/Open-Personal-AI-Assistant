from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/vault", tags=["vault"], dependencies=[Depends(api_key_auth)])


@router.get("")
def vault_stats(request: Request) -> dict[str, object]:
    return request.app.state.services.vault.stats()


@router.post("/scan")
def vault_scan(request: Request) -> dict[str, object]:
    return request.app.state.services.vault.scan()
