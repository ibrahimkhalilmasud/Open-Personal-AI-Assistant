from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult
from app.tools.tool_validation import ValidationResult, validate_runtime_availability, validate_schema


@dataclass(slots=True)
class ToolDescriptor:
    tool_id: str
    name: str
    version: str
    description: str
    category: str
    author: str
    permissions: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class BaseTool(ABC):
    tool_id: str = ""
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    category: str = "general"
    author: str = "core"
    permissions: list[str] = []
    input_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    output_schema: dict[str, Any] = {"type": "object", "properties": {}}
    runtime_requirements: list[str] = []

    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id=self.tool_id,
            name=self.name,
            version=self.version,
            description=self.description,
            category=self.category,
            author=self.author,
            permissions=list(self.permissions),
            input_schema=dict(self.input_schema),
            output_schema=dict(self.output_schema),
        )

    def validate(self, inputs: dict[str, Any], context: ToolContext) -> ValidationResult:
        schema_result = validate_schema(inputs, self.input_schema)
        runtime_result = validate_runtime_availability(self.runtime_requirements)
        errors = [*schema_result.errors, *runtime_result.errors]
        return ValidationResult(valid=not errors, errors=errors)

    @abstractmethod
    def initialize(self, context: ToolContext) -> None:
        ...

    @abstractmethod
    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        ...

    @abstractmethod
    def cleanup(self, context: ToolContext) -> None:
        ...
