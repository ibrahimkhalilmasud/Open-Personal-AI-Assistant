import unittest

from app.query import QueryAnalyzer


class QueryAnalyzerTests(unittest.TestCase):
    def test_analyzer_extracts_filters_and_intent(self) -> None:
        analyzer = QueryAnalyzer()
        result = analyzer.analyze("Find all medical reports from October 2024 in Insurance folder")

        self.assertEqual(result.intent, "retrieve")
        self.assertIn("medical", result.keywords)
        self.assertIn("October", result.entities)
        self.assertIn("after", result.date_filters)
        self.assertIn("before", result.date_filters)
        self.assertIn("Insurance", result.folder_filters)


if __name__ == "__main__":
    unittest.main()
