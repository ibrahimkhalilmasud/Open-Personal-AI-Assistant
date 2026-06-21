from __future__ import annotations

import argparse

from app.core.system import create_system
from app.search import SearchEngine
from app.vault.engine import VaultEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-Personal-OS")
    parser.add_argument("--scan", action="store_true", help="Scan vault and update database")
    parser.add_argument("--watch", action="store_true", help="Watch vault for file changes")
    parser.add_argument("--index", action="store_true", help="Build semantic vector index")
    parser.add_argument("--auto-index", action="store_true", help="Run scan+index and continuous auto indexing")
    parser.add_argument("--search", type=str, help="Run hybrid semantic search")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    system = create_system()

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
            f"indexed={index_summary.indexed} skipped={index_summary.skipped} failed={index_summary.failed}"
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
        results = search_engine.search(args.search, top_k=10)
        if not results:
            print("No results found.")
            return
        for index, result in enumerate(results, start=1):
            print(f"Result {index}")
            print(f"Score: {result.score:.2f}")
            print(f"File: {result.filename}")
            print(f"Path: {result.path}")
            print("Snippet:")
            print(f"\"{result.snippet}\"")
            print()
        return

    print(system.summary())


if __name__ == "__main__":
    main()
