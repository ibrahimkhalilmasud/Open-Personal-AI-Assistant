import unittest

from app.context import ContextBuilder


class ContextBuilderTests(unittest.TestCase):
    def test_context_builder_deduplicates_and_applies_limits(self) -> None:
        builder = ContextBuilder(max_chunks=2, max_tokens=20)
        bundle = builder.build(
            [
                {
                    "score": 0.8,
                    "text": "insurance renewal details with policy and coverage",
                    "filename": "a.txt",
                    "path": "/vault/a.txt",
                    "page": 1,
                    "chunk_id": "a::1",
                    "modified_date": "2025-02-01T00:00:00+00:00",
                },
                {
                    "score": 0.8,
                    "text": "insurance renewal details with policy and coverage",
                    "filename": "a.txt",
                    "path": "/vault/a.txt",
                    "page": 1,
                    "chunk_id": "a::1",
                    "modified_date": "2025-01-01T00:00:00+00:00",
                },
                {
                    "score": 0.75,
                    "text": "travel invoice and reservation details",
                    "filename": "b.txt",
                    "path": "/vault/b.txt",
                    "page": 1,
                    "chunk_id": "b::1",
                    "modified_date": "2025-03-01T00:00:00+00:00",
                },
            ]
        )

        self.assertEqual(len(bundle.chunks), 2)
        self.assertGreater(bundle.estimated_tokens, 0)


if __name__ == "__main__":
    unittest.main()
