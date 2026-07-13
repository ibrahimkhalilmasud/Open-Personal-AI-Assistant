# USER GUIDE

## 1) Configure

```env
VAULT_PATH=/home/user/PersonalVault
DATABASE=data/database.db
VECTOR_DB=data/vector
DEFAULT_MODEL=qwen3
```

## 2) Vault operations

```bash
python main.py --scan
python main.py --index
python main.py --watch
```

## 3) Search and ask

```bash
python main.py --search "insurance renewal"
python main.py --ask "Which documents mention Brussels?"
```

## 4) Memory and graph

```bash
python main.py --memory
python main.py --memory-search "passport"
python main.py --timeline 2025
python main.py --project Luxoria
python main.py --person Mike
```

## 5) Service/API mode

```bash
python main.py --api
python main.py --health
python main.py --status
python main.py --metrics
```

Then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI spec: `http://127.0.0.1:8000/openapi.json`

## 6) SDK quick test

```bash
python main.py --sdk-test
```

Use API key auth for protected `/api/v1/*` endpoints.
