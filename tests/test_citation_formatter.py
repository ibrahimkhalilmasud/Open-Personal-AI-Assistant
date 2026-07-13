import unittest

from app.citations import CitationFormatter
from app.context import ContextChunk


class CitationFormatterTests(unittest.TestCase):
    def test_formatter_outputs_unique_citations(self) -> None:
        formatter = CitationFormatter()
        chunks = [
            ContextChunk(1, 0.9, "x", "Medical Report.pdf", "/vault/Medical/Medical Report.pdf", 4, "a", ""),
            ContextChunk(2, 0.8, "y", "Medical Report.pdf", "/vault/Medical/Medical Report.pdf", 4, "a", ""),
        ]

        citations = formatter.format(chunks)
        sources = formatter.as_sources(citations)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0].folder, "Medical")
        self.assertEqual(sources[0]["filename"], "Medical Report.pdf")


if __name__ == "__main__":
    unittest.main()
