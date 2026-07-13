# API REFERENCE

## Purpose
Document all REST endpoints implemented in `app/api/server.py` and `app/api/routes/*`.

## Audience
API consumers and SDK users.

## Prerequisites
Run server: `python main.py --api`.

## Authentication
- Protected endpoints require `X-API-Key`.
- Create key: `POST /api/v1/system/api-keys` with `{ "name": "sdk" }`.

## Step-by-step
Base URL: `http://127.0.0.1:8000`

### Public endpoints
- `GET /` -> app name/version
- `GET /health`
- `GET /status`
- `GET /metrics`
- `GET /docs`
- `GET /openapi.json`

### API key endpoint
- `POST /api/v1/system/api-keys`

### Search
- `GET /api/v1/search?q=<query>&top_k=10&folder=&file_type=&after=&before=`
- `POST /api/v1/search` body: `{ "query": "...", "top_k": 10, "folder": "", "file_type": "", "after": "", "before": "" }`

### Memory
- `GET /api/v1/memory`
- `POST /api/v1/memory/refresh`
- `GET /api/v1/memory/search?q=<query>`
- `POST /api/v1/memory/conversations` body: `{ "question": "", "answer": "", "referenced_documents": [], "ai_provider": "api", "confidence": 0.5 }`
- `PUT /api/v1/memory/preferences/{key}` body: `{ "value": "", "confidence": 0.8 }`
- `GET /api/v1/memory/projects/{name}`
- `GET /api/v1/memory/persons/{name}`

### Vault
- `GET /api/v1/vault`
- `POST /api/v1/vault/scan`

### RAG
- `POST /api/v1/rag/ask` body: `{ "question": "...", "model": "optional" }`

### Tasks
- `GET /api/v1/tasks?status=<optional>`
- `POST /api/v1/tasks/plan` body: `{ "request": "...", "workflow": "" }`
- `POST /api/v1/tasks/execute` body optional: `{ "approve_pending": true }`
- `GET /api/v1/tasks/status`
- `DELETE /api/v1/tasks/{task_id}`

### Workflows
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{name}`
- `POST /api/v1/workflows/{name}/tasks`

### Tools
- `GET /api/v1/tools`
- `POST /api/v1/tools` body: `{ "name": "...", "metadata_json": "{}", "enabled": true }`
- `PUT /api/v1/tools/{name}` body same as POST
- `DELETE /api/v1/tools/{name}`

### Plugins
- `GET /api/v1/plugins`
- `POST /api/v1/plugins` body: `{ "name": "...", "metadata_json": "{}", "enabled": true }`
- `PUT /api/v1/plugins/{name}`
- `DELETE /api/v1/plugins/{name}`

### System
- `GET /api/v1/system`
- `GET /api/v1/system/config`

## Error responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "request_id": "...",
    "details": []
  }
}
```
Common statuses: `401` missing key, `403` invalid key, `404` resource not found, `422` validation error.

## Examples
```bash
curl -X POST http://127.0.0.1:8000/api/v1/system/api-keys -H "Content-Type: application/json" -d '{"name":"sdk"}'
```

## Troubleshooting
If protected endpoint returns 401/403, regenerate key and include `X-API-Key` header.

## Related documents
- [SDK_GUIDE.md](SDK_GUIDE.md)
- [SECURITY.md](SECURITY.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
