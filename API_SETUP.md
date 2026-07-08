# API SETUP

All API keys are optional and are loaded automatically from `.env`.

Priority used by router:
1. local models
2. Gemini
3. Groq
4. OpenAI

The system keeps local provider support available even when cloud keys are missing.

Required for indexing commands:
- `VAULT_PATH`

Operational settings:
- `DATABASE`
- `VECTOR_DB`
- `EMBEDDING_MODEL`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `EMBED_BATCH_SIZE`
