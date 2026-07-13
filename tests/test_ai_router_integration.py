import unittest
from unittest.mock import MagicMock, patch

from app.config.settings import Settings
from app.router.ai_router import AIRouter


class AIRouterIntegrationTests(unittest.TestCase):
    @patch("app.router.ai_router.requests.post")
    def test_router_falls_back_to_next_provider(self, post: MagicMock) -> None:
        settings = Settings(
            default_model="gemini-1.5-flash",
            google_api_key="g-key",
            openai_api_key="o-key",
            model_timeout_seconds=10,
        )
        router = AIRouter.from_settings(settings)

        failed = MagicMock()
        failed.raise_for_status.side_effect = RuntimeError("gemini down")

        success = MagicMock()
        success.raise_for_status.return_value = None
        success.json.return_value = {
            "choices": [{"message": {"content": "grounded answer"}}],
        }

        post.side_effect = [failed, success]

        output = router.generate(system_prompt="sys", user_prompt="user", selected_model="gemini-1.5-flash")

        self.assertEqual(output["provider"], "openai")
        self.assertEqual(output["answer"], "grounded answer")


if __name__ == "__main__":
    unittest.main()
