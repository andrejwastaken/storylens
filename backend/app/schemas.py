"""API request/response models (FastAPI-facing). Distinct from the LLM's
internal structured-output schemas in app/services/llm/schemas.py.
"""

from __future__ import annotations

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    url: str
    weights: dict[str, float] | None = None


class ArticleInfo(BaseModel):
    url: str
    title: str
    author: str | None
    published_at: str | None
    domain: str
    source_name: str


class ScoreBreakdown(BaseModel):
    source: float
    corroboration: float
    evidence: float
    consistency: float
    sensationalism: float
    anti_sensationalism: float


class BiasOut(BaseModel):
    label: str
    confidence: float
    explanation: str


class ClaimOut(BaseModel):
    id: str
    text: str
    importance: float
    verdict: str
    confidence: float
    supporting_urls: list[str]
    contradicting_urls: list[str]
    explanation: str


class RelatedSourceOut(BaseModel):
    url: str
    title: str
    domain: str
    outlet_name: str
    reliability_score: float


class OutletFramingOut(BaseModel):
    url: str
    outlet_name: str
    domain: str
    framing_summary: str
    tone: str


class AiImageSignalOut(BaseModel):
    """P2: soft, heuristic AI-generated-image likelihood for the article's
    lead image. Not a forensic verdict - see app/services/fal_client.py."""

    image_url: str
    likelihood: float
    reasoning: str


class StoryProfileResponse(BaseModel):
    analysis_id: int
    article: ArticleInfo
    summary: str
    trust_score: float
    scores: ScoreBreakdown
    weights_used: dict[str, float]
    bias: BiasOut
    reasons: list[str]
    warnings: list[str]
    claims: list[ClaimOut]
    related_sources: list[RelatedSourceOut]
    framing: list[OutletFramingOut]
    independent_source_count: int
    cached: bool = False
    ai_image_signal: AiImageSignalOut | None = None
    audio_summary_available: bool = False
