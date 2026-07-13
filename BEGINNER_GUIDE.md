# BEGINNER GUIDE

## Purpose
Explain core concepts in plain language.

## Audience
Non-technical and beginner users.

## Prerequisites
A successful installation.

## Step-by-step (Concept Tour)
1. **Personal Vault**: your folder of files the assistant reads.
2. **SQLite**: a local database file used for metadata, memory, and operations.
3. **ChromaDB / local vector DB**: stores vector representations of document chunks for semantic search.
4. **Embeddings**: numeric vectors representing meaning of text.
5. **Semantic search**: finds meaning-based matches, not only exact words.
6. **RAG**: retrieve relevant files, then answer using those files.
7. **Memory**: stores conversation entries and learned preferences/project summaries.
8. **Knowledge Graph**: stores entities (people/projects/topics) and relationships.
9. **Agents**: task executors/planners (current built-in: `planning-agent`).
10. **Tools**: callable capabilities (search, metadata, memory search, summarization, etc.).
11. **Plugins**: optional extensions that can add custom tools.

## Examples
```bash
python main.py --search "passport"
python main.py --memory-search "passport"
python main.py --person Mike
```

## Troubleshooting
If results are empty, run `--scan` and `--index` again after adding files.

## Related documents
- [USER_GUIDE.md](USER_GUIDE.md)
- [MEMORY_GUIDE.md](MEMORY_GUIDE.md)
- [KNOWLEDGE_GRAPH_GUIDE.md](KNOWLEDGE_GRAPH_GUIDE.md)
