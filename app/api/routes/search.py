from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/search", tags=["search"], dependencies=[Depends(api_key_auth)])


@router.get("")
def search_get(
    request: Request,
    q: str,
    top_k: int = 10,
    folder: str | None = None,
    file_type: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, object]:
    results = request.app.state.services.search.search(
        query=q,
        top_k=top_k,
        folder=folder,
        file_type=file_type,
        after=after,
        before=before,
    )
    return {"query": q, "count": len(results), "results": results}


@router.post("")
def search_post(request: Request, payload: dict[str, object]) -> dict[str, object]:
    query = str(payload.get("query", "")).strip()
    results = request.app.state.services.search.search(
        query=query,
        top_k=int(payload.get("top_k", 10) or 10),
        folder=payload.get("folder"),
        file_type=payload.get("file_type"),
        after=payload.get("after"),
        before=payload.get("before"),
    )
    return {"query": query, "count": len(results), "results": results}
