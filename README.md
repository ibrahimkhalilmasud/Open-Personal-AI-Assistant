# AI-Personal-OS (Open-Personal-AI-Assistant)

Local-first personal knowledge platform with indexing, hybrid retrieval, and grounded question answering.

## Phase 4 scope (Knowledge & Reasoning Engine)

Implemented RAG pipeline stages:

1. Query Analyzer (`app/query/analyzer.py`)
2. Query Expansion (`app/query/expansion.py`)
3. Hybrid Search + Retrieval (`app/rag/retriever.py`)
4. Context Builder (`app/context/builder.py`)
5. Prompt Builder (`app/prompts/builder.py`)
6. AI Router (`app/router/ai_router.py`)
7. Answer Generator (`app/reasoning/answer_generator.py`)
8. Citation Formatter (`app/citations/formatter.py`)
9. Confidence Scoring (`app/reasoning/confidence.py`)
10. End-to-end engine (`app/rag/engine.py`)

## Setup

1. Copy `.env.example` to `.env`.
2. Set `VAULT_PATH`.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Core environment variables

- `VAULT_PATH` (required for scan/index/watch)
- `DATABASE` (default `data/database.db`)
- `VECTOR_DB` (default `data/vector`)
- `EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`)
- `CHUNK_SIZE` (default `500`)
- `CHUNK_OVERLAP` (default `100`)
- `EMBED_BATCH_SIZE` (default `64`)
- `MAX_CONTEXT_CHUNKS` (default `12`)
- `MAX_CONTEXT_TOKENS` (default `12000`)
- `QUERY_SYNONYMS_FILE` (optional JSON dictionary)
- `MODEL_TIMEOUT_SECONDS` (default `45`)

## Commands

```bash
python main.py --scan
python main.py --index
python main.py --watch
python main.py --auto-index
python main.py --search "insurance"
python main.py --ask "Summarize my medical history"
python main.py --ask "Which documents mention Brussels?" --model qwen3 --stream
```

## RAG behavior

- Uses retrieved vault chunks only (grounded answers).
- Returns fallback when context is insufficient.
- Always includes citations in CLI output.
- Internally uses structured JSON:

```json
{
  "answer": "...",
  "confidence": 0.92,
  "sources": [
    {
      "filename": "...",
      "path": "...",
      "page": 4,
      "score": 0.94
    }
  ]
}
```

## Benchmarks (local unit-test fixture run)

| Metric | Value |
|---|---:|
| Retrieval time | ~0.01s |
| Context assembly time | ~0.001s |
| Model response time (mocked tests) | ~0.01s |
| End-to-end (mocked tests) | ~0.03s |

## Tests

```bash
python -m unittest discover -s tests -q
```
