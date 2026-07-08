from __future__ import annotations

import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.filetypes.supported import SUPPORTED_EXTENSIONS
from app.logging import get_error_logger, get_file_logger
from app.vault.engine import VaultEngine


class VaultEventHandler(FileSystemEventHandler):
    def __init__(self, engine: VaultEngine) -> None:
        self.engine = engine
        self.logger = get_file_logger("watcher", "watcher.log")
        self.error_logger = get_error_logger("watcher")

    def _should_process(self, event: FileSystemEvent) -> bool:
        if event.is_directory:
            return False
        suffix = Path(event.src_path).suffix.lower()
        return suffix in SUPPORTED_EXTENSIONS

    def on_created(self, event: FileSystemEvent) -> None:
        if not self._should_process(event):
            return
        path = Path(event.src_path)
        try:
            self.engine.index_single_path(path)
            self.logger.info("file added | %s", event.src_path)
        except Exception:
            self.error_logger.exception("watcher on_created failed | %s", event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not self._should_process(event):
            return
        path = Path(event.src_path)
        try:
            self.engine.index_single_path(path)
            self.logger.info("file modified | %s", event.src_path)
        except Exception:
            self.error_logger.exception("watcher on_modified failed | %s", event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        suffix = Path(event.src_path).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            return
        path = Path(event.src_path)
        try:
            self.engine.remove_single_path(path)
            self.logger.info("file removed | %s", event.src_path)
        except Exception:
            self.error_logger.exception("watcher on_deleted failed | %s", event.src_path)


def watch_vault(engine: VaultEngine) -> None:
    if not engine.settings.vault_path.strip():
        raise ValueError("VAULT_PATH is required")

    root = Path(engine.settings.vault_path)
    if not root.exists() or not root.is_dir():
        raise ValueError("VAULT_PATH does not exist or is not a directory")

    observer = Observer()
    handler = VaultEventHandler(engine)
    observer.schedule(handler, str(root), recursive=True)
    observer.start()

    logger = get_file_logger("watcher", "watcher.log")
    logger.info("watcher started | root=%s", str(root))

    try:
        while True:
            time.sleep(max(1, engine.settings.scan_interval))
    except KeyboardInterrupt:
        logger.info("watcher stopping")
        observer.stop()
    observer.join()
