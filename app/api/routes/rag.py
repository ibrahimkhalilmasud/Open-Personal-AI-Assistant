from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/rag", tags=["rag"], dependencies=[Depends(api_key_auth)])


@router.post("/ask")
def ask(request: Request, payload: dict[str, object]) -> dict[str, object]:
    question = str(payload.get("question", "")).strip()
    model = payload.get("model")
    return request.app.state.services.rag.ask(question=question, model=model)
