# SERVICE ARCHITECTURE

## Diagram

```text
CLI / SDK / Future Clients
        |
        v
   FastAPI REST API (/api/v1)
        |
        v
      Services
  (search, memory, rag,
   vault, tasks, workflows,
   tools, plugins, config,
   health, system)
        |
        v
 Existing Core Modules
(memory, graph, retrieval, rag,
 vault, task engine, workflow engine)
```

## Design principles

- Clients only talk to API/service layer.
- Business logic stays in existing reusable modules.
- Versioning boundary at `/api/v1`.
- Structured errors and request IDs for observability.
- Auth via API keys now; OAuth/JWT/RBAC-ready extension points are isolated in `app/api/auth`.
