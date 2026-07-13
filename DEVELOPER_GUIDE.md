# DEVELOPER GUIDE

## Project layout
Core modules are under `app/` and mirror the target architecture.

## Memory architecture
- `app/memory/short_term.py`: in-session turn cache
- `app/memory/conversations.py`: persistent conversation memory
- `app/memory/preferences.py`: persistent preference memory
- `app/memory/projects.py`: project detection and project memory
- `app/memory/long_term.py`: incremental long-term memory pipeline

## Knowledge graph
- `app/knowledge_graph/entities.py`: canonical entities and aliases
- `app/knowledge_graph/relationships.py`: typed graph edges with confidence
- `app/knowledge_graph/timeline.py`: persistent timeline events
- `app/knowledge_graph/query.py`: graph query helpers for person/project/related queries

## Incremental updates
- The memory pipeline processes only files with changed index/hash signatures using `memory_processing_state`.
- Summary generation is cached in `summary_cache` and only refreshes when source signatures change.

## Entity and relationship extraction
- Rule-based extraction is implemented in `app/entity_extraction/`.
- Entity deduplication and alias merging is implemented in `app/entity_resolution/`.
- Relationship typing currently maps document evidence into `works_for`, `belongs_to`, `located_in`, `travels_to`, `references`, and fallback `related_to`.

## Run tests
```bash
python -m unittest discover -s tests -q
```
