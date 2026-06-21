import tempfile
import unittest
from pathlib import Path

from app.vault.hashing import compute_sha256


class HashingTests(unittest.TestCase):
    def test_compute_sha256_changes_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample.txt"
            target.write_text("alpha", encoding="utf-8")
            first_hash = compute_sha256(target)

            target.write_text("beta", encoding="utf-8")
            second_hash = compute_sha256(target)

            self.assertNotEqual(first_hash, second_hash)
            self.assertEqual(len(first_hash), 64)


if __name__ == "__main__":
    unittest.main()
