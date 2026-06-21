# AI-Personal-OS (Open-Personal-AI-Assistant)

A local-first Personal AI Operating System scaffold focused on user-owned knowledge.

## Phase 3 status: Vector Indexing and Semantic Search

This repository now includes:
- personal vault path configuration via `VAULT_PATH`
- recursive scanner for supported file types
- SHA256 hashing for file change detection
- SQLite-backed file index table with scan metadata
- document text extraction (PDF, DOCX, TXT/MD, CSV/XLSX)
- image metadata extraction (dimensions, size, EXIF)
- video metadata extraction (duration, resolution)
- watchdog-based file watcher with automatic DB updates
- ChromaDB vector index for document chunks
- configurable embeddings model (`EMBEDDING_MODEL`)
- chunking pipeline (`CHUNK_SIZE=500`, `CHUNK_OVERLAP=100`)
- semantic + keyword hybrid search
- retrieval API (`retrieve(query, top_k=10)`)
- search logging at `logs/search.log`
- dedicated logs: `logs/scan.log` and `logs/watcher.log`

## Configure

1. Copy `.env.example` to `.env`.
2. Set `VAULT_PATH` to your Personal Data Vault folder.
3. Optional:
   - `AUTO_SCAN=true|false`
   - `SCAN_INTERVAL=300`
   - `VECTOR_DB=data/vector`
   - `EMBEDDING_MODEL=all-MiniLM-L6-v2`
   - `CHUNK_SIZE=500`
   - `CHUNK_OVERLAP=100`

## Commands

Run one-time vault scan:
```bash
python main.py --scan
```

Run continuous watcher:
```bash
python main.py --watch
```

Build/refresh vector index:
```bash
python main.py --index
```

Run continuous background indexing:
```bash
python main.py --auto-index
```

Run semantic + hybrid search:
```bash
python main.py --search "insurance renewal"
python main.py --search "medical report 2024"
```

Default startup summary:
```bash
python main.py
```
