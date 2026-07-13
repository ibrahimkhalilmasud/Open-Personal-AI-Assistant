# ADMIN GUIDE

## Purpose
Operational administration and maintenance for production-like usage.

## Audience
Administrators and operators.

## Prerequisites
Installation complete; access to host filesystem and logs.

## Step-by-step
### Deployment
- Run with virtualenv or Docker.
- Keep `.env` outside public repos.

### Configuration
Key settings: `DATABASE`, `VECTOR_DB`, `VAULT_PATH`, `DEFAULT_MODEL`, `MODEL_TIMEOUT_SECONDS`, CORS options.

### Monitoring
```bash
python main.py --health
python main.py --status
python main.py --metrics
```

### Database maintenance
- SQLite: backup by copying DB file when process is stopped.
- Validate table existence via `app/database/sqlite_db.py` bootstrap logic.

### Vector DB maintenance
- Re-index when chunk/model settings change:
```bash
python main.py --index
```

### Log management
Logs under `logs/` (`application.log`, `error.log`, `search.log`, `scan.log`, `watcher.log`).

### Backup / restore procedure
1. Stop API/CLI long-running jobs.
2. Backup `data/database.db`, `data/vector/`, and vault files.
3. Restore by replacing those paths and re-running `python main.py --index`.

## Examples
- Weekly: run `--scan`, `--index`, `--metrics`.
- Monthly: rotate/archive logs and verify DB/vector backups.

## Troubleshooting
If DB file locks occur, ensure only one writer-heavy process is active.

## Related documents
- [INSTALL.md](INSTALL.md)
- [SECURITY.md](SECURITY.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
