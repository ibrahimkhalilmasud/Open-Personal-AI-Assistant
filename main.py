from __future__ import annotations

import argparse

from app.core.system import create_system
from app.logging import get_application_logger, get_error_logger
from app.rag import RAGEngine
from app.search import SearchEngine
from app.vault.engine import VaultEngine


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
    parser.add_argument("--ask", type=str, help="Ask grounded question using Personal Vault context")
    parser.add_argument("--model", type=str, help="Override AI model for --ask")
    parser.add_argument("--stream", action="store_true", help="Enable streaming response when supported")
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

        if args.ask is not None:
            rag_engine = RAGEngine(system.settings, system.router)

            def _on_token(token: str) -> None:
                print(token, end="", flush=True)

            answer = rag_engine.ask(
                args.ask,
                model=args.model,
                stream=args.stream,
                on_token=_on_token if args.stream else None,
            )
            if args.stream:
                print()

            print("Answer:")
            print(str(answer["answer"]))
            print()
            print(f"Confidence: {answer['confidence']} ({answer['confidence_label']})")
            print(f"Provider: {answer['provider']}")
            print(f"Model: {answer['model']}")
            citations = answer.get("citations", [])
            if citations:
                print("Citations:")
                for item in citations:
                    print(f"- {item}")
            else:
                print("Citations: none")

            timings = answer.get("timings", {})
            if isinstance(timings, dict):
                print(
                    "Performance | "
                    f"retrieval={timings.get('retrieval_seconds', 0)}s "
                    f"context={timings.get('context_seconds', 0)}s "
                    f"model={timings.get('model_seconds', 0)}s "
                    f"total={timings.get('total_seconds', 0)}s"
                )
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
