# DEVELOPER GUIDE

## Project layout

Phase 4 RAG modules:

- `app/query/` → query analysis and expansion
- `app/rag/` → orchestrator and hybrid retrieval
- `app/context/` → context filtering, token budgeting, dedupe
- `app/prompts/` → reusable prompt construction
- `app/reasoning/` → answer generation + confidence scoring
- `app/citations/` → citation extraction/formatting

## Retrieval and reasoning flow

`Question -> QueryAnalyzer -> QueryExpander -> HybridRetriever -> ContextBuilder -> PromptBuilder -> AIRouter -> AnswerGenerator -> CitationFormatter -> JSON response`

## Grounding guarantees

- Prompts explicitly forbid hallucinations.
- Insufficient context returns deterministic fallback message.
- Citations are attached to every grounded answer.
- Generated answers are not written into vault storage.

## Performance metrics

`RAGEngine.ask()` returns timings:

- `retrieval_seconds`
- `context_seconds`
- `model_seconds`
- `total_seconds`

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
