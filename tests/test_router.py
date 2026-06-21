import unittest

from app.config.settings import Settings
from app.router.ai_router import AIRouter


class RouterTests(unittest.TestCase):
    def test_router_provider_priority_local_first(self) -> None:
        settings = Settings(
            google_api_key="g",
            groq_api_key="k",
            openai_api_key="o",
        )
        router = AIRouter.from_settings(settings)
        self.assertEqual(router.available_providers, ["local", "gemini", "groq", "openai"])
        self.assertEqual(router.preferred_provider(), "local")


if __name__ == "__main__":
    unittest.main()
