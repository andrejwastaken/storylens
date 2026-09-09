"""Deterministic Trust Score engine.

This is plain, testable Python - the LLM never produces the final score.
The LLM only produces *signals* (headline-consistency score, sensationalism
score, per-claim verdicts + confidence). This module combines those signals
with source-reputation priors using a transparent, configurable weighted
formula.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from urllib.parse import urlparse

DEFAULT_WEIGHTS = {
    "source": 0.25,
    "corroboration": 0.30,
    "evidence": 0.25,
    "consistency": 0.10,
    "anti_sensationalism": 0.10,
}

VERDICT_VALUE = {
    "supported": 100.0,
    "partially_supported": 60.0,
    "unverified": 40.0,
    "contradicted": 0.0,
}


def get_domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())[:600]


def normalize_weights(weights: dict[str, float] | None) -> dict[str, float]:
    """Fill in defaults for missing keys and normalize so they sum to 1.0."""
    merged = {**DEFAULT_WEIGHTS, **(weights or {})}
    total = sum(merged.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {k: v / total for k, v in merged.items()}


def cluster_independent_sources(
    related_articles: list[dict], primary_domain: str
) -> list[list[dict]]:
    """Group related articles into clusters of the same underlying source.

    Two articles are considered the same underlying source if they share a
    domain, or if their text is near-duplicate (a strong signal of copied
    wire-service content). This prevents "5 sites copying the same AP wire
    story" from counting as 5 independent corroborations.
    """
    clusters: list[list[dict]] = []
    for art in related_articles:
        domain = art.get("domain") or get_domain(art["url"])
        if domain == primary_domain:
            continue
        text = _normalize(art.get("markdown") or art.get("snippet") or "")
        placed = False
        for cluster in clusters:
            rep = cluster[0]
            rep_domain = rep.get("domain") or get_domain(rep["url"])
            if rep_domain == domain:
                cluster.append(art)
                placed = True
                break
            rep_text = _normalize(rep.get("markdown") or rep.get("snippet") or "")
            if text and rep_text and SequenceMatcher(None, text, rep_text).ratio() > 0.82:
                cluster.append(art)
                placed = True
                break
        if not placed:
            clusters.append([art])
    return clusters


def score_corroboration(independent_count: int) -> float:
    """Map count of independent corroborating outlets -> 0-100 score.

    Diminishing returns: going from 0->1 matters a lot more than 4->5.
    """
    table = {0: 8.0, 1: 32.0, 2: 52.0, 3: 68.0, 4: 82.0, 5: 90.0}
    if independent_count in table:
        return table[independent_count]
    return 96.0 if independent_count > 5 else 8.0


def score_evidence(claims: list[dict], verdicts: list[dict], source_lookup) -> tuple[float, list[dict]]:
    """Importance- and confidence-weighted average of claim verdicts.

    source_lookup(domain) -> reliability_score (0-100), used so that a claim
    "supported" by Reuters counts for more than one "supported" by an
    unknown blog (primary/authoritative sources carry more evidence weight).
    """
    verdicts_by_claim = {v["claim_id"]: v for v in verdicts}
    total_weight = 0.0
    total_value = 0.0
    detail = []

    for claim in claims:
        v = verdicts_by_claim.get(claim["id"])
        if v is None:
            continue
        base_value = VERDICT_VALUE.get(v["verdict"], 40.0)

        citing_domains = [get_domain(u) for u in (v.get("supporting_urls") or []) if u]
        if citing_domains:
            avg_reliability = sum(source_lookup(d) for d in citing_domains) / len(citing_domains)
        else:
            avg_reliability = 50.0
        credibility_multiplier = 0.7 + 0.3 * (avg_reliability / 100.0)

        confidence = max(0.0, min(100.0, v.get("confidence", 50)))
        importance = max(0.0, min(100.0, claim.get("importance", 50)))

        value = base_value * credibility_multiplier
        weight = importance * (0.4 + 0.6 * confidence / 100.0)

        total_value += value * weight
        total_weight += weight
        detail.append({"claim_id": claim["id"], "value": round(value, 1), "weight": round(weight, 1)})

    evidence_score = (total_value / total_weight) if total_weight > 0 else 40.0
    return evidence_score, detail


@dataclass
class ScoringInput:
    source_reliability: float
    claims: list[dict]
    verdicts: list[dict]
    related_articles: list[dict]
    primary_domain: str
    headline_consistency_score: float
    sensationalism_score: float
    source_lookup: callable
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


@dataclass
class ScoringResult:
    trust_score: float
    source_score: float
    corroboration_score: float
    evidence_score: float
    consistency_score: float
    sensationalism_score: float  # raw, higher = more sensational (stored as-is)
    anti_sensationalism_score: float
    independent_source_count: int
    weights_used: dict[str, float]
    reasons: list[str]
    warnings: list[str]


def compute_trust_score(inp: ScoringInput) -> ScoringResult:
    weights = normalize_weights(inp.weights)

    clusters = cluster_independent_sources(inp.related_articles, inp.primary_domain)
    independent_count = len(clusters)

    source_score = max(0.0, min(100.0, inp.source_reliability))
    corroboration_score = score_corroboration(independent_count)
    evidence_score, _detail = score_evidence(inp.claims, inp.verdicts, inp.source_lookup)
    consistency_score = max(0.0, min(100.0, inp.headline_consistency_score))
    sensationalism_score = max(0.0, min(100.0, inp.sensationalism_score))
    anti_sensationalism_score = 100.0 - sensationalism_score

    trust_score = (
        weights["source"] * source_score
        + weights["corroboration"] * corroboration_score
        + weights["evidence"] * evidence_score
        + weights["consistency"] * consistency_score
        + weights["anti_sensationalism"] * anti_sensationalism_score
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if source_score >= 80:
        reasons.append("Published by a source with a strong editorial track record (signal, not certainty).")
    elif source_score < 50:
        warnings.append("This outlet has a lower track-record signal or is not in our known-source list.")

    if independent_count >= 3:
        reasons.append(f"Independently reported by {independent_count} other outlets (not just wire copies).")
    elif independent_count <= 1:
        warnings.append("Limited independent corroboration found - coverage may rely on very few outlets.")

    if evidence_score >= 80:
        reasons.append("Central claims are well-supported by independent evidence.")
    elif evidence_score < 50:
        warnings.append("Some important claims are weakly supported, contradicted, or unverified.")

    if consistency_score >= 80:
        reasons.append("Headline is consistent with the article body.")
    elif consistency_score < 60:
        warnings.append("Headline may overstate or understate what the article body actually says.")

    if anti_sensationalism_score >= 70:
        reasons.append("Language is measured rather than sensationalized.")
    elif sensationalism_score > 60:
        warnings.append("Article uses sensational or emotionally charged language.")

    verdicts_by_claim = {v["claim_id"]: v for v in inp.verdicts}
    for claim in inp.claims:
        v = verdicts_by_claim.get(claim["id"])
        if not v:
            continue
        if claim.get("importance", 0) >= 60 and v["verdict"] in ("unverified", "contradicted", "partially_supported"):
            label = {"unverified": "unverified", "contradicted": "contradicted", "partially_supported": "only partially supported"}[
                v["verdict"]
            ]
            warnings.append(f"Claim \"{claim['text']}\" is currently {label}.")

    return ScoringResult(
        trust_score=round(trust_score, 1),
        source_score=round(source_score, 1),
        corroboration_score=round(corroboration_score, 1),
        evidence_score=round(evidence_score, 1),
        consistency_score=round(consistency_score, 1),
        sensationalism_score=round(sensationalism_score, 1),
        anti_sensationalism_score=round(anti_sensationalism_score, 1),
        independent_source_count=independent_count,
        weights_used=weights,
        reasons=reasons,
        warnings=warnings,
    )
