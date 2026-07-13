# AI-Personal-OS (Open-Personal-AI-Assistant)

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

## Core environment variables

- `VAULT_PATH` (required for scan/index/watch)
- `DATABASE` (default `data/database.db`)
- `VECTOR_DB` (default `data/vector`)
- `EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`)
- `CHUNK_SIZE` (default `500`)
- `CHUNK_OVERLAP` (default `100`)
- `EMBED_BATCH_SIZE` (default `64`)
- `MAX_CONTEXT_CHUNKS` (default `12`)
- `MAX_CONTEXT_TOKENS` (default `12000`)
- `QUERY_SYNONYMS_FILE` (optional JSON dictionary)
- `MODEL_TIMEOUT_SECONDS` (default `45`)

## Commands

```bash
python main.py --scan
python main.py --index
python main.py --watch
python main.py --auto-index
python main.py --search "insurance"
python main.py --search "invoice" --folder Insurance --type pdf --after 2025 --top 10
python main.py --agents
python main.py --agent-list
python main.py --workflow-list
python main.py --plan "Prepare my Bali trip"
python main.py --execute
python main.py --tools
python main.py --tool-list
python main.py --tool-info FileSearchTool
python main.py --tool-test FileSearchTool
python main.py --plugin-list
python main.py --plugin-load sample_plugin
python main.py --plugin-unload sample_plugin
```

## Tool chaining

Sequential chain execution is supported through `ToolExecutor.execute_chain()`:

`Question -> MemorySearchTool -> KnowledgeGraphTool -> VectorSearchTool -> DocumentReaderTool -> SummarizationTool -> Answer`

Each step receives structured outputs from prior steps and all executions are persisted in `tool_history`.

## RAG behavior

- Uses retrieved vault chunks only (grounded answers).
- Returns fallback when context is insufficient.
- Always includes citations in CLI output.
- Internally uses structured JSON:

```json
{
  "answer": "...",
  "confidence": 0.92,
  "sources": [
    {
      "filename": "...",
      "path": "...",
      "page": 4,
      "score": 0.94
    }
  ]
}
```

## Benchmarks (local unit-test fixture run)

| Metric | Value |
|---|---:|
| Retrieval time | ~0.01s |
| Context assembly time | ~0.001s |
| Model response time (mocked tests) | ~0.01s |
| End-to-end (mocked tests) | ~0.03s |

## Tests

```bash
python -m unittest discover -s tests -q
```
