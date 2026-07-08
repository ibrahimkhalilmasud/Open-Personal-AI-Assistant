# AI-Personal-OS (Open-Personal-AI-Assistant)

Local-first personal knowledge platform with persistent indexing, retrieval, and hybrid search.

## Phase 3.5 stabilization scope

- persistent vector storage (ChromaDB + durable local fallback)
- incremental indexing using hash + modified date + model/chunk signature
- batch embedding support (`EMBED_BATCH_SIZE`)
- hybrid semantic + keyword + metadata search
- retrieval schema with normalized score and file metadata
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

## Commands

```bash
python main.py --scan
python main.py --index
python main.py --watch
python main.py --auto-index
python main.py --search "insurance"
python main.py --search "invoice" --folder Insurance --type pdf --after 2025 --top 10
```

## Tests

```bash
python -m unittest discover -s tests -q
```
