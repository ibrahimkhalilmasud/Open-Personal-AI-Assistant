# USER GUIDE

## Purpose
Daily usage reference for CLI and API mode.

## Audience
End users.

## Prerequisites
Configured `.env` with `VAULT_PATH`.

## Step-by-step
### Daily workflow
```bash
python main.py --scan
python main.py --index
python main.py --search "insurance"
python main.py --ask "Summarize my insurance"
```

### Memory and graph
```bash
python main.py --memory
python main.py --memory-search "passport"
python main.py --timeline 2025
python main.py --project Luxoria
python main.py --person Mike
```

### Agents and workflows
```bash
python main.py --agent-list
python main.py --workflow-list
python main.py --plan "review insurance policies"
python main.py --execute
```

### API mode
```bash
python main.py --api
```
Open `http://127.0.0.1:8000/docs`.

## Examples
```bash
python main.py --search "invoice" --folder finance --type pdf --top 5
python main.py --ask "What is due this month?" --model qwen3
```

## Troubleshooting
Use `python main.py --health` and `--status` when operations fail.

## Related documents
- [QUICK_START.md](QUICK_START.md)
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
