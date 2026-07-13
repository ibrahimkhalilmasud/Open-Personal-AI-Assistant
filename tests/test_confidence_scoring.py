import unittest

from app.reasoning import ConfidenceScorer


class ConfidenceScoringTests(unittest.TestCase):
    def test_confidence_labels(self) -> None:
        scorer = ConfidenceScorer()

        high = scorer.score([0.95, 0.9], used_chunks=4, insufficient_context=False)
        low = scorer.score([], used_chunks=0, insufficient_context=True)

        self.assertEqual(scorer.label(high), "High")
        self.assertEqual(scorer.label(low), "Low")


if __name__ == "__main__":
    unittest.main()
