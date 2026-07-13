# USER GUIDE

## 1) Configure your vault

Set `.env` values:

```env
VAULT_PATH=/home/user/PersonalVault
MAX_CONTEXT_CHUNKS=12
MAX_CONTEXT_TOKENS=12000
DEFAULT_MODEL=qwen3
```

Optional:

```env
QUERY_SYNONYMS_FILE=/absolute/path/to/synonyms.json
MODEL_TIMEOUT_SECONDS=45
```

## 2) Build and maintain vault index

```bash
python main.py --scan
python main.py --index
python main.py --watch
```

## 3) Search directly

```bash
python main.py --search "insurance renewal"
python main.py --search "invoice" --folder Insurance --type pdf --after 2025 --top 10
```

## 4) Ask grounded questions (RAG)

```bash
python main.py --ask "Summarize my medical history"
python main.py --ask "Show every insurance document"
python main.py --ask "Which documents mention Brussels?"
python main.py --ask "Summarize my PhD research"
```

Streaming when provider supports it:

```bash
python main.py --ask "Summarize my research" --stream
```

## 5) Understand answer output

CLI prints:

- grounded answer
- confidence score and label (High/Medium/Low)
- provider/model used
- citations (filename + page when available)
- timing metrics (retrieval/context/model/total)

If context is missing, response is:

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
