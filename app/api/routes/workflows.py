from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.auth import api_key_auth

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"], dependencies=[Depends(api_key_auth)])


@router.get("")
def list_workflows(request: Request) -> dict[str, object]:
    workflows = request.app.state.services.workflows.list_workflows()
    return {"count": len(workflows), "workflows": workflows}


@router.get("/{name}")
def get_workflow(request: Request, name: str) -> dict[str, object]:
    workflow = request.app.state.services.workflows.get_workflow(name)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"name": name, "steps": workflow}


@router.post("/{name}/tasks")
def run_workflow(request: Request, name: str) -> dict[str, object]:
    tasks = request.app.state.services.workflows.create_tasks(name)
    return {"workflow": name, "count": len(tasks), "tasks": tasks}
