from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.filetypes.supported import SUPPORTED_EXTENSIONS
from app.metadata.extractors import extract_document_text, extract_image_metadata, extract_video_metadata
from app.vault.hashing import compute_sha256


@dataclass(slots=True)
class IndexedFile:
    path: str
    filename: str
    extension: str
    file_size: int
    created_date: str
    modified_date: str
    sha256: str
    indexed: int
    last_scan: str
    extracted_text: str
    metadata: dict[str, str | int | float]


def index_file(file_path: Path) -> IndexedFile:
    stats = file_path.stat()
    now = datetime.now(UTC).isoformat()
    extracted_text = extract_document_text(file_path)
    metadata: dict[str, str | int | float] = {}
    metadata.update(extract_image_metadata(file_path))
    metadata.update(extract_video_metadata(file_path))

    return IndexedFile(
        path=str(file_path.resolve()),
        filename=file_path.name,
        extension=file_path.suffix.lower().lstrip("."),
        file_size=stats.st_size,
        created_date=datetime.fromtimestamp(stats.st_ctime, UTC).isoformat(),
        modified_date=datetime.fromtimestamp(stats.st_mtime, UTC).isoformat(),
        sha256=compute_sha256(file_path),
        indexed=1,
        last_scan=now,
        extracted_text=extracted_text,
        metadata=metadata,
    )


def collect_supported_files(vault_path: str) -> list[Path]:
    root = Path(vault_path)
    if not root.exists() or not root.is_dir():
        return []

    return sorted(
        candidate
        for candidate in root.rglob("*")
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS
    )
