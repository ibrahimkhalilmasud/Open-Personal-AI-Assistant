import tempfile
import unittest
from pathlib import Path

from app.scanner.file_scanner import scan_supported_files


class ScannerTests(unittest.TestCase):
    def test_scan_supported_files_filters_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.pdf").write_text("x", encoding="utf-8")
            (root / "b.jpg").write_text("x", encoding="utf-8")
            (root / "c.exe").write_text("x", encoding="utf-8")

            results = scan_supported_files(str(root))
            names = {path.name for path in results}
            self.assertEqual(names, {"a.pdf", "b.jpg"})


if __name__ == "__main__":
    unittest.main()
