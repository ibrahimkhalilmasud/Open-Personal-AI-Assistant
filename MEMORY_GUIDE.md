# MEMORY GUIDE

## Purpose
Document memory types and memory operations.

## Audience
Users and developers.

## Prerequisites
Index at least one vault file.

## Step-by-step
Memory layers:
- Conversation memory (`conversation_memory`)
- Preference memory (`preferences`)
- Project memory (`projects`)
- Knowledge memory (`knowledge_memory`)
- Processing checkpoints (`memory_processing_state`)

Commands:
```bash
python main.py --memory
python main.py --memory-search "query"
python main.py --timeline 2025
python main.py --project <name>
python main.py --person <name>
```

## Examples
`--memory-search insurance` returns counts for conversations/preferences/projects/entities/relationships.

## Troubleshooting
If memory appears stale, run `--memory` (refreshes from index first).

## Related documents
- [KNOWLEDGE_GRAPH_GUIDE.md](KNOWLEDGE_GRAPH_GUIDE.md)
- [USER_GUIDE.md](USER_GUIDE.md)
