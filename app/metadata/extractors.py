from __future__ import annotations

from pathlib import Path

from app.filetypes.supported import DOCUMENT_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from app.logging import get_error_logger

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None

error_logger = get_error_logger("metadata.extractors")


def extract_document_text(path: Path) -> str:
    extension = path.suffix.lower()
    if extension not in DOCUMENT_EXTENSIONS:
        return ""

    try:
        if extension in {".txt", ".md"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if extension == ".docx" and Document is not None:
            doc = Document(str(path))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        if extension == ".csv" and pd is not None:
            frame = pd.read_csv(path)
            return frame.to_csv(index=False)
        if extension == ".xlsx" and pd is not None:
            frame = pd.read_excel(path)
            return frame.to_csv(index=False)
        if extension == ".pdf" and fitz is not None:
            with fitz.open(path) as pdf:
                if getattr(pdf, "is_encrypted", False):
                    return ""
                return "\n".join(page.get_text("text") for page in pdf)
    except Exception:
        error_logger.exception("document extraction failed | path=%s", str(path))
        return ""

    return ""


def extract_image_metadata(path: Path) -> dict[str, str | int]:
    if path.suffix.lower() not in IMAGE_EXTENSIONS or Image is None:
        return {}

    try:
        with Image.open(path) as image:
            exif_raw = image.getexif() or {}
            exif_data = {str(key): str(value) for key, value in exif_raw.items()}
            return {
                "width": int(image.width),
                "height": int(image.height),
                "file_size": path.stat().st_size,
                "exif": str(exif_data),
            }
    except Exception:
        error_logger.exception("image metadata extraction failed | path=%s", str(path))
        return {}


def extract_video_metadata(path: Path) -> dict[str, str | int | float]:
    if path.suffix.lower() not in VIDEO_EXTENSIONS or cv2 is None:
        return {}

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        error_logger.error("video metadata extraction failed to open | path=%s", str(path))
        return {}

    try:
        fps = capture.get(cv2.CAP_PROP_FPS) or 0
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration = float(frame_count / fps) if fps > 0 else 0.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        return {
            "duration_seconds": duration,
            "resolution": f"{width}x{height}",
        }
    finally:
        capture.release()
