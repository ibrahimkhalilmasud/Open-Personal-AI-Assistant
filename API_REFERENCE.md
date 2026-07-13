# API REFERENCE

## Base

- Base URL: `http://127.0.0.1:8000`
- Versioned API: `/api/v1`
- Auth header for protected endpoints: `X-API-Key: <key>`

## Public endpoints

- `GET /health`
- `GET /status`
- `GET /metrics`
- `GET /docs`
- `GET /openapi.json`

## API key management

- `POST /api/v1/system/api-keys`

## Core resources

- `GET|POST /api/v1/search`
- `GET /api/v1/memory`
- `POST /api/v1/memory/refresh`
- `GET /api/v1/memory/search?q=...`
- `POST /api/v1/memory/conversations`
- `PUT /api/v1/memory/preferences/{key}`
- `GET /api/v1/memory/projects/{name}`
- `GET /api/v1/memory/persons/{name}`
- `POST /api/v1/rag/ask`
- `GET /api/v1/vault`
- `POST /api/v1/vault/scan`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks/plan`
- `POST /api/v1/tasks/execute`
- `GET /api/v1/tasks/status`
- `DELETE /api/v1/tasks/{task_id}`
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{name}`
- `POST /api/v1/workflows/{name}/tasks`
- `GET|POST /api/v1/tools`
- `PUT|DELETE /api/v1/tools/{name}`
- `GET|POST /api/v1/plugins`
- `PUT|DELETE /api/v1/plugins/{name}`
- `GET /api/v1/system`
- `GET /api/v1/system/config`

## Error format

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
