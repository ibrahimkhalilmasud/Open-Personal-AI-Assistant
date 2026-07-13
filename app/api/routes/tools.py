from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/tools", tags=["tools"], dependencies=[Depends(api_key_auth)])


@router.get("")
def list_tools(request: Request) -> dict[str, object]:
    tools = request.app.state.services.tools.list_tools()
    return {"count": len(tools), "tools": tools}


@router.post("")
def add_tool(request: Request, payload: dict[str, object]) -> dict[str, object]:
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    request.app.state.services.tools.upsert_tool(
        name=name,
        metadata_json=str(payload.get("metadata_json", "{}")),
        enabled=bool(payload.get("enabled", True)),
    )
    return {"status": "ok", "name": name}


@router.put("/{name}")
def update_tool(request: Request, name: str, payload: dict[str, object]) -> dict[str, object]:
    request.app.state.services.tools.upsert_tool(
        name=name,
        metadata_json=str(payload.get("metadata_json", "{}")),
        enabled=bool(payload.get("enabled", True)),
    )
    return {"status": "ok", "name": name}


@router.delete("/{name}")
def remove_tool(request: Request, name: str) -> dict[str, object]:
    removed = request.app.state.services.tools.remove_tool(name)
    if removed <= 0:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"status": "deleted", "name": name}
