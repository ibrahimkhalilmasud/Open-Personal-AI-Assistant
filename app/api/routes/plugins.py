from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"], dependencies=[Depends(api_key_auth)])


@router.get("")
def list_plugins(request: Request) -> dict[str, object]:
    plugins = request.app.state.services.plugins.list_plugins()
    return {"count": len(plugins), "plugins": plugins}


@router.post("")
def add_plugin(request: Request, payload: dict[str, object]) -> dict[str, object]:
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    request.app.state.services.plugins.upsert_plugin(
        name=name,
        metadata_json=str(payload.get("metadata_json", "{}")),
        enabled=bool(payload.get("enabled", True)),
    )
    return {"status": "ok", "name": name}


@router.put("/{name}")
def update_plugin(request: Request, name: str, payload: dict[str, object]) -> dict[str, object]:
    request.app.state.services.plugins.upsert_plugin(
        name=name,
        metadata_json=str(payload.get("metadata_json", "{}")),
        enabled=bool(payload.get("enabled", True)),
    )
    return {"status": "ok", "name": name}


@router.delete("/{name}")
def remove_plugin(request: Request, name: str) -> dict[str, object]:
    removed = request.app.state.services.plugins.remove_plugin(name)
    if removed <= 0:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"status": "deleted", "name": name}
