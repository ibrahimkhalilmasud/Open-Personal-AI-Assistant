import tempfile
import unittest
from pathlib import Path

from app.metadata.extractors import extract_document_text


class MetadataExtractorTests(unittest.TestCase):
    def test_corrupted_pdf_returns_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.pdf"
            path.write_bytes(b"not-a-valid-pdf")
            text = extract_document_text(path)
            self.assertEqual(text, "")


if __name__ == "__main__":
    unittest.main()
