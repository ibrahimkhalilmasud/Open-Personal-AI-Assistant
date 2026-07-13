from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import create_api_key
from app.api.middleware import (
    catch_exceptions_middleware,
    error_payload,
    logging_middleware,
    metrics_middleware,
    rate_limit_middleware,
    request_context_middleware,
)
from app.api.routes import (
    memory_router,
    plugins_router,
    rag_router,
    search_router,
    system_router,
    tasks_router,
    tools_router,
    vault_router,
    workflows_router,
)
from app.core.system import create_system
from app.database.sqlite_db import initialize_database
from app.services import (
    ConfigService,
    HealthService,
    MemoryService,
    PluginService,
    RAGService,
    SearchService,
    SystemService,
    TaskService,
    ToolService,
    VaultService,
    WorkflowService,
)


@dataclass(slots=True)
class ServiceContainer:
    search: SearchService
    memory: MemoryService
    rag: RAGService
    vault: VaultService
    tasks: TaskService
    workflows: WorkflowService
    tools: ToolService
    plugins: PluginService
    config: ConfigService
    health: HealthService
    system: SystemService


def create_app() -> FastAPI:
    app = FastAPI(
        title="Open Personal AI Assistant API",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
    )

    system = create_system()
    initialize_database(system.settings.database)

    app.state.system = system
    app.state.services = ServiceContainer(
        search=SearchService(system),
        memory=MemoryService(system),
        rag=RAGService(system),
        vault=VaultService(system),
        tasks=TaskService(system),
        workflows=WorkflowService(system),
        tools=ToolService(system),
        plugins=PluginService(system),
        config=ConfigService(system),
        health=HealthService(system),
        system=SystemService(system),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(system.settings.cors_allowed_origins),
        allow_credentials=bool(system.settings.cors_allow_credentials),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    app.middleware("http")(catch_exceptions_middleware)
    app.middleware("http")(request_context_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(metrics_middleware)

    app.include_router(search_router)
    app.include_router(memory_router)
    app.include_router(vault_router)
    app.include_router(rag_router)
    app.include_router(tasks_router)
    app.include_router(workflows_router)
    app.include_router(tools_router)
    app.include_router(plugins_router)
    app.include_router(system_router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"name": "Open Personal AI Assistant API", "version": "v1"}

    @app.get("/health")
    def health() -> dict[str, object]:
        return app.state.services.health.health()

    @app.get("/status")
    def status() -> dict[str, object]:
        return app.state.services.health.status()

    @app.get("/metrics")
    def metrics() -> dict[str, object]:
        return app.state.services.system.metrics()

    @app.post("/api/v1/system/api-keys")
    def create_key(payload: dict[str, object]) -> dict[str, object]:
        name = str(payload.get("name", "sdk")).strip() or "sdk"
        key = create_api_key(
            system.settings.database,
            name=name,
            pepper=system.settings.api_key_hash_pepper,
        )
        return {"name": name, "api_key": key}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                code={401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "RESOURCE_NOT_FOUND"}.get(
                    exc.status_code,
                    "REQUEST_ERROR",
                ),
                message=str(exc.detail),
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_payload(
                code="VALIDATION_ERROR",
                message="Validation failed",
                request_id=getattr(request.state, "request_id", None),
                details=exc.errors(),
            ),
        )

    return app
