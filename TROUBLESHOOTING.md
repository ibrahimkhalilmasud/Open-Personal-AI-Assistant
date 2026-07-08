# TROUBLESHOOTING

## `VAULT_PATH` is empty
Set `VAULT_PATH` in `.env` to your Personal Data Vault path.

## Database not created
Ensure `DATABASE` points to a writable location.

## `.env` values not applied
Install `python-dotenv` and keep `.env` in the project root (or set `OPA_ENV_FILE=/path/to/.env`).

## `--watch` / `--auto-index` fails
Install `watchdog` from requirements.

## Search returns no semantic results
Verify `VECTOR_DB` is writable and run:
```bash
python main.py --index
```

## Corrupted or encrypted documents
The system skips unreadable files and logs errors to `logs/error.log`.

## ChromaDB unavailable
Install `chromadb`. A durable local vector backend is used when ChromaDB is unavailable.

## No cloud provider used
Add API keys in `.env`; local provider remains first by design.
