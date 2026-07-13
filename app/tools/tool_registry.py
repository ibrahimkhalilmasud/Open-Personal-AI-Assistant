from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from app.tools.base_tool import BaseTool
from app.tools.tool_discovery import discover_tools


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def discover(self) -> None:
        for tool in discover_tools():
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        key = tool.tool_id or tool.name
        self._tools[key] = tool
        if tool.name and tool.name != key:
            self._tools[tool.name] = tool

    def unregister(self, tool_name_or_id: str) -> None:
        tool = self._tools.pop(tool_name_or_id, None)
        if tool is None:
            return
        for key, item in list(self._tools.items()):
            if item is tool:
                self._tools.pop(key, None)

    def list_tools(self) -> list[dict[str, Any]]:
        unique = {tool.tool_id: tool for tool in self._tools.values() if tool.tool_id}
        if not unique:
            unique = {tool.name: tool for tool in self._tools.values() if tool.name}
        return [asdict(tool.descriptor()) for tool in sorted(unique.values(), key=lambda item: item.name)]

    def find_tool(self, search_term: str) -> list[dict[str, Any]]:
        term = search_term.strip().lower()
        return [
            tool
            for tool in self.list_tools()
            if term in str(tool["name"]).lower() or term in str(tool["description"]).lower()
        ]

    def get_tool(self, tool_name_or_id: str) -> BaseTool | None:
        return self._tools.get(tool_name_or_id)

    def persist(self, database_path: str, builtin_tool_ids: set[str] | None = None) -> None:
        builtin_ids = builtin_tool_ids or set()
        now = datetime.now(UTC).isoformat()
        unique = {tool.tool_id: tool for tool in self._tools.values() if tool.tool_id}
        with sqlite3.connect(database_path) as conn:
            for tool in unique.values():
                descriptor = tool.descriptor()
                conn.execute(
                    """
                    INSERT INTO tools (
                        tool_id, name, version, description, category, author,
                        permissions_json, input_schema_json, output_schema_json, is_builtin, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(tool_id) DO UPDATE SET
                        name=excluded.name,
                        version=excluded.version,
                        description=excluded.description,
                        category=excluded.category,
                        author=excluded.author,
                        permissions_json=excluded.permissions_json,
                        input_schema_json=excluded.input_schema_json,
                        output_schema_json=excluded.output_schema_json,
                        is_builtin=excluded.is_builtin,
                        updated_at=excluded.updated_at
                    """,
                    (
                        descriptor.tool_id,
                        descriptor.name,
                        descriptor.version,
                        descriptor.description,
                        descriptor.category,
                        descriptor.author,
                        json.dumps(descriptor.permissions, ensure_ascii=False),
                        json.dumps(descriptor.input_schema, ensure_ascii=False),
                        json.dumps(descriptor.output_schema, ensure_ascii=False),
                        1 if descriptor.tool_id in builtin_ids else 0,
                        now,
                    ),
                )
            conn.commit()
