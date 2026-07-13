from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/memory", tags=["memory"], dependencies=[Depends(api_key_auth)])


@router.get("")
def get_memory(request: Request) -> dict[str, object]:
    return request.app.state.services.memory.overview()


@router.post("/refresh")
def refresh_memory(request: Request) -> dict[str, object]:
    summary = request.app.state.services.memory.refresh()
    return {"status": "ok", "summary": summary}


@router.get("/search")
def search_memory(request: Request, q: str) -> dict[str, object]:
    return request.app.state.services.memory.search(q)


@router.post("/conversations")
def add_conversation(request: Request, payload: dict[str, object]) -> dict[str, object]:
    request.app.state.services.memory.add_conversation(
        question=str(payload.get("question", "")),
        answer=str(payload.get("answer", "")),
        referenced_documents=list(payload.get("referenced_documents", [])),
        ai_provider=str(payload.get("ai_provider", "api")),
        confidence=float(payload.get("confidence", 0.5)),
    )
    return {"status": "ok"}


@router.put("/preferences/{key}")
def set_preference(request: Request, key: str, payload: dict[str, object]) -> dict[str, object]:
    request.app.state.services.memory.set_preference(
        key=key,
        value=str(payload.get("value", "")),
        confidence=float(payload.get("confidence", 0.8)),
    )
    return {"status": "ok", "key": key}


@router.get("/projects/{name}")
def get_project(request: Request, name: str) -> dict[str, object]:
    return request.app.state.services.memory.project(name)


@router.get("/persons/{name}")
def get_person(request: Request, name: str) -> dict[str, object]:
    return request.app.state.services.memory.person(name)
