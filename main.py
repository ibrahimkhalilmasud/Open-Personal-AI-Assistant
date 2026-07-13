from __future__ import annotations

import argparse
import json

from app.agents.context import ContextEngine
from app.agents.executor import AgentExecutor
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.core.system import create_system
from app.database.sqlite_db import initialize_database
from app.knowledge_graph.query import KnowledgeGraphQuery
from app.logging import get_application_logger, get_error_logger
from app.memory import ConversationMemory, LongTermMemoryEngine, PreferenceMemory, ProjectMemory
from app.plugins.loader import PluginLoader
from app.plugins.manager import PluginManager
from app.rag import RAGEngine
from app.search import SearchEngine
from app.tasks.executor import TaskExecutionEngine
from app.tasks.history import TaskHistoryStore
from app.tasks.planner import TaskPlanner
from app.tasks.queue import TaskQueue
from app.tools import PermissionLevels, ToolExecutor, ToolPermissionManager, ToolRegistry
from app.vault.engine import VaultEngine
from app.workflows.engine import WorkflowEngine
from app.workflows.registry import WorkflowRegistry


BUILTIN_TOOL_IDS = {
    "tool.file_search",
    "tool.document_reader",
    "tool.metadata",
    "tool.memory_search",
    "tool.knowledge_graph",
    "tool.vector_search",
    "tool.summarization",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-Personal-OS")
    parser.add_argument("--scan", action="store_true", help="Scan vault and update database")
    parser.add_argument("--watch", action="store_true", help="Watch vault for file changes")
    parser.add_argument("--index", action="store_true", help="Build semantic vector index")
    parser.add_argument("--auto-index", action="store_true", help="Run scan+index and continuous auto indexing")
    parser.add_argument("--search", type=str, help="Run hybrid semantic search")
    parser.add_argument("--folder", type=str, help="Filter search by folder name or path fragment")
    parser.add_argument("--type", dest="file_type", type=str, help="Filter search by file extension")
    parser.add_argument("--after", type=str, help="Filter search by modified_date >= value")
    parser.add_argument("--before", type=str, help="Filter search by modified_date <= value")
    parser.add_argument("--top", type=int, default=10, help="Maximum number of search results")
    parser.add_argument("--ask", type=str, help="Ask grounded RAG question")
    parser.add_argument("--model", type=str, help="Preferred model")
    parser.add_argument("--stream", action="store_true", help="Stream model output when provider supports it")

    parser.add_argument("--agents", action="store_true", help="Show registered agents")
    parser.add_argument("--agent-list", action="store_true", help="Show registered agents")
    parser.add_argument("--workflow-list", action="store_true", help="Show workflows")
    parser.add_argument("--plan", type=str, help="Create a task plan")
    parser.add_argument("--execute", action="store_true", help="Execute approved tasks")

    parser.add_argument("--memory", action="store_true", help="Show persistent memory overview")
    parser.add_argument("--memory-search", type=str, help="Search memory and knowledge graph")
    parser.add_argument("--timeline", type=str, help="Show timeline for year/month prefix (e.g. 2025 or 2025-03)")
    parser.add_argument("--project", type=str, help="Show memory and graph details for a project")
    parser.add_argument("--person", type=str, help="Show memory and graph details for a person")

    parser.add_argument("--tools", action="store_true", help="Show registered tools")
    parser.add_argument("--tool-list", action="store_true", help="Show registered tools")
    parser.add_argument("--tool-info", type=str, help="Show tool metadata by tool name")
    parser.add_argument("--tool-test", type=str, help="Run a built-in tool smoke test")
    parser.add_argument("--plugin-list", action="store_true", help="Show plugins")
    parser.add_argument("--plugin-load", type=str, help="Load plugin by folder name")
    parser.add_argument("--plugin-unload", type=str, help="Unload plugin by manifest name")
    return parser.parse_args()


def _build_tooling(database_path: str) -> tuple[ToolRegistry, ToolExecutor, PluginManager]:
    initialize_database(database_path)
    registry = ToolRegistry()
    registry.discover()
    registry.persist(database_path, builtin_tool_ids=BUILTIN_TOOL_IDS)

    permissions = ToolPermissionManager(database_path)
    for principal in ("cli", "planning-agent"):
        permissions.grant(principal, PermissionLevels.READ_VAULT, source="bootstrap")

    executor = ToolExecutor(database_path=database_path, registry=registry, permission_manager=permissions)
    plugin_loader = PluginLoader(database_path=database_path, tool_registry=registry, plugins_root="plugins")
    plugin_manager = PluginManager(plugin_loader)
    return registry, executor, plugin_manager


def _default_tool_test_inputs(tool_name: str) -> dict[str, object]:
    fixtures = {
        "FileSearchTool": {"query": "insurance", "top_k": 3},
        "DocumentReaderTool": {"path": "README.md"},
        "MetadataTool": {"path": "README.md"},
        "MemorySearchTool": {"query": "project"},
        "KnowledgeGraphTool": {"query": "project", "mode": "related"},
        "VectorSearchTool": {"query": "project", "top_k": 3},
        "SummarizationTool": {"subject": "tool-test", "facts": ["tool framework initialized"]},
    }
    return fixtures.get(tool_name, {"message": "tool smoke test"})


def main() -> None:
    app_logger = get_application_logger("main")
    error_logger = get_error_logger("main")
    args = parse_args()
    system = create_system()
    app_logger.info("startup | %s", system.settings.settings_validation_report)

    try:
        ask_value = getattr(args, "ask", None)
        model_value = getattr(args, "model", None)
        stream_value = bool(getattr(args, "stream", False))
        agents_flag = bool(getattr(args, "agents", False))
        agent_list_flag = bool(getattr(args, "agent_list", False))
        workflow_list_flag = bool(getattr(args, "workflow_list", False))
        plan_value = getattr(args, "plan", None)
        execute_flag = bool(getattr(args, "execute", False))
        tools_flag = bool(getattr(args, "tools", False))
        tool_list_flag = bool(getattr(args, "tool_list", False))
        tool_info_value = getattr(args, "tool_info", None)
        tool_test_value = getattr(args, "tool_test", None)
        plugin_list_flag = bool(getattr(args, "plugin_list", False))
        plugin_load_value = getattr(args, "plugin_load", None)
        plugin_unload_value = getattr(args, "plugin_unload", None)

        if args.scan:
            engine = VaultEngine(system.settings)
            summary = engine.full_scan()
            print(
                "Scan complete | "
                f"total={summary['total']} new={summary['new']} changed={summary['changed']} deleted={summary['deleted']}"
            )
            return

        if args.watch:
            try:
                from app.vault.watcher import watch_vault
            except ModuleNotFoundError as exc:
                raise SystemExit("watchdog is required for --watch. Install dependencies from requirements.txt") from exc

            engine = VaultEngine(system.settings)
            watch_vault(engine)
            return

        if args.index:
            engine = VaultEngine(system.settings)
            scan_summary = engine.full_scan()
            index_summary = engine.vector_indexer.index_all()
            print(
                "Index complete | "
                f"scan_total={scan_summary['total']} new={scan_summary['new']} changed={scan_summary['changed']} "
                f"deleted={scan_summary['deleted']} indexed={index_summary.indexed} updated={index_summary.updated} "
                f"skipped={index_summary.skipped} failed={index_summary.failed} "
                f"duration={index_summary.duration_seconds:.2f}s"
            )
            return

        if args.auto_index:
            try:
                from app.vault.watcher import watch_vault
            except ModuleNotFoundError as exc:
                raise SystemExit("watchdog is required for --auto-index. Install dependencies from requirements.txt") from exc

            engine = VaultEngine(system.settings)
            engine.full_scan()
            engine.vector_indexer.index_all()
            watch_vault(engine)
            return

        if args.search is not None:
            search_engine = SearchEngine(system.settings)
            results = search_engine.search(
                args.search,
                top_k=max(1, args.top),
                folder=args.folder,
                file_type=args.file_type,
                after=args.after,
                before=args.before,
            )
            if not results:
                print("No results found.")
                return
            for index, result in enumerate(results, start=1):
                print(f"Result {index}")
                print(f"Score: {result.score:.2f}")
                print(f"File: {result.filename}")
                print(f"Path: {result.path}")
                print(f"Type: {result.file_type}")
                print("Snippet:")
                print(f'"{result.snippet}"')
                print()
            return

        if ask_value is not None:
            rag = RAGEngine(system.settings, system.router)
            response = rag.ask(ask_value, model=model_value, stream=stream_value)
            print(response.get("answer", ""))
            print(f"confidence={response.get('confidence', 0.0)} label={response.get('confidence_label', 'Low')}")
            print(f"provider={response.get('provider', 'none')} model={response.get('model', 'none')}")
            citations = response.get("citations", [])
            if citations:
                print("citations:")
                for citation in citations:
                    print(f"- {citation}")
            return

        if args.memory:
            memory_engine = LongTermMemoryEngine(system.settings.database)
            refresh_summary = memory_engine.refresh_from_index()
            conversations = ConversationMemory(system.settings.database).list_recent(limit=10)
            preferences = PreferenceMemory(system.settings.database).all()
            print(
                "Memory refreshed | "
                f"processed_files={refresh_summary['processed_files']} "
                f"entities={refresh_summary['entities']} "
                f"relationships={refresh_summary['relationships']} "
                f"facts={refresh_summary['facts']}"
            )
            print(f"Conversation records: {len(conversations)}")
            print(f"Preferences: {len(preferences)}")
            return

        if args.memory_search is not None:
            memory_engine = LongTermMemoryEngine(system.settings.database)
            memory_engine.refresh_from_index()
            query = args.memory_search
            conversation_hits = ConversationMemory(system.settings.database).search(query)
            preference_hits = PreferenceMemory(system.settings.database).search(query)
            project_hits = ProjectMemory(system.settings.database).search(query)
            graph = KnowledgeGraphQuery(system.settings.database).related_to(query)
            print(
                "Memory search results | "
                f"query={query} conversations={len(conversation_hits)} preferences={len(preference_hits)} "
                f"projects={len(project_hits)} entities={len(graph['entities'])} relationships={len(graph['relationships'])}"
            )
            return

        if args.timeline is not None:
            memory_engine = LongTermMemoryEngine(system.settings.database)
            memory_engine.refresh_from_index()
            events = memory_engine.timeline.query(args.timeline)
            print(f"Timeline events for {args.timeline}: {len(events)}")
            for event in events[:20]:
                print(
                    f"{event['event_date']} | {event['event_type']} | "
                    f"project={event['project_name']} entity={event['entity_name']} "
                    f"source={event['source_document']}"
                )
            return

        if args.project is not None:
            memory_engine = LongTermMemoryEngine(system.settings.database)
            memory_engine.refresh_from_index()
            project_name = args.project
            project = ProjectMemory(system.settings.database).get(project_name)
            graph = KnowledgeGraphQuery(system.settings.database).project(project_name)
            if project is None:
                print(f"No project memory found for: {project_name}")
                return
            print(
                f"Project {project['name']} | files={len(project['related_files'])} "
                f"people={len(project['related_people'])} confidence={project['confidence']:.2f}"
            )
            print(f"Summary: {project['summary']}")
            print(f"Graph relationships: {len(graph['relationships'])}")
            return

        if args.person is not None:
            memory_engine = LongTermMemoryEngine(system.settings.database)
            memory_engine.refresh_from_index()
            person_graph = KnowledgeGraphQuery(system.settings.database).person(args.person)
            print(
                f"Person query {args.person} | entities={len(person_graph['entities'])} "
                f"relationships={len(person_graph['relationships'])} facts={len(person_graph['facts'])}"
            )
            for fact in person_graph["facts"][:10]:
                print(f"- {fact['fact']} (source={fact['source_document']})")
            return

        if agents_flag or agent_list_flag:
            registry = AgentRegistry()
            registry.discover()
            print(json.dumps(registry.list_agents(), indent=2))
            return

        if workflow_list_flag:
            workflows = WorkflowRegistry()
            print(json.dumps(workflows.list_workflows(), indent=2))
            return

        if plan_value is not None:
            agents = AgentRegistry()
            agents.discover()
            planner = TaskPlanner(agents)
            queue = TaskQueue(system.settings.database)
            tasks = planner.plan(plan_value, requested_by="cli")
            queue.enqueue_many(tasks)
            print(f"Planned tasks: {len(tasks)}")
            return

        if execute_flag:
            registry = AgentRegistry()
            registry.discover()
            queue = TaskQueue(system.settings.database)
            context_engine = ContextEngine(system.settings)
            agent_history = AgentHistoryStore(system.settings.database)
            task_history = TaskHistoryStore(system.settings.database)
            _, tool_executor, _ = _build_tooling(system.settings.database)
            executor = AgentExecutor(registry, context_engine, agent_history, tool_executor=tool_executor)
            engine = TaskExecutionEngine(queue, executor, task_history)
            results = engine.execute(approve_pending=True)
            print(f"Executed tasks: {len(results)}")
            return

        tooling_requested = any(
            [
                tools_flag,
                tool_list_flag,
                bool(tool_info_value),
                bool(tool_test_value),
                plugin_list_flag,
                bool(plugin_load_value),
                bool(plugin_unload_value),
            ]
        )
        if tooling_requested:
            tool_registry, tool_executor, plugin_manager = _build_tooling(system.settings.database)

            if tools_flag or tool_list_flag:
                print(json.dumps(tool_registry.list_tools(), indent=2))
                return

            if tool_info_value:
                tool = tool_registry.get_tool(str(tool_info_value))
                if tool is None:
                    print(f"Tool not found: {tool_info_value}")
                    return
                print(json.dumps(tool.descriptor().__dict__, indent=2))
                return

            if tool_test_value:
                tool = tool_registry.get_tool(str(tool_test_value))
                if tool is None:
                    print(f"Tool not found: {tool_test_value}")
                    return
                inputs = _default_tool_test_inputs(tool.name)
                result = tool_executor.execute(tool.tool_id, inputs, agent_name="cli", workflow_name="tool-test")
                print(json.dumps(result, indent=2))
                return

            if plugin_list_flag:
                discovered = plugin_manager.loader.discover()
                installed = plugin_manager.list_plugins()
                print(json.dumps({"discovered": discovered, "installed": installed}, indent=2))
                return

            if plugin_load_value:
                ok, message = plugin_manager.load_plugin(str(plugin_load_value))
                print(message)
                if not ok:
                    raise SystemExit(1)
                return

            if plugin_unload_value:
                ok, message = plugin_manager.unload_plugin(str(plugin_unload_value))
                print(message)
                if not ok:
                    raise SystemExit(1)
                return

        print(system.summary())
    except ValueError as exc:
        error_logger.exception("runtime validation error")
        raise SystemExit(str(exc)) from exc
    except Exception as exc:
        error_logger.exception("unexpected runtime error")
        raise SystemExit(f"Unexpected error: {exc}") from exc


if __name__ == "__main__":
    main()
