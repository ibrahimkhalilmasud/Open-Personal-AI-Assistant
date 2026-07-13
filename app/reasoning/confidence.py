from __future__ import annotations


class ConfidenceScorer:
    def score(self, retrieval_scores: list[float], used_chunks: int, insufficient_context: bool) -> float:
        if insufficient_context or used_chunks == 0:
            return 0.0
        if not retrieval_scores:
            return 0.2

        top = sorted((max(0.0, min(1.0, value)) for value in retrieval_scores), reverse=True)[:5]
        average = sum(top) / len(top)
        chunk_bonus = min(0.2, used_chunks * 0.03)
        return max(0.0, min(1.0, average * 0.9 + chunk_bonus))

    def label(self, value: float) -> str:
        if value >= 0.9:
            return "High"
        if value >= 0.7:
            return "Medium"
        return "Low"
