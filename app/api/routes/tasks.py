from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"], dependencies=[Depends(api_key_auth)])


@router.get("")
def list_tasks(request: Request, status: str | None = None) -> dict[str, object]:
    tasks = request.app.state.services.tasks.list_tasks(status=status)
    return {"count": len(tasks), "tasks": tasks}


@router.post("/plan")
def plan_tasks(request: Request, payload: dict[str, object]) -> dict[str, object]:
    request_text = str(payload.get("request", "")).strip()
    workflow = str(payload.get("workflow", ""))
    tasks = request.app.state.services.tasks.plan(request=request_text, workflow=workflow)
    return {"count": len(tasks), "tasks": tasks}


@router.post("/execute")
def execute_tasks(request: Request, payload: dict[str, object] | None = None) -> dict[str, object]:
    approve = True if payload is None else bool(payload.get("approve_pending", True))
    results = request.app.state.services.tasks.execute(approve_pending=approve)
    return {"count": len(results), "results": results}


@router.get("/status")
def task_statuses(request: Request) -> dict[str, int]:
    return request.app.state.services.tasks.statuses()


@router.delete("/{task_id}")
def delete_task(request: Request, task_id: str) -> dict[str, object]:
    with sqlite3.connect(request.app.state.system.settings.database) as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()
    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted", "task_id": task_id}
