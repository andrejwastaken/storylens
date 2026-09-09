"""Abstract LLM provider interface.

Keep this small and stable so a new provider (e.g. a local Ollama model)
can be dropped in later without touching the rest of the app. Every
provider implementation must return the same Pydantic schema objects
defined in app.services.llm.schemas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.llm.schemas import ArticleAnalysis, EvidenceComparisonResult


class LLMProvider(ABC):
    @abstractmethod
    def analyze_article(self, title: str, url: str, markdown: str) -> ArticleAnalysis:
        """Pass 1: extract claims + language/bias signals from the original article."""

    @abstractmethod
    def compare_evidence(
        self,
        original_title: str,
        original_url: str,
        claims: list[dict],
        related_articles: list[dict],
    ) -> EvidenceComparisonResult:
        """Pass 2: compare claims against independent coverage + summarize framing differences."""
