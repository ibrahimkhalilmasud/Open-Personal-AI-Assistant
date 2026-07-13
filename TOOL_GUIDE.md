# TOOL GUIDE

## Purpose
Document built-in tools and tool framework behavior.

## Audience
Developers and advanced users.

## Prerequisites
Tool metadata/schema understanding.

## Step-by-step
Built-in tools (`app/tools/builtin_tools.py`):
- `tool.file_search`
- `tool.document_reader`
- `tool.metadata`
- `tool.memory_search`
- `tool.knowledge_graph`
- `tool.vector_search`
- `tool.summarization`

Framework components:
- discovery: `tool_discovery.py`
- registry: `tool_registry.py`
- execution + history: `tool_executor.py`
- permissions: `tool_permissions.py`

## Examples
List installed tool records via API:
```bash
GET /api/v1/tools
```

## Troubleshooting
If tool is undiscovered, ensure class inherits `BaseTool` and module is in `app/tools`.

## Related documents
- [PLUGIN_GUIDE.md](PLUGIN_GUIDE.md)
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
