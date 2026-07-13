import unittest

from app.entity_extraction import RuleBasedEntityExtractor


class EntityExtractionPhase5Tests(unittest.TestCase):
    def test_rule_based_extraction_detects_core_types(self) -> None:
        extractor = RuleBasedEntityExtractor()
        text = (
            "Mr. Mike works at Luxoria Company in Brussels. "
            "Passport expires 2029 and insurance renewal is $450. "
            "Date: 2025-03-10. Address: 10 Baker Street."
        )
        entities = extractor.extract(text, source_path="/vault/Luxoria/passport_notes.txt")
        pairs = {(entity.entity_type, entity.name.lower()) for entity in entities}

        self.assertIn(("person", "mr. mike"), pairs)
        self.assertIn(("organization", "luxoria company"), pairs)
        self.assertIn(("city", "brussels"), pairs)
        self.assertIn(("money", "$450"), pairs)
        self.assertIn(("date", "2025-03-10"), pairs)
        self.assertIn(("file_name", "passport_notes.txt"), pairs)


if __name__ == "__main__":
    unittest.main()
