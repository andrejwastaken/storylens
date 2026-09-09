"""SQLAlchemy ORM models. Tables are created via Base.metadata.create_all (no migrations)."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # 0-100 signal, not objective truth. See app/seed_sources.py for seed values.
    reliability_score: Mapped[float] = mapped_column(Float, default=50.0)
    # -1.0 (left) .. 0 (center) .. 1.0 (right) signal, not objective truth.
    bias_score: Mapped[float] = mapped_column(Float, default=0.0)

    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))
    title: Mapped[str] = mapped_column(String(1024), default="")
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    content_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    # True for the article the user originally submitted; False for related/corroborating articles.
    is_primary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    source: Mapped[Source | None] = relationship(back_populates="articles")


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_title: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    claims: Mapped[list["Claim"]] = relationship(back_populates="story")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    text: Mapped[str] = mapped_column(Text)
    # 0-100, how central this claim is to the story.
    importance: Mapped[float] = mapped_column(Float, default=50.0)
    # Overall verdict summary (denormalized from Evidence rows, for cheap
    # reconstruction/caching of a Story Profile without re-running the LLM).
    # One of: supported | contradicted | partially_supported | unverified
    verdict: Mapped[str] = mapped_column(String(32), default="unverified")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, default="")

    story: Mapped[Story] = relationship(back_populates="claims")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="claim")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"))
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    # One of: supported | contradicted | partially_supported | unverified
    relationship_type: Mapped[str] = mapped_column(String(32), default="unverified")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, default="")

    claim: Mapped[Claim] = relationship(back_populates="evidence")
    article: Mapped[Article] = relationship()


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))

    trust_score: Mapped[float] = mapped_column(Float)
    source_score: Mapped[float] = mapped_column(Float)
    corroboration_score: Mapped[float] = mapped_column(Float)
    evidence_score: Mapped[float] = mapped_column(Float)
    consistency_score: Mapped[float] = mapped_column(Float)
    sensationalism_score: Mapped[float] = mapped_column(Float)  # higher = MORE sensational

    bias_label: Mapped[str] = mapped_column(String(32), default="unknown")
    bias_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    bias_explanation: Mapped[str] = mapped_column(Text, default="")
    # Optional signal (soft heuristic) (0-100), null when unavailable/not configured.
    ai_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    ai_image_reasoning: Mapped[str] = mapped_column(Text, default="")

    weights_json: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, default="")
    warnings_json: Mapped[list] = mapped_column(JSON, default=list)
    reasons_json: Mapped[list] = mapped_column(JSON, default=list)
    framing_json: Mapped[list] = mapped_column(JSON, default=list)
    independent_source_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    article: Mapped[Article] = relationship()


class StoryArticle(Base):
    __tablename__ = "story_articles"

    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
