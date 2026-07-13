from __future__ import annotations

from dataclasses import dataclass

from app.context import ContextBundle
from app.query import QueryAnalysis


@dataclass(slots=True)
class PromptPackage:
    system_prompt: str
    user_prompt: str


class PromptBuilder:
    def build(self, question: str, analysis: QueryAnalysis, context: ContextBundle) -> PromptPackage:
        system_prompt = (
            "You are a personal knowledge assistant. "
            "Answer only from supplied context. "
            "Do not hallucinate or infer unsupported facts. "
            "If context is insufficient, explicitly say so. "
            "Always include citations that map to context chunk references."
        )

        context_blocks: list[str] = []
        for chunk in context.chunks:
            context_blocks.append(
                "\n".join(
                    [
                        f"[C{chunk.rank}] filename={chunk.filename}",
                        f"path={chunk.path}",
                        f"page={chunk.page}",
                        f"chunk_id={chunk.chunk_id}",
                        f"score={chunk.score:.3f}",
                        f"text={chunk.text}",
                    ]
                )
            )

        user_prompt = "\n\n".join(
            [
                f"Question: {question}",
                f"Intent: {analysis.intent}",
                f"Keywords: {', '.join(analysis.keywords)}",
                f"Entities: {', '.join(analysis.entities)}",
                f"Date filters: {analysis.date_filters}",
                f"Folder filters: {analysis.folder_filters}",
                f"File type filters: {analysis.file_type_filters}",
                f"Context token estimate: {context.estimated_tokens}",
                "Retrieved context:\n" + "\n\n".join(context_blocks),
                "Return a grounded answer and cite chunk references such as [C1], [C2].",
            ]
        )

        return PromptPackage(system_prompt=system_prompt, user_prompt=user_prompt)
