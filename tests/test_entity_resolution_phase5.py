import unittest

from app.entity_resolution import EntityResolver


class EntityResolutionPhase5Tests(unittest.TestCase):
    def test_entity_resolution_merges_aliases(self) -> None:
        resolver = EntityResolver()
        resolved = resolver.resolve(
            [
                {"name": "Mike", "entity_type": "person", "confidence": 0.6},
                {"name": "Mr. Mike", "entity_type": "person", "confidence": 0.8},
                {"name": "Michael", "entity_type": "person", "confidence": 0.7},
            ]
        )

        self.assertEqual(len(resolved), 2)
        canonical_names = {item.canonical_name for item in resolved}
        self.assertIn("Mike", canonical_names)
        self.assertIn("Michael", canonical_names)


if __name__ == "__main__":
    unittest.main()
