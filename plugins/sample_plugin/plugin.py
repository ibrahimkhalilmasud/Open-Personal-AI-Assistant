from __future__ import annotations

from app.plugins.manifest import PluginManifest
from app.plugins.sdk import PluginBase
from app.tools.base_tool import BaseTool
from app.tools.tool_context import ToolContext
from app.tools.tool_permissions import PermissionLevels
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_result import ToolResult


class SampleEchoTool(BaseTool):
    tool_id = "plugin.sample.echo"
    name = "SampleEchoTool"
    version = "1.0.0"
    description = "Echoes plugin input payload."
    category = "plugin"
    author = "sample_plugin"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }
    output_schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
    }

    def initialize(self, context: ToolContext) -> None:
        return

    def execute(self, inputs: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult.completed({"message": str(inputs.get("message", ""))}, confidence=0.9)

    def cleanup(self, context: ToolContext) -> None:
        return


class SamplePlugin(PluginBase):
    def __init__(self) -> None:
        self.manifest = PluginManifest(
            name="sample_plugin",
            version="1.0.0",
            author="core",
            description="Sample plugin demonstrating Tool SDK integration.",
            minimum_application_version="7.0.0",
            supported_platforms=["linux", "darwin", "windows"],
            supported_agents=["planning-agent"],
            required_permissions=["read_vault"],
        )
        self._tool = SampleEchoTool()

    def initialize(self) -> None:
        return

    def register_tools(self, registry: ToolRegistry) -> list[str]:
        registry.register(self._tool)
        return [self._tool.tool_id]

    def unregister_tools(self, registry: ToolRegistry) -> None:
        registry.unregister(self._tool.tool_id)

    def cleanup(self) -> None:
        return


def create_plugin() -> PluginBase:
    return SamplePlugin()
