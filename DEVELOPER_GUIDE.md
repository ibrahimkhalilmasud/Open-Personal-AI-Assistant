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

## Tool architecture (Phase 7)

- Base contract: `app/tools/base_tool.py`
  - required metadata: `tool_id`, `name`, `version`, `description`, `category`, `author`, `permissions`, `input_schema`, `output_schema`
  - lifecycle methods: `initialize()`, `validate()`, `execute()`, `cleanup()`
- Discovery and registration: `app/tools/tool_discovery.py`, `app/tools/tool_registry.py`
- Execution engine: `app/tools/tool_executor.py`
  - execution metadata: `execution_id`, `agent_name`, `workflow_name`, `start_time`, `finish_time`, `duration`, `status`, `tool_inputs`, `tool_outputs`, `confidence`, `citations`
  - persistent history: `tool_history`, `tool_metrics`
- Permission and validation:
  - `app/tools/tool_permissions.py`
  - `app/tools/tool_validation.py`
- Chaining support: `ToolExecutor.execute_chain()`

## Plugin SDK

- `app/plugins/manifest.py` defines plugin metadata contract.
- `app/plugins/sdk.py` defines `PluginBase` lifecycle contract.
- `app/plugins/validator.py` enforces required plugin files and manifest fields.
- `app/plugins/loader.py` supports `load_plugin`, `unload_plugin`, `reload_plugin`, `list_plugins`, and `validate_plugin`.
- `app/plugins/sandbox.py` enforces untrusted plugin permission restrictions.
- `app/plugins/manager.py` orchestrates discovery and lifecycle operations.

## SQLite schema additions (phase 7)

- `tools`
- `tool_history`
- `plugins`
- `plugin_history`
- `permissions`
- `tool_metrics`

## Run tests

```bash
python -m unittest discover -s tests -q
```
