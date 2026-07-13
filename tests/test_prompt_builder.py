import unittest

from app.context import ContextBundle, ContextChunk
from app.prompts import PromptBuilder
from app.query import QueryAnalysis


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_builder_structures_prompt(self) -> None:
        builder = PromptBuilder()
        analysis = QueryAnalysis(intent="summarize", keywords=["medical"], entities=[], date_filters={})
        context = ContextBundle(
            chunks=[
                ContextChunk(
                    rank=1,
                    score=0.9,
                    text="medical report summary",
                    filename="Medical.pdf",
                    path="/vault/Medical.pdf",
                    page=4,
                    chunk_id="doc::1",
                    modified_date="2025-01-01T00:00:00+00:00",
                )
            ],
            estimated_tokens=10,
            truncated=False,
        )

        prompts = builder.build("Summarize my medical history", analysis, context)

        self.assertIn("Answer only from supplied context", prompts.system_prompt)
        self.assertIn("Question: Summarize my medical history", prompts.user_prompt)
        self.assertIn("[C1]", prompts.user_prompt)


if __name__ == "__main__":
    unittest.main()
