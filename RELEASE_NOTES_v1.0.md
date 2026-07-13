# RELEASE NOTES v1.0

## Purpose
Publish-ready release summary for GitHub release body.

## Audience
End users and adopters.

## Prerequisites
Version 1.0 branch is tested.

## Step-by-step
### Feature list
- Local-first vault scan/index/search
- Grounded RAG answers with confidence/citations
- Persistent memory + knowledge graph
- Planning agent + task/workflow execution
- Tool framework + plugin SDK
- FastAPI + API key auth + SDK

### Known limitations
- No CLI flags for `--setup`, `--backup`, `--restore`, `--demo`, `--plugin-list`, `--tool-list`.
- Plugin sandbox is policy-based, not process-isolated.
- Some embedding/provider flows depend on network/model availability.

### Upgrade guide
- Pull latest code
- Reinstall requirements
- Keep `.env` and `data/` backups
- Run `python main.py --index`

### Migration notes
- Database schema bootstrap tracks version in `schema_migrations` (`baseline_v1`).

### Repository metadata suggestions
- Description: `Local-first personal AI assistant with vault indexing, memory graph, RAG, API, SDK, tools, and plugins.`
- Topics: `python`, `fastapi`, `rag`, `sqlite`, `chromadb`, `knowledge-graph`, `personal-assistant`, `semantic-search`, `local-first`, `ai-agent`.
- Suggested screenshots/GIFs:
  1. CLI scan/index/search flow
  2. `/docs` API explorer
  3. Task plan + execute output
  4. Memory/timeline query output

## Examples
Recommended release title: `Open Personal AI Assistant v1.0.0`.

## Troubleshooting
If release checks fail, rerun tests and endpoint smoke checks before publishing.

## Related documents
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
