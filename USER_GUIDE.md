# USER GUIDE

## 1) Select your vault folder
Open `.env` and set:

```env
VAULT_PATH=/home/user/PersonalVault
```

Examples:
- Windows: `D:\PersonalVault`
- Linux: `/home/user/PersonalVault`
- macOS: `/Users/user/PersonalVault`

Optional scan controls:

```env
AUTO_SCAN=true
SCAN_INTERVAL=300
VECTOR_DB=data/vector
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=100
EMBED_BATCH_SIZE=64
```

## 2) Run a full scan

```bash
python main.py --scan
```

This recursively scans supported files and updates the database.

## 3) Run live watching

```bash
python main.py --watch
```

This monitors file add/modify/remove events and updates the database automatically.

## 4) Check logs

- `logs/application.log`
- `logs/error.log`
- `logs/scan.log`
- `logs/watcher.log`
- `logs/search.log`

## 5) Build semantic index

```bash
python main.py --index
```

This reads extracted text, creates overlapping chunks, generates embeddings, and stores vectors in ChromaDB.

## 6) Run semantic + hybrid search

```bash
python main.py --search "insurance renewal"
python main.py --search "medical report 2024"
python main.py --search "documents mentioning Brussels"
python main.py --search "invoice" --folder Insurance --type pdf --after 2025 --top 10
```

Search returns score, filename, path, and a snippet.

## 7) Run automatic background indexing

```bash
python main.py --auto-index
```

This runs initial scan/index and keeps vectors updated for file changes.

## 8) Build and query persistent memory

```bash
python main.py --memory
python main.py --memory-search "insurance"
python main.py --timeline 2025
python main.py --project Luxoria
python main.py --person Mike
```

Behavior:
- `--memory` runs incremental memory extraction and prints memory totals
- `--memory-search` searches conversation memory, preferences, projects, and graph entities/relationships
- `--timeline` returns timeline events by date prefix (`YYYY` or `YYYY-MM`)
- `--project` returns project summary + related graph connections
- `--person` returns person entities, connected relationships, and known facts
