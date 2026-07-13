# OPERATIONS MANUAL

## Purpose
Day-2 operational runbook.

## Audience
Power users and administrators.

## Prerequisites
Installed instance with configured `.env`.

## Step-by-step
### Daily
- `python main.py --scan`
- `python main.py --index`
- `python main.py --search "<topic>"`

### Weekly
- Review metrics: `python main.py --metrics`
- Verify health/status: `python main.py --health && python main.py --status`

### Monthly
- Backup `data/database.db`, `data/vector/`, vault files.
- Archive or rotate logs under `logs/`.

### Updating
1. Pull latest code.
2. Reinstall dependencies.
3. Run `python main.py --index`.

### Re-indexing
Run after changing `EMBEDDING_MODEL`, `CHUNK_SIZE`, or `CHUNK_OVERLAP`.

### Change model/provider
Update `.env` (`DEFAULT_MODEL`, API keys), then restart command/API run.

### Failure recovery
- Restore DB/vector/vault backup.
- Run `python main.py --scan` and `python main.py --index`.

## Examples
Use API mode for monitoring integrations:
```bash
python main.py --api
```

## Troubleshooting
Check `logs/error.log` first, then run health/status/metrics commands.

## Related documents
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- [INSTALL.md](INSTALL.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
