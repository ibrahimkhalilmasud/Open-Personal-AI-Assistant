from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import load_settings
from app.knowledge_graph.query import KnowledgeGraphQuery
from app.memory.conversations import ConversationMemory
from app.memory.preferences import PreferenceMemory
from app.memory.projects import ProjectMemory
from app.metadata.extractors import extract_document_text, extract_image_metadata, extract_video_metadata
from app.retrieval import RetrievalEngine
from app.search import SearchEngine
from app.summarization import SummaryGenerator
from app.tools.base_tool import BaseTool
from app.tools.tool_context import ToolContext
from app.tools.tool_permissions import PermissionLevels
from app.tools.tool_result import ToolResult


class FileSearchTool(BaseTool):
    tool_id = "tool.file_search"
    name = "FileSearchTool"
    version = "1.0.0"
    description = "Searches indexed files using hybrid retrieval."
    category = "search"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer"},
            "folder": {"type": "string"},
            "file_type": {"type": "string"},
            "after": {"type": "string"},
            "before": {"type": "string"},
        },
        "required": ["query"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def initialize(self, context: ToolContext) -> None:
        self.settings = load_settings()
        self.search = SearchEngine(self.settings)

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        results = self.search.search(
            str(inputs.get("query", "")),
            top_k=max(1, int(inputs.get("top_k", 5))),
            folder=str(inputs.get("folder", "") or "") or None,
            file_type=str(inputs.get("file_type", "") or "") or None,
            after=str(inputs.get("after", "") or "") or None,
            before=str(inputs.get("before", "") or "") or None,
        )
        payload = {
            "results": [
                {
                    "path": item.path,
                    "filename": item.filename,
                    "score": item.score,
                    "snippet": item.snippet,
                    "file_type": item.file_type,
                }
                for item in results
            ]
        }
        citations = [item.path for item in results[:5]]
        return ToolResult.completed(payload, confidence=0.8 if results else 0.45, citations=citations)

    def cleanup(self, context: ToolContext) -> None:
        self.search = None


class DocumentReaderTool(BaseTool):
    tool_id = "tool.document_reader"
    name = "DocumentReaderTool"
    version = "1.0.0"
    description = "Reads document text from supported files."
    category = "document"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "must_exist": True},
        },
        "required": ["path"],
    }
    output_schema = {"type": "object", "properties": {"text": {"type": "string"}, "path": {"type": "string"}}}

    def initialize(self, context: ToolContext) -> None:
        return

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        path = Path(str(inputs.get("path", "")))
        text = extract_document_text(path)
        if not text and path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")[:10000]
        return ToolResult.completed(
            {
                "path": str(path),
                "text": text,
                "text_length": len(text),
            },
            confidence=0.75 if text else 0.2,
            citations=[str(path)],
        )

    def cleanup(self, context: ToolContext) -> None:
        return


class MetadataTool(BaseTool):
    tool_id = "tool.metadata"
    name = "MetadataTool"
    version = "1.0.0"
    description = "Extracts file metadata from documents, images, and videos."
    category = "metadata"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "must_exist": True},
        },
        "required": ["path"],
    }
    output_schema = {"type": "object", "properties": {"metadata": {"type": "object"}}}

    def initialize(self, context: ToolContext) -> None:
        return

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        path = Path(str(inputs.get("path", "")))
        stat = path.stat()
        metadata: dict[str, Any] = {
            "path": str(path),
            "file_size": stat.st_size,
            "modified": stat.st_mtime,
        }
        metadata.update(extract_image_metadata(path))
        metadata.update(extract_video_metadata(path))
        return ToolResult.completed({"metadata": metadata}, confidence=0.7, citations=[str(path)])

    def cleanup(self, context: ToolContext) -> None:
        return


