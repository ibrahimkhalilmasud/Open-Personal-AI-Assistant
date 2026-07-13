# DEVELOPER GUIDE

## Architecture (Phase 8)

`Client -> REST API (/api/v1) -> Service Layer -> Core modules (memory/graph/rag/vault/tasks/workflows)`

## New module groups

- `app/services/`: stable internal service interfaces
- `app/api/`: FastAPI server, routes, middleware, auth
- `app/sdk/`: internal Python SDK wrapper for REST API

## API versioning

- Current version prefix: `/api/v1/`
- Route grouping and server wiring are version-isolated to support `/api/v2/` in future.

## Auth and middleware

- API key auth via `X-API-Key`
- Request ID and latency headers
- Request logging
- Metrics + audit persistence (`api_requests`, `api_audit_log`)
- Structured exception responses
- CORS and GZip enabled

## New operational tables

- `api_keys`
- `api_requests`
- `service_metrics`
- `service_health`
- `api_audit_log`
- `installed_tools`
- `installed_plugins`

## Run tests

```bash
python -m unittest discover -s tests -q
```
