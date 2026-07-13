from __future__ import annotations

import argparse

from app.agents.context import ContextEngine
from app.agents.executor import AgentExecutor
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.core.system import create_system
from app.logging import get_application_logger, get_error_logger
from app.search import SearchEngine
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
    parser.add_argument("--agents", action="store_true", help="Show discovered agents")
    parser.add_argument("--agent-list", action="store_true", help="Show discovered agents")
    parser.add_argument("--workflow-list", action="store_true", help="Show available workflows")
    parser.add_argument("--plan", type=str, help="Create structured task plan from a natural language request")
    parser.add_argument("--execute", action="store_true", help="Approve pending tasks and execute them sequentially")
    return parser.parse_args()


def main() -> None:
    app_logger = get_application_logger("main")
    error_logger = get_error_logger("main")
    args = parse_args()
    system = create_system()
    app_logger.info("startup | %s", system.settings.settings_validation_report)

    try:
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
                print(f"\"{result.snippet}\"")
                print()
            return

        if getattr(args, "agents", False) or getattr(args, "agent_list", False):
            registry = AgentRegistry()
            registry.discover()
            agents = registry.list_agents()
            if not agents:
                print("No agents registered.")
                return
            for agent in agents:
                capabilities = ",".join(agent["capabilities"])
                print(f"{agent['name']} | v{agent['version']} | {agent['description']} | capabilities={capabilities}")
            return

        if getattr(args, "workflow_list", False):
            registry = WorkflowRegistry()
            workflows = registry.list_workflows()
            if not workflows:
                print("No workflows registered.")
                return
            for workflow in workflows:
                print(workflow)
            return

        if getattr(args, "plan", None):
            agent_registry = AgentRegistry()
            agent_registry.discover()
            planner = TaskPlanner(agent_registry)
            queue = TaskQueue(system.settings.database)
            tasks = planner.plan(request=args.plan, requested_by="cli", workflow="")
            if not tasks:
                print("No plan generated.")
                return
            queue.enqueue_many(tasks)
            print("Plan generated and saved as pending tasks:")
            for task in tasks:
                print(f"- {task.title}: {task.description} (task_id={task.task_id})")
            print("Approval required before execution. Run --execute to approve and run pending tasks.")
            return

        if getattr(args, "execute", False):
            registry = AgentRegistry()
            registry.discover()
            queue = TaskQueue(system.settings.database)
            context_engine = ContextEngine(system.settings)
            agent_history = AgentHistoryStore(system.settings.database)
            task_history = TaskHistoryStore(system.settings.database)
            agent_executor = AgentExecutor(registry, context_engine, agent_history)
            engine = TaskExecutionEngine(queue, agent_executor, task_history)
            results = engine.execute(approve_pending=True)
            if not results:
                print("No executable tasks found.")
                return
            for result in results:
                print(
                    f"{result.task_id} | {result.status} | agent={result.agent_name} "
                    f"| confidence={result.confidence:.2f} | duration={result.duration_seconds:.2f}s"
                )
                print(result.summary)
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
