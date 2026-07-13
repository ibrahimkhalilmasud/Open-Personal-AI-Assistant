# AI-Personal-OS (Open-Personal-AI-Assistant)

Local-first personal knowledge platform with indexing, retrieval, persistent memory, a knowledge graph, and a reusable service/API layer.

## Phase 8 scope (Service Layer + REST API + SDK)

- Service Layer entry points under `app/services/`
- FastAPI server with versioned routes under `app/api/`
- Internal Python SDK under `app/sdk/`
- API key authentication, middleware, health/status/metrics endpoints
- Migration-safe API/service tables (`api_keys`, `api_requests`, `service_metrics`, `service_health`, `api_audit_log`)
Local-first personal knowledge platform with persistent indexing, retrieval, hybrid search, and a persistent memory + knowledge graph engine.

## Phase 7 scope (tool execution framework + plugin SDK)

- persistent vector storage (ChromaDB + durable local fallback)
- incremental indexing using hash + modified date + model/chunk signature
- batch embedding support (`EMBED_BATCH_SIZE`)
- hybrid semantic + keyword + metadata search
- retrieval schema with normalized score and file metadata
- persistent memory layers:
  - conversation memory
  - preference memory
  - project memory
  - knowledge memory (document-supported facts only)
- SQLite-backed knowledge graph:
  - entities
  - relationships
  - timelines
  - summary cache
- rule-based entity extraction and entity resolution with incremental updates
- rotating logs:
  - `logs/application.log`
  - `logs/error.log`
  - `logs/search.log`
  - `logs/scan.log`
  - `logs/watcher.log`
- tool execution framework:
  - `app/tools/base_tool.py` standardized tool contract
  - `app/tools/tool_registry.py` auto discovery/registration
  - `app/tools/tool_executor.py` permission-gated execution + history
  - `app/tools/tool_permissions.py` principal permission model
  - `app/tools/tool_validation.py` structured validation and runtime checks
  - built-in tools: `FileSearchTool`, `DocumentReaderTool`, `MetadataTool`, `MemorySearchTool`, `KnowledgeGraphTool`, `VectorSearchTool`, `SummarizationTool`
- plugin SDK:
  - `app/plugins/sdk.py` plugin base contract
  - `app/plugins/manifest.py` plugin metadata schema
  - `app/plugins/loader.py` load/unload/reload/validate/list
  - `app/plugins/sandbox.py` untrusted permission restrictions
  - `app/plugins/manager.py` plugin lifecycle orchestration

## Setup

1. Copy `.env.example` to `.env`.
2. Set `VAULT_PATH`.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Core commands

```bash
python main.py --scan
python main.py --index
python main.py --watch
python main.py --auto-index
python main.py --search "insurance"
python main.py --ask "Summarize my PhD research"
python main.py --agents
python main.py --workflow-list
python main.py --plan "Prepare my Bali trip"
python main.py --execute
python main.py --api
python main.py --health
python main.py --status
python main.py --metrics
python main.py --sdk-test
```

## API base routes

- `/api/v1/search`
- `/api/v1/memory`
- `/api/v1/rag`
- `/api/v1/vault`
- `/api/v1/tasks`
- `/api/v1/workflows`
- `/api/v1/tools`
- `/api/v1/plugins`
- `/api/v1/system`

Public operational endpoints:

- `/health`
- `/status`
- `/metrics`
- `/docs`
- `/openapi.json`

## SDK example

```python
from sdk import Client

client = Client(base_url="http://127.0.0.1:8000", api_key="YOUR_KEY")
print(client.search("insurance"))
print(client.memory("passport"))
print(client.ask("Summarize my PhD"))
```

## Tests

```bash
python -m unittest discover -s tests -q
```
