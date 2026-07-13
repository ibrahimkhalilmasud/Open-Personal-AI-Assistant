# PLUGIN GUIDE

## Purpose
Explain plugin layout, lifecycle, and operations.

## Audience
Plugin developers.

## Prerequisites
Understand `PluginBase` and tool contracts.

## Step-by-step
1. Create `plugins/<plugin_name>/manifest.json`.
2. Add `plugin.py` exposing `create_plugin()`.
3. Implement class extending `PluginBase`.
4. Register one or more tools in `register_tools()`.

Sample: `plugins/sample_plugin`.

## Examples
Manifest fields: name, version, author, description, minimum_application_version, supported_platforms, supported_agents, required_permissions.

## Troubleshooting
- Missing `create_plugin()`: load fails.
- Invalid manifest: validator rejects plugin.

## Related documents
- [TOOL_GUIDE.md](TOOL_GUIDE.md)
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
