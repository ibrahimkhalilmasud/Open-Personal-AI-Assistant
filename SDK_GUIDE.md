# SDK GUIDE

## Install dependencies

```bash
pip install -r requirements.txt
```

## Import

```python
from sdk import Client
```

## Initialize

```python
client = Client(base_url="http://127.0.0.1:8000", api_key="YOUR_KEY")
```

## Methods

- `client.search(query, top_k=10)`
- `client.memory(query)`
- `client.ask(question, model=None)`
- `client.health()`
- `client.status()`
- `client.metrics()`

## Example

```python
result = client.search("insurance")
print(result.count)

memory = client.memory("passport")
print(memory)

answer = client.ask("Summarize my PhD")
print(answer.answer)
```
