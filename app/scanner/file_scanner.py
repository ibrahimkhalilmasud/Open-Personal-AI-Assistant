from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".md",
    ".jpg", ".png", ".webp", ".tiff",
    ".mp4", ".mov", ".avi",
    ".mp3", ".wav", ".m4a",
    ".zip",
}


def scan_supported_files(vault_path: str) -> list[Path]:
    root = Path(vault_path)
    if not root.exists() or not root.is_dir():
        return []
    return sorted(
        file_path
        for file_path in root.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
