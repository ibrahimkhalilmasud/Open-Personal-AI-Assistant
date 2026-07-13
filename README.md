# AI-Personal-OS (Open-Personal-AI-Assistant)

Local-first personal knowledge platform with indexing, retrieval, persistent memory, a knowledge graph, and a reusable service/API layer.

## Phase 8 scope (Service Layer + REST API + SDK)

- Service Layer entry points under `app/services/`
- FastAPI server with versioned routes under `app/api/`
- Internal Python SDK under `app/sdk/`
- API key authentication, middleware, health/status/metrics endpoints
- Migration-safe API/service tables (`api_keys`, `api_requests`, `service_metrics`, `service_health`, `api_audit_log`)

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
