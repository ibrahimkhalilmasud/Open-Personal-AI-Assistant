# KNOWLEDGE GRAPH GUIDE

## Purpose
Explain entity/relationship extraction and graph querying.

## Audience
Users and developers.

## Prerequisites
Vault scanned/indexed.

## Step-by-step
- Entities stored in `entities`
- Links stored in `relationships`
- Time slices stored in `timelines`

Graph entry points:
- CLI: `--memory-search`, `--timeline`, `--project`, `--person`
- API: `/api/v1/memory/search`, `/api/v1/memory/projects/{name}`, `/api/v1/memory/persons/{name}`

## Examples
```bash
python main.py --person Mike
python main.py --project Luxoria
```

## Troubleshooting
Low entity counts usually indicate insufficient source documents.

## Related documents
- [MEMORY_GUIDE.md](MEMORY_GUIDE.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