class MemorySearchTool(BaseTool):
    tool_id = "tool.memory_search"
    name = "MemorySearchTool"
    version = "1.0.0"
    description = "Searches conversation, preference, and project memories."
    category = "memory"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
        },
        "required": ["query"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "conversations": {"type": "array"},
            "preferences": {"type": "array"},
            "projects": {"type": "array"},
        },
    }

    def initialize(self, context: ToolContext) -> None:
        self.settings = load_settings()

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        query = str(inputs.get("query", ""))
        conversation_hits = ConversationMemory(self.settings.database).search(query)
        preference_hits = PreferenceMemory(self.settings.database).search(query)
        project_hits = ProjectMemory(self.settings.database).search(query)
        citations = [str(item.get("source_document", "")) for item in project_hits[:5] if item.get("source_document")]
        return ToolResult.completed(
            {
                "query": query,
                "conversations": conversation_hits,
                "preferences": preference_hits,
                "projects": project_hits,
            },
            confidence=0.72,
            citations=citations,
        )

    def cleanup(self, context: ToolContext) -> None:
        return


class KnowledgeGraphTool(BaseTool):
    tool_id = "tool.knowledge_graph"
    name = "KnowledgeGraphTool"
    version = "1.0.0"
    description = "Queries related entities and relationships from the knowledge graph."
    category = "knowledge_graph"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {"type": "string"},
        },
        "required": ["query"],
    }
    output_schema = {"type": "object", "properties": {"entities": {"type": "array"}, "relationships": {"type": "array"}}}

    def initialize(self, context: ToolContext) -> None:
        self.settings = load_settings()
        self.query = KnowledgeGraphQuery(self.settings.database)

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        query = str(inputs.get("query", ""))
        mode = str(inputs.get("mode", "related")).lower()
        if mode == "project":
            payload = self.query.project(query)
        elif mode == "person":
            payload = self.query.person(query)
        else:
            payload = self.query.related_to(query)
        citations = [str(item.get("source_document", "")) for item in payload.get("facts", [])[:5] if item.get("source_document")]
        return ToolResult.completed(payload, confidence=0.7, citations=citations)

    def cleanup(self, context: ToolContext) -> None:
        return


class VectorSearchTool(BaseTool):
    tool_id = "tool.vector_search"
    name = "VectorSearchTool"
    version = "1.0.0"
    description = "Runs retrieval engine vector-first search over indexed content."
    category = "retrieval"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer"},
        },
        "required": ["query"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def initialize(self, context: ToolContext) -> None:
        self.engine = RetrievalEngine()

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        query = str(inputs.get("query", ""))
        top_k = max(1, int(inputs.get("top_k", 5)))
        results = self.engine.retrieve(query, top_k=top_k)
        citations = [str(item.get("path", "")) for item in results[:5] if item.get("path")]
        return ToolResult.completed({"results": results}, confidence=0.78 if results else 0.4, citations=citations)

    def cleanup(self, context: ToolContext) -> None:
        return


class SummarizationTool(BaseTool):
    tool_id = "tool.summarization"
    name = "SummarizationTool"
    version = "1.0.0"
    description = "Builds concise summaries from tool outputs."
    category = "reasoning"
    author = "core"
    permissions = [PermissionLevels.READ_VAULT]
    input_schema = {
        "type": "object",
        "properties": {
            "subject": {"type": "string"},
            "facts": {"type": "array"},
            "source_rows": {"type": "array"},
        },
        "required": ["subject"],
    }
    output_schema = {"type": "object", "properties": {"summary": {"type": "string"}}}

    def initialize(self, context: ToolContext) -> None:
        self.settings = load_settings()
        self.generator = SummaryGenerator(self.settings.database)

    def execute(self, inputs: dict[str, Any], context: ToolContext) -> ToolResult:
        subject = str(inputs.get("subject", "summary"))
        facts = [str(item) for item in (inputs.get("facts") or []) if str(item).strip()]
        source_rows = [item for item in (inputs.get("source_rows") or []) if isinstance(item, dict)]
        if source_rows:
            summary = self.generator.get_or_refresh("tool", subject, source_rows)
        elif facts:
            summary = f"Summary for {subject}: " + " ".join(facts[:5])
        else:
            summary = f"Summary for {subject}: no additional facts available."
        return ToolResult.completed({"summary": summary}, confidence=0.66, citations=[])

    def cleanup(self, context: ToolContext) -> None:
        return
