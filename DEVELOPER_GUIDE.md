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

## Tool architecture (Phase 7)

- Base contract: `app/tools/base_tool.py`
  - required metadata: `tool_id`, `name`, `version`, `description`, `category`, `author`, `permissions`, `input_schema`, `output_schema`
  - lifecycle methods: `initialize()`, `validate()`, `execute()`, `cleanup()`
- Discovery and registration: `app/tools/tool_discovery.py`, `app/tools/tool_registry.py`
- Execution engine: `app/tools/tool_executor.py`
  - execution metadata: `execution_id`, `agent_name`, `workflow_name`, `start_time`, `finish_time`, `duration`, `status`, `tool_inputs`, `tool_outputs`, `confidence`, `citations`
  - persistent history: `tool_history`, `tool_metrics`
- Permission and validation:
  - `app/tools/tool_permissions.py`
  - `app/tools/tool_validation.py`
- Chaining support: `ToolExecutor.execute_chain()`

## Plugin SDK

- `app/plugins/manifest.py` defines plugin metadata contract.
- `app/plugins/sdk.py` defines `PluginBase` lifecycle contract.
- `app/plugins/validator.py` enforces required plugin files and manifest fields.
- `app/plugins/loader.py` supports `load_plugin`, `unload_plugin`, `reload_plugin`, `list_plugins`, and `validate_plugin`.
- `app/plugins/sandbox.py` enforces untrusted plugin permission restrictions.
- `app/plugins/manager.py` orchestrates discovery and lifecycle operations.

## SQLite schema additions (phase 7)

- `tools`
- `tool_history`
- `plugins`
- `plugin_history`
- `permissions`
- `tool_metrics`

## Run tests

```bash
python -m unittest discover -s tests -q
```
