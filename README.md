# AI-Personal-OS (Open-Personal-AI-Assistant)

Local-first personal knowledge platform with persistent indexing, retrieval, hybrid search, and a persistent memory + knowledge graph engine.

## Phase 5 scope (persistent memory + knowledge graph)

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
python main.py --memory
python main.py --memory-search "passport"
python main.py --timeline 2025
python main.py --project Luxoria
python main.py --person Mike
```

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
