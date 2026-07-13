# DEVELOPER GUIDE

## Purpose
Explain project structure and extension points.

## Audience
Contributors and maintainers.

## Prerequisites
Python dev environment and test dependencies installed.

## Step-by-step
### Project structure
- `main.py`: CLI entrypoint
- `app/api`: FastAPI server, auth, middleware, routes
- `app/services`: service-layer orchestration
- `app/vault`, `app/search`, `app/rag`, `app/memory`, `app/knowledge_graph`
- `app/tools`, `app/plugins`, `app/agents`, `app/workflows`

### Coding standards
- Keep changes local and tested.
- Follow existing dataclass/type-hint patterns.
- Avoid undocumented CLI/API behavior.

### Add an agent
1. Create class extending `BaseAgent` in `app/agents/`.
2. Implement lifecycle and plan/execute methods.
3. Ensure `AgentRegistry.discover()` auto-discovers it.

### Add a tool
1. Create class extending `BaseTool` in `app/tools/`.
2. Define metadata + schemas + execute logic.
3. It becomes discoverable through `ToolRegistry.discover()`.

### Add a plugin
1. Add folder under `plugins/<name>`.
2. Provide `manifest.json` and `plugin.py` with `create_plugin()`.
3. Use `PluginBase` and register tools through `ToolRegistry`.

### Add a workflow
Edit `app/workflows/templates.py`.

### Add AI provider
Extend `AIRouter` provider chain in `app/router/ai_router.py`.

### Migrations
Schema bootstrap is in `app/database/sqlite_db.py`; schema version tracked in `schema_migrations`.

### Tests
```bash
python -m unittest discover -s tests -q
```

### Debugging
- Check logs in `logs/`
- Use `python main.py --status` and API `/metrics`

## Examples
See `plugins/sample_plugin` and `app/tools/builtin_tools.py`.

## Troubleshooting
If discovery fails, verify module location and inheritance from base classes.

## Related documents
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_REFERENCE.md](API_REFERENCE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
