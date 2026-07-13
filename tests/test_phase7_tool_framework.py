import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database.sqlite_db import initialize_database
from app.tools import BaseTool, ToolContext, ToolExecutor, ToolPermissionManager, ToolRegistry, ToolResult
from app.tools.tool_permissions import PermissionLevels


class _EchoTool(BaseTool):
    tool_id = "tool.test.echo"
    name = "EchoTool"
    version = "1.0.0"
    description = "Echo test tool"
    category = "test"
    author = "tests"
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


class _PrefixTool(BaseTool):
    tool_id = "tool.test.prefix"
    name = "PrefixTool"
    version = "1.0.0"
    description = "Prefix test tool"
    category = "test"
    author = "tests"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }
    output_schema = {
        "type": "object",
        "properties": {"summary": {"type": "string"}},
    }

    def initialize(self, context: ToolContext) -> None:
        return

    def execute(self, inputs: dict[str, object], context: ToolContext) -> ToolResult:
        return ToolResult.completed({"summary": f"final:{inputs.get('message', '')}"}, confidence=0.8)

    def cleanup(self, context: ToolContext) -> None:
        return


class Phase7ToolFrameworkTests(unittest.TestCase):
    def test_registry_discovers_builtin_tools(self) -> None:
        registry = ToolRegistry()
        registry.discover()
        names = {item["name"] for item in registry.list_tools()}
        self.assertIn("FileSearchTool", names)
        self.assertIn("SummarizationTool", names)

    def test_base_tool_validation_reports_missing_required_inputs(self) -> None:
        tool = _EchoTool()
        validation = tool.validate({}, ToolContext(execution_id="e1", agent_name="tester"))
        self.assertFalse(validation.valid)
        self.assertTrue(any(item.code == "MISSING_PARAMETER" for item in validation.errors))

    def test_tool_executor_enforces_permission_and_persists_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "tooling.db")
            initialize_database(db_path)

            registry = ToolRegistry()
            registry.register(_EchoTool())
            permissions = ToolPermissionManager(db_path)
            executor = ToolExecutor(db_path, registry, permissions)

            denied = executor.execute("tool.test.echo", {"message": "hello"}, agent_name="agent-x")
            self.assertEqual(denied["status"], "failed")
            self.assertEqual(denied["error"]["code"], "PERMISSION_DENIED")

            permissions.grant("agent-x", PermissionLevels.READ_VAULT)
            success = executor.execute("tool.test.echo", {"message": "hello"}, agent_name="agent-x")
            self.assertEqual(success["status"], "completed")
            self.assertEqual(success["tool_outputs"]["message"], "hello")

            with sqlite3.connect(db_path) as conn:
                count = conn.execute("SELECT COUNT(*) FROM tool_history").fetchone()[0]
                self.assertGreaterEqual(count, 2)

    def test_tool_executor_supports_chaining(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "tooling.db")
            initialize_database(db_path)

            registry = ToolRegistry()
            registry.register(_EchoTool())
            registry.register(_PrefixTool())
            permissions = ToolPermissionManager(db_path)
            permissions.grant("agent-x", PermissionLevels.READ_VAULT)
            executor = ToolExecutor(db_path, registry, permissions)

            chain = [
                {"tool": "EchoTool", "inputs": {"message": "hello"}},
                {"tool": "PrefixTool", "inputs": {"message": "$message"}},
            ]
            history = executor.execute_chain(chain, agent_name="agent-x", workflow_name="chain")
            self.assertEqual(len(history), 2)
            self.assertEqual(history[-1]["status"], "completed")
            self.assertEqual(history[-1]["tool_outputs"]["summary"], "final:hello")


if __name__ == "__main__":
    unittest.main()
