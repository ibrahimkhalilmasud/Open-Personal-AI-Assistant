from __future__ import annotations

import argparse

from app.core.system import create_system
from app.vault.engine import VaultEngine
from app.vault.watcher import watch_vault


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-Personal-OS")
    parser.add_argument("--scan", action="store_true", help="Scan vault and update database")
    parser.add_argument("--watch", action="store_true", help="Watch vault for file changes")
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
        engine = VaultEngine(system.settings)
        watch_vault(engine)
        return

    print(system.summary())


if __name__ == "__main__":
    main()
