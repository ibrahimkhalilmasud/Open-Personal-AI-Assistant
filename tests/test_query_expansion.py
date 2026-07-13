import unittest

from app.query import QueryExpander


class QueryExpansionTests(unittest.TestCase):
    def test_expander_adds_synonyms(self) -> None:
        expander = QueryExpander()
        expanded = expander.expand("medical insurance", ["medical", "insurance"])

        self.assertIn("doctor", expanded.expanded_terms)
        self.assertIn("policy", expanded.expanded_terms)
        self.assertIn("insurance", expanded.expanded_terms)


if __name__ == "__main__":
    unittest.main()
