# TROUBLESHOOTING

## Purpose
Resolve common install/runtime/API/search/memory/workflow issues.

## Audience
Users and admins.

## Prerequisites
Access to terminal and project logs.

## Step-by-step (Common issues)
### Installation failures
- Recreate venv and reinstall dependencies.

### Missing dependencies
- `ModuleNotFoundError`: run `pip install -r requirements.txt` in active venv.

### Database problems
- Ensure `DATABASE` path is writable.
- Remove corrupted DB backup/restore if needed.

### ChromaDB issues
- Chroma optional; local vector fallback is used.
- Rebuild index with `python main.py --index`.

### Plugin problems
- Validate plugin folder has `manifest.json` + `plugin.py` + `create_plugin()`.

### API problems
- 401/403: API key missing/invalid.
- Verify server with `/health`.

### Memory/search issues
- Run `--scan`, then `--index`, then `--memory`.

### Agent/workflow issues
- Verify `python main.py --agent-list` and `--workflow-list`.

### Python errors
- Confirm Python 3.12+ and correct virtualenv activation.

## Examples
```bash
python main.py --health
python main.py --status
python main.py --metrics
python -m unittest discover -s tests -q
```

## Troubleshooting
If unresolved, inspect `logs/error.log` and open an issue with reproduction steps.

## Related documents
- [INSTALL.md](INSTALL.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [SECURITY.md](SECURITY.md)
