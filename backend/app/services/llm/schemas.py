"""Pydantic schemas for structured LLM output.

These are used both as the OpenAI Structured Outputs schema (via
`client.responses.parse(text_format=...)`) and as the in-process data
contract between the LLM layer and the rest of the app.

IMPORTANT: the LLM only ever produces *signals* (sub-scores, verdicts,
labels). The final Trust Score is always computed by
`app.scoring` in plain Python - never by the model.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedClaim(BaseModel):
    id: str = Field(description="Short stable id like 'c1', 'c2'.")
    text: str = Field(description="The factual claim, as a single clear sentence.")
    importance: int = Field(description="How central this claim is to the story, 0-100.")
    search_query: str = Field(description="A good web-search query to find independent coverage of this claim.")


class HeadlineConsistency(BaseModel):
    score: int = Field(description="0-100. 100 = headline fully and accurately represents the body.")
    explanation: str


class Sensationalism(BaseModel):
    score: int = Field(description="0-100. 100 = extremely sensational/emotionally manipulative language.")
    explanation: str


class BiasAssessment(BaseModel):
    label: str = Field(description="One of: left, center-left, center, center-right, right, unclear")
    confidence: int = Field(description="0-100 confidence in this label. Low confidence is fine and expected.")
    explanation: str


class ArticleAnalysis(BaseModel):
    """Output of pass 1: read the original article only."""

    summary: str = Field(description="A concise, neutral 2-4 sentence summary of the article.")
    claims: list[ExtractedClaim] = Field(description="3-6 important, independently checkable factual claims.")
    headline_consistency: HeadlineConsistency
    sensationalism: Sensationalism
    bias: BiasAssessment


class ClaimVerdict(BaseModel):
    claim_id: str = Field(description="Must match an id from the claims list, e.g. 'c1'.")
    verdict: str = Field(description="One of: supported, contradicted, partially_supported, unverified")
    confidence: int = Field(description="0-100 confidence in this verdict based on the evidence available.")
    supporting_urls: list[str] = Field(description="URLs (from the provided related articles) that support the claim.")
    contradicting_urls: list[str] = Field(description="URLs (from the provided related articles) that contradict the claim.")
    explanation: str = Field(description="1-2 sentences on why this verdict was reached.")


class RelatedArticleFraming(BaseModel):
    url: str = Field(description="Must match a URL from the provided related articles.")
    outlet_name: str
    framing_summary: str = Field(description="1-2 sentences on how this outlet frames/angles the story differently.")
    tone: str = Field(description="One or two words, e.g. neutral, critical, sympathetic, alarmist, supportive.")


class EvidenceComparisonResult(BaseModel):
    """Output of pass 2: compare the original article's claims against related coverage."""

    verdicts: list[ClaimVerdict]
    framing: list[RelatedArticleFraming]
