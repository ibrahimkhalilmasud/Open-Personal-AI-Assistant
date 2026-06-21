# AI-Personal-OS (Open-Personal-AI-Assistant)

A local-first Personal AI Operating System scaffold focused on user-owned knowledge.

## Phase 2 status: Personal Data Vault Engine

This repository now includes:
- personal vault path configuration via `VAULT_PATH`
- recursive scanner for supported file types
- SHA256 hashing for file change detection
- SQLite-backed file index table with scan metadata
- document text extraction (PDF, DOCX, TXT/MD, CSV/XLSX)
- image metadata extraction (dimensions, size, EXIF)
- video metadata extraction (duration, resolution)
- watchdog-based file watcher with automatic DB updates
- dedicated logs: `logs/scan.log` and `logs/watcher.log`

## Configure

1. Copy `.env.example` to `.env`.
2. Set `VAULT_PATH` to your Personal Data Vault folder.
3. Optional:
   - `AUTO_SCAN=true|false`
   - `SCAN_INTERVAL=300`

## Commands

Run one-time vault scan:
```bash
python main.py --scan
```

Run continuous watcher:
```bash
python main.py --watch
```

Default startup summary:
```bash
python main.py
```
