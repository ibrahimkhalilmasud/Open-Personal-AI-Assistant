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

`I could not find enough information in your Personal Vault to answer this question.`
