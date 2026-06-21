import unittest

from app.vector.chunking import chunk_document


class ChunkingTests(unittest.TestCase):
    def test_chunk_document_uses_size_and_overlap(self) -> None:
        words = [f"w{i}" for i in range(1200)]
        text = " ".join(words)

        chunks = chunk_document(
            text=text,
            source_path="/vault/doc.txt",
            filename="doc.txt",
            chunk_size=500,
            chunk_overlap=100,
        )

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].chunk_number, 1)
        self.assertEqual(chunks[1].chunk_number, 2)
        self.assertEqual(chunks[2].chunk_number, 3)
        self.assertTrue(chunks[0].id.endswith("chunk::1"))


if __name__ == "__main__":
    unittest.main()
