"""OpenAI implementation of LLMProvider, using Structured Outputs
(`responses.parse` with a Pydantic `text_format`) so the model's JSON always
matches our schema exactly. Get an API key at https://platform.openai.com/api-keys
"""

from __future__ import annotations

from openai import OpenAI

from app.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.prompts import (
    CLAIM_EXTRACTION_SYSTEM,
    EVIDENCE_COMPARISON_SYSTEM,
    build_claim_extraction_user_prompt,
    build_evidence_comparison_user_prompt,
)
from app.services.llm.schemas import ArticleAnalysis, EvidenceComparisonResult

settings = get_settings()


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Get one at https://platform.openai.com/api-keys")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def analyze_article(self, title: str, url: str, markdown: str) -> ArticleAnalysis:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM},
                {"role": "user", "content": build_claim_extraction_user_prompt(title, url, markdown)},
            ],
            text_format=ArticleAnalysis,
        )
        return response.output_parsed

    def compare_evidence(
        self,
        original_title: str,
        original_url: str,
        claims: list[dict],
        related_articles: list[dict],
    ) -> EvidenceComparisonResult:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": EVIDENCE_COMPARISON_SYSTEM},
                {
                    "role": "user",
                    "content": build_evidence_comparison_user_prompt(
                        original_title, original_url, claims, related_articles
                    ),
                },
            ],
            text_format=EvidenceComparisonResult,
        )
        return response.output_parsed
