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

## Run tests

```bash
python -m unittest discover -s tests -q
```
