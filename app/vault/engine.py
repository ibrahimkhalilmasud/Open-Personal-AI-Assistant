from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from app.config.settings import Settings
from app.database.sqlite_db import fetch_file_hashes, initialize_database, remove_file, upsert_indexed_file
from app.indexer.file_indexer import collect_supported_files, index_file
from app.logging.vault_logger import get_file_logger


class VaultEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scan_logger = get_file_logger("scan", "scan.log")

    def full_scan(self) -> dict[str, int]:
        initialize_database(self.settings.database)

        known_hashes = fetch_file_hashes(self.settings.database)
        current_files = collect_supported_files(self.settings.vault_path)
        current_paths = {str(path.resolve()) for path in current_files}

        new_count = 0
        changed_count = 0

        for file_path in current_files:
            indexed_file = index_file(file_path)
            payload = asdict(indexed_file)
            prior_hash = known_hashes.get(indexed_file.path)

            if prior_hash is None:
                new_count += 1
            elif prior_hash != indexed_file.sha256:
                changed_count += 1

            upsert_indexed_file(self.settings.database, payload)

        deleted_paths = sorted(set(known_hashes) - current_paths)
        for file_path in deleted_paths:
            remove_file(self.settings.database, file_path)

        summary = {
            "new": new_count,
            "changed": changed_count,
            "deleted": len(deleted_paths),
            "total": len(current_files),
        }
        self.scan_logger.info(
            "scan complete | total=%s new=%s changed=%s deleted=%s",
            summary["total"],
            summary["new"],
            summary["changed"],
            summary["deleted"],
        )
        return summary

    def index_single_path(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            return
        indexed_file = index_file(file_path)
        upsert_indexed_file(self.settings.database, asdict(indexed_file))
        self.scan_logger.info("indexed file | path=%s", indexed_file.path)

    def remove_single_path(self, file_path: Path) -> None:
        remove_file(self.settings.database, str(file_path.resolve()))
        self.scan_logger.info("removed file | path=%s", str(file_path.resolve()))
