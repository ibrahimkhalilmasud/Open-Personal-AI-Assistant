from __future__ import annotations

import argparse

import uvicorn

from app.agents.context import ContextEngine
from app.agents.executor import AgentExecutor
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.api.server import create_app
from app.core.system import create_system
from app.knowledge_graph.query import KnowledgeGraphQuery
from app.knowledge_graph.timeline import TimelineEngine
from app.logging import get_application_logger, get_error_logger
from app.memory import ConversationMemory, LongTermMemoryEngine, PreferenceMemory, ProjectMemory
from app.rag import RAGEngine
from app.search import SearchEngine
from app.sdk import Client
from app.tasks.executor import TaskExecutionEngine
from app.tasks.history import TaskHistoryStore
from app.tasks.planner import TaskPlanner
from app.tasks.queue import TaskQueue
from app.vault.engine import VaultEngine
from app.workflows.registry import WorkflowRegistry


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
    parser.add_argument("--ask", type=str, help="Ask a grounded RAG question")
    parser.add_argument("--model", type=str, help="Model to use for --ask")
    parser.add_argument("--stream", action="store_true", help="Stream model tokens")
    parser.add_argument("--agents", action="store_true", help="Show available agents")
    parser.add_argument("--agent-list", action="store_true", help="Show available agents")
    parser.add_argument("--workflow-list", action="store_true", help="List registered workflows")
    parser.add_argument("--plan", type=str, help="Plan tasks using a planning agent")
    parser.add_argument("--execute", action="store_true", help="Execute approved tasks")
    parser.add_argument("--memory", action="store_true", help="Show persistent memory overview")
    parser.add_argument("--memory-search", type=str, help="Search memory and knowledge graph")
    parser.add_argument("--timeline", type=str, help="Show timeline for year/month prefix (e.g. 2025 or 2025-03)")
    parser.add_argument("--project", type=str, help="Show memory and graph details for a project")
    parser.add_argument("--person", type=str, help="Show memory and graph details for a person")
    parser.add_argument("--api", action="store_true", help="Run REST API server")
    parser.add_argument("--health", action="store_true", help="Show service health")
    parser.add_argument("--status", action="store_true", help="Show service status")
    parser.add_argument("--metrics", action="store_true", help="Show service metrics")
    parser.add_argument("--sdk-test", action="store_true", help="Run internal SDK connectivity test")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    return parser.parse_args()


def _print_rag_response(payload: dict[str, object]) -> None:
    print(payload.get("answer", ""))
    print(f"Confidence: {payload.get('confidence', 0.0)} ({payload.get('confidence_label', 'Unknown')})")
    print(f"Provider: {payload.get('provider', 'unknown')} | Model: {payload.get('model', 'unknown')}")
    citations = payload.get("citations", [])
    if citations:
        print("Citations:")
        for line in citations:
            print(f"- {line}")


def main() -> None:
    app_logger = get_application_logger("main")
    error_logger = get_error_logger("main")
    args = parse_args()
    system = create_system()
    app_logger.info("startup | %s", system.settings.settings_validation_report)

    try:
        if getattr(args, "api", False):
            uvicorn.run(create_app(), host=args.host, port=args.port)
            return

        if getattr(args, "health", False):
            from app.services import HealthService

            print(HealthService(system).health())
            return

        if getattr(args, "status", False):
            from app.services import HealthService

            print(HealthService(system).status())
            return

        if getattr(args, "metrics", False):
            from app.services import SystemService

            print(SystemService(system).metrics())
            return

        if getattr(args, "sdk_test", False):
            client = Client(base_url=f"http://{args.host}:{args.port}")
            print({"health": client.health(), "status": client.status(), "metrics": client.metrics()})
            return

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

        if getattr(args, "ask", None) is not None:
            rag_engine = RAGEngine(system.settings, system.router)
            _print_rag_response(
                rag_engine.ask(
                    question=args.ask,
                    model=getattr(args, "model", None),
                    stream=getattr(args, "stream", False),
                )
            )
            return

        if args.agents or args.agent_list:
            registry = AgentRegistry()
            registry.discover()
            print(registry.list_agents())
            return

        if args.workflow_list:
            workflows = WorkflowRegistry().list_workflows()
            print(workflows)
            return

        if args.plan:
            registry = AgentRegistry()
            registry.discover()
            queue = TaskQueue(system.settings.database)
            tasks = TaskPlanner(registry).plan(args.plan)
            queue.enqueue_many(tasks)
            print([task.to_dict() for task in tasks])
            return

        if args.execute:
            registry = AgentRegistry()
            registry.discover()
            queue = TaskQueue(system.settings.database)
            agent_executor = AgentExecutor(
                registry,
                ContextEngine(system.settings),
                AgentHistoryStore(system.settings.database),
            )
            executor = TaskExecutionEngine(queue, agent_executor, TaskHistoryStore(system.settings.database))
            print([item.to_dict() for item in executor.execute(approve_pending=True)])
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
            events = TimelineEngine(system.settings.database).query(args.timeline)
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

        print(system.summary())
    except ValueError as exc:
        error_logger.exception("runtime validation error")
        raise SystemExit(str(exc)) from exc
    except Exception as exc:
        error_logger.exception("unexpected runtime error")
        raise SystemExit(f"Unexpected error: {exc}") from exc


if __name__ == "__main__":
    main()
