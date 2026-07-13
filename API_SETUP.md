# API SETUP

All keys are optional; provider fallback is automatic.

## Provider selection order

1. User-selected model (`--model`)
2. Default model (`DEFAULT_MODEL`)
3. Provider fallback chain

Router provider chain:

1. Ollama (`ollama`, local)
2. Gemini (`GOOGLE_API_KEY`)
3. Groq (`GROQ_API_KEY`)
4. OpenAI (`OPENAI_API_KEY`)

## Required for vault indexing

- `VAULT_PATH`

## RAG and model settings

- `DEFAULT_MODEL`
- `MODEL_TIMEOUT_SECONDS`
- `MAX_CONTEXT_CHUNKS`
- `MAX_CONTEXT_TOKENS`
- `QUERY_SYNONYMS_FILE`

## API security settings

- `OPA_API_KEY_HASH_PEPPER` (used for API key hash derivation)
- `CORS_ALLOWED_ORIGINS` (comma-separated, defaults to localhost origins)
- `CORS_ALLOW_CREDENTIALS` (defaults to `false`)

## Example `.env`

```env
OPENAI_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
OLLAMA_URL=http://localhost:11434
DEFAULT_MODEL=qwen3
MODEL_TIMEOUT_SECONDS=45
MAX_CONTEXT_CHUNKS=12
MAX_CONTEXT_TOKENS=12000
QUERY_SYNONYMS_FILE=
OPA_API_KEY_HASH_PEPPER=open-personal-ai-assistant-api-key-v1
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
CORS_ALLOW_CREDENTIALS=false
```

## Streaming behavior

- Ollama/OpenAI-compatible providers: streaming supported.
- Gemini path: non-streaming mode used.
- If a provider fails, router falls back to next provider.
