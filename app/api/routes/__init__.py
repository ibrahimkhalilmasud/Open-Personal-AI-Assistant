from app.api.routes.memory import router as memory_router
from app.api.routes.plugins import router as plugins_router
from app.api.routes.rag import router as rag_router
from app.api.routes.search import router as search_router
from app.api.routes.system import router as system_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.tools import router as tools_router
from app.api.routes.vault import router as vault_router
from app.api.routes.workflows import router as workflows_router

__all__ = [
    "memory_router",
    "plugins_router",
    "rag_router",
    "search_router",
    "system_router",
    "tasks_router",
    "tools_router",
    "vault_router",
    "workflows_router",
]
