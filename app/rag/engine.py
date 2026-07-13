from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from app.citations import CitationFormatter
from app.config.settings import Settings
from app.context import ContextBuilder
from app.prompts import PromptBuilder
from app.query import QueryAnalyzer, QueryExpander
from app.reasoning import AnswerGenerator, ConfidenceScorer
from app.router.ai_router import AIRouter
from app.rag.retriever import HybridRetriever

INSUFFICIENT_CONTEXT_MESSAGE = "I could not find enough information in your Personal Vault to answer this question."


@dataclass(slots=True)
class RAGEngine:
    settings: Settings
    router: AIRouter

    def __post_init__(self) -> None:
        self.query_analyzer = QueryAnalyzer()
        self.query_expander = QueryExpander(synonyms_file=self.settings.query_synonyms_file)
        self.retriever = HybridRetriever(self.settings)
        self.context_builder = ContextBuilder(
            max_chunks=self.settings.max_context_chunks,
            max_tokens=self.settings.max_context_tokens,
        )
        self.prompt_builder = PromptBuilder()
        self.answer_generator = AnswerGenerator(self.router)
        self.citation_formatter = CitationFormatter()
        self.confidence_scorer = ConfidenceScorer()

    def ask(
        self,
        question: str,
        *,
        model: str | None = None,
        stream: bool = False,
        on_token: Callable[[str], None] | None = None,
    ) -> dict[str, object]:
        overall_started = time.perf_counter()

        analysis_started = time.perf_counter()
        analysis = self.query_analyzer.analyze(question)
        expansion = self.query_expander.expand(question, analysis.keywords)
        analysis_time = time.perf_counter() - analysis_started

        retrieval_started = time.perf_counter()
        folder = analysis.folder_filters[0] if analysis.folder_filters else None
        file_type = analysis.file_type_filters[0] if analysis.file_type_filters else None
        after = analysis.date_filters.get("after") if analysis.date_filters else None
        before = analysis.date_filters.get("before") if analysis.date_filters else None
        retrieval = self.retriever.retrieve(
            query_terms=expansion.expanded_terms or [question],
            top_k=max(self.settings.max_context_chunks * 3, 12),
            folder=folder,
            file_type=file_type,
            after=after,
            before=before,
        )
        retrieval_time = time.perf_counter() - retrieval_started

        context_started = time.perf_counter()
        context = self.context_builder.build(retrieval.results)
        context_time = time.perf_counter() - context_started

        if not context.chunks:
            confidence = self.confidence_scorer.score([], 0, insufficient_context=True)
            total_time = time.perf_counter() - overall_started
            return {
                "answer": INSUFFICIENT_CONTEXT_MESSAGE,
                "confidence": confidence,
                "confidence_label": self.confidence_scorer.label(confidence),
                "sources": [],
                "citations": [],
                "provider": "none",
                "model": "none",
                "timings": {
                    "analysis_seconds": round(analysis_time, 4),
                    "retrieval_seconds": round(retrieval_time, 4),
                    "context_seconds": round(context_time, 4),
                    "model_seconds": 0.0,
                    "total_seconds": round(total_time, 4),
                },
                "retrieval_metadata": {
                    "terms": expansion.expanded_terms,
                    "result_count": len(retrieval.results),
                    "used_chunks": 0,
                    "truncated": context.truncated,
                    "estimated_tokens": context.estimated_tokens,
                },
            }

        prompt_package = self.prompt_builder.build(question, analysis, context)

        model_started = time.perf_counter()
        generated = self.answer_generator.generate(
            prompt_package,
            model=model,
            stream=stream,
            on_token=on_token,
        )
        model_time = time.perf_counter() - model_started

        citations = self.citation_formatter.format(context.chunks)
        sources = self.citation_formatter.as_sources(citations)
        retrieval_scores = [float(item.get("score", 0.0) or 0.0) for item in retrieval.results]
        confidence = self.confidence_scorer.score(retrieval_scores, len(context.chunks), insufficient_context=False)

        total_time = time.perf_counter() - overall_started
        return {
            "answer": generated.answer,
            "confidence": round(confidence, 2),
            "confidence_label": self.confidence_scorer.label(confidence),
            "sources": sources,
            "citations": self.citation_formatter.to_display_lines(citations),
            "provider": generated.provider,
            "model": generated.model,
            "timings": {
                "analysis_seconds": round(analysis_time, 4),
                "retrieval_seconds": round(retrieval_time, 4),
                "context_seconds": round(context_time, 4),
                "model_seconds": round(model_time, 4),
                "total_seconds": round(total_time, 4),
            },
            "retrieval_metadata": {
                "terms": expansion.expanded_terms,
                "result_count": len(retrieval.results),
                "used_chunks": len(context.chunks),
                "truncated": context.truncated,
                "estimated_tokens": context.estimated_tokens,
            },
        }
