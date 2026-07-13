# SDK GUIDE

## Purpose
Use the internal Python SDK (`sdk.Client`) for API access.

## Audience
Python developers.

## Prerequisites
API server running and API key created.

## Step-by-step
```python
from sdk import Client

client = Client(base_url="http://127.0.0.1:8000", api_key="YOUR_KEY")
print(client.health())
print(client.search("insurance", top_k=5).count)
print(client.memory("passport"))
print(client.ask("Summarize my insurance").answer)
```

Methods:
- `search(query, top_k=10)`
- `memory(query)`
- `ask(question, model=None)`
- `health()` `status()` `metrics()`

## Examples
Use `python main.py --sdk-test` for built-in connectivity check.

## Troubleshooting
`APIError` indicates non-2xx response; inspect status code and JSON payload.

## Related documents
- [API_REFERENCE.md](API_REFERENCE.md)
- [INSTALL.md](INSTALL.md)
