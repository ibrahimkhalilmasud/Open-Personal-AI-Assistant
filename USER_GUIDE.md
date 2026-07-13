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

## 9) Tool execution framework

```bash
python main.py --tools
python main.py --tool-list
python main.py --tool-info FileSearchTool
python main.py --tool-test FileSearchTool
```

Behavior:
- tools are auto-discovered from `app/tools/` and plugin registrations
- every tool run is permission-checked before execution
- tool execution history is stored in SQLite (`tool_history`, `tool_metrics`)

## 10) Plugin SDK lifecycle

```bash
python main.py --plugin-list
python main.py --plugin-load sample_plugin
python main.py --plugin-unload sample_plugin
```

Plugin package structure:
- required: `manifest.json`, `plugin.py`, `README.md`
- optional: `requirements.txt`

Untrusted plugins run through sandbox permission checks that block unapproved internet access, destructive filesystem permissions, and database write permissions unless explicitly trusted.
