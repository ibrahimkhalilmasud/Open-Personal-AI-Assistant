from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from app.config.settings import Settings
from app.database.sqlite_db import fetch_file_hashes, initialize_database, remove_file, upsert_indexed_file
from app.indexer.file_indexer import collect_supported_files, index_file
from app.logging import get_application_logger, get_error_logger, get_file_logger
from app.vector.indexing import VectorIndexer


class VaultEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scan_logger = get_file_logger("scan", "scan.log")
        self.application_logger = get_application_logger("vault.engine")
        self.error_logger = get_error_logger("vault.engine")
        self.vector_indexer = VectorIndexer(settings)

    def _vault_path_or_raise(self) -> str:
        if not self.settings.vault_path.strip():
            raise ValueError("VAULT_PATH is required")
        return self.settings.vault_path

    def full_scan(self) -> dict[str, int]:
        initialize_database(self.settings.database)
        self.application_logger.info("full_scan started")

        known_hashes = fetch_file_hashes(self.settings.database)
        current_files = collect_supported_files(self._vault_path_or_raise())
        current_paths = {str(path.resolve()) for path in current_files}

        new_count = 0
        changed_count = 0

        for file_path in current_files:
            try:
                indexed_file = index_file(file_path)
            except Exception:
                self.error_logger.exception("index_file failed | path=%s", str(file_path))
                continue
            prior_hash = known_hashes.get(indexed_file.path)

            if prior_hash is None:
                new_count += 1
                upsert_indexed_file(self.settings.database, asdict(indexed_file))
            elif prior_hash != indexed_file.sha256:
                changed_count += 1
                upsert_indexed_file(self.settings.database, asdict(indexed_file))

        deleted_paths = sorted(set(known_hashes) - current_paths)
        for file_path in deleted_paths:
            remove_file(self.settings.database, file_path)
            self.vector_indexer.remove_path(file_path)

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
        self.application_logger.info("full_scan complete | %s", summary)
        return summary

    def index_single_path(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            return
        try:
            indexed_file = index_file(file_path)
            upsert_indexed_file(self.settings.database, asdict(indexed_file))
            self.vector_indexer.index_path(indexed_file.path)
            self.scan_logger.info("indexed file | path=%s", indexed_file.path)
        except Exception:
            self.error_logger.exception("index_single_path failed | path=%s", str(file_path))

    def remove_single_path(self, file_path: Path) -> None:
        path = str(file_path.resolve())
        remove_file(self.settings.database, path)
        self.vector_indexer.remove_path(path)
        self.scan_logger.info("removed file | path=%s", path)
