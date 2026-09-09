from __future__ import annotations

import datetime as dt
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import get_settings
from app.database import get_db
from app.scoring import ScoringInput, compute_trust_score, get_domain
from app.seed_sources import lookup as lookup_source
from app.services.exa_client import ExaError, search_related_coverage
from app.services.firecrawl_client import FirecrawlError, scrape_article
from app.services.llm import get_llm_provider

logger = logging.getLogger("storylens.analyze")
settings = get_settings()
router = APIRouter()


def _parse_published_at(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _fetch_related_articles(primary_domain: str, search_queries: list[str]) -> list[dict]:
    """Exa search for independent coverage, then Firecrawl-scrape the top results."""
    seen_urls: set[str] = set()
    seen_domains: set[str] = set()
    candidates: list[dict] = []

    for query in search_queries:
        try:
            results = search_related_coverage(query, num_results=8, exclude_domain=primary_domain)
        except ExaError as exc:
            logger.warning("Exa search failed for %r: %s", query, exc)
            continue
        for r in results:
            if not r.get("url") or r["url"] in seen_urls:
                continue
            domain = get_domain(r["url"])
            if domain == primary_domain:
                continue
            seen_urls.add(r["url"])
            candidates.append({**r, "domain": domain})
        if len(candidates) >= settings.max_related_sources * 3:
            break

    # Prefer one article per domain first (maximize independent breadth), then fill remaining slots.
    ordered: list[dict] = []
    for c in candidates:
        if c["domain"] not in seen_domains:
            seen_domains.add(c["domain"])
            ordered.append(c)
    for c in candidates:
        if c not in ordered:
            ordered.append(c)
    top = ordered[: settings.max_related_sources]

    related_articles: list[dict] = []

    def _scrape(candidate: dict) -> dict | None:
        try:
            scraped = scrape_article(candidate["url"])
            return {**candidate, **scraped, "domain": candidate["domain"]}
        except FirecrawlError as exc:
            logger.warning("Firecrawl failed for %s: %s", candidate["url"], exc)
            return {**candidate, "markdown": candidate.get("snippet", ""), "title": candidate.get("title", "")}

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(_scrape, c) for c in top]
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                related_articles.append(result)

    return related_articles


@router.post("/analyze", response_model=schemas.StoryProfileResponse)
def analyze(req: schemas.AnalyzeRequest, db: Session = Depends(get_db)) -> schemas.StoryProfileResponse:
    llm = get_llm_provider()

    # 1. Extract the primary article.
    try:
        primary = scrape_article(req.url)
    except FirecrawlError as exc:
        raise HTTPException(status_code=502, detail=f"Could not extract article: {exc}") from exc

    if not primary.get("markdown"):
        raise HTTPException(status_code=422, detail="Extracted article had no readable text.")

    primary_domain = get_domain(primary["url"])
    source = crud.get_or_create_source(db, primary_domain)

    article = models.Article(
        url=primary["url"],
        title=primary["title"] or req.url,
        source_id=source.id,
        author=primary.get("author"),
        published_at=_parse_published_at(primary.get("published_at")),
        content=primary["markdown"],
        content_hash=crud.content_hash(primary["markdown"]),
        is_primary=True,
    )
    db.add(article)
    db.flush()

    # 2. LLM pass 1: claims + language signals.
    analysis = llm.analyze_article(article.title, article.url, primary["markdown"])

    story = models.Story(canonical_title=analysis.summary[:200] or article.title)
    db.add(story)
    db.flush()
    db.add(models.StoryArticle(story_id=story.id, article_id=article.id, similarity=1.0))

    claim_rows = []
    for c in analysis.claims:
        row = models.Claim(story_id=story.id, text=c.text, importance=c.importance)
        db.add(row)
        claim_rows.append((c, row))
    db.flush()

    # 3. Exa search + Firecrawl extraction of independent coverage.
    search_queries = [c.search_query for c, _ in claim_rows[:3]] or [article.title]
    related_articles = _fetch_related_articles(primary_domain, search_queries)

    related_models = []
    for ra in related_articles:
        rsource = crud.get_or_create_source(db, ra["domain"])
        ra_article = models.Article(
            url=ra["url"],
            title=ra.get("title") or "",
            source_id=rsource.id,
            author=ra.get("author"),
            published_at=_parse_published_at(ra.get("published_at")),
            content=ra.get("markdown", ""),
            content_hash=crud.content_hash(ra.get("markdown") or ra.get("snippet") or ra["url"]),
            is_primary=False,
        )
        db.add(ra_article)
        db.flush()
        db.add(models.StoryArticle(story_id=story.id, article_id=ra_article.id, similarity=0.0))
        related_models.append((ra, ra_article, rsource))

    # 4. LLM pass 2: compare claims against independent coverage + framing.
    claims_payload = [{"id": c.id, "text": c.text, "importance": c.importance} for c, _ in claim_rows]
    articles_payload = [
        {
            "url": ra["url"],
            "title": ra.get("title", ""),
            "site_name": rsource.name,
            "domain": ra["domain"],
            "markdown": ra.get("markdown", ""),
            "snippet": ra.get("snippet", ""),
        }
        for ra, _am, rsource in related_models
    ]

    if claims_payload and articles_payload:
        comparison = llm.compare_evidence(article.title, article.url, claims_payload, articles_payload)
    else:
        comparison = type("Empty", (), {"verdicts": [], "framing": []})()

    verdicts_by_claim = {v.claim_id: v for v in comparison.verdicts}
    url_to_article_id = {am.url: am.id for _ra, am, _s in related_models}

    for c, row in claim_rows:
        v = verdicts_by_claim.get(c.id)
        if not v:
            continue
        for url in v.supporting_urls:
            if url in url_to_article_id:
                db.add(
                    models.Evidence(
                        claim_id=row.id,
                        article_id=url_to_article_id[url],
                        relationship_type="supported",
                        confidence=v.confidence,
                        explanation=v.explanation,
                    )
                )
        for url in v.contradicting_urls:
            if url in url_to_article_id:
                db.add(
                    models.Evidence(
                        claim_id=row.id,
                        article_id=url_to_article_id[url],
                        relationship_type="contradicted",
                        confidence=v.confidence,
                        explanation=v.explanation,
                    )
                )

    # 5. Deterministic scoring.
    def source_lookup(domain: str) -> float:
        return lookup_source(domain)["reliability_score"]

    scoring_result = compute_trust_score(
        ScoringInput(
            source_reliability=source.reliability_score,
            claims=claims_payload,
            verdicts=[v.model_dump() for v in comparison.verdicts],
            related_articles=[{"url": ra["url"], "domain": ra["domain"], "markdown": ra.get("markdown", "")} for ra, _a, _s in related_models],
            primary_domain=primary_domain,
            headline_consistency_score=analysis.headline_consistency.score,
            sensationalism_score=analysis.sensationalism.score,
            source_lookup=source_lookup,
            weights=req.weights or {},
        )
    )

    framing_payload = [f.model_dump() for f in comparison.framing]
    for f in framing_payload:
        f["domain"] = get_domain(f["url"])

    db_analysis = models.Analysis(
        article_id=article.id,
        trust_score=scoring_result.trust_score,
        source_score=scoring_result.source_score,
        corroboration_score=scoring_result.corroboration_score,
        evidence_score=scoring_result.evidence_score,
        consistency_score=scoring_result.consistency_score,
        sensationalism_score=scoring_result.sensationalism_score,
        bias_label=analysis.bias.label,
        bias_confidence=analysis.bias.confidence,
        ai_probability=None,
        weights_json=scoring_result.weights_used,
        summary=analysis.summary,
        warnings_json=scoring_result.warnings,
        reasons_json=scoring_result.reasons,
        framing_json=framing_payload,
    )
    db.add(db_analysis)
    db.commit()

    claims_out = []
    for c, row in claim_rows:
        v = verdicts_by_claim.get(c.id)
        claims_out.append(
            schemas.ClaimOut(
                id=c.id,
                text=c.text,
                importance=c.importance,
                verdict=v.verdict if v else "unverified",
                confidence=v.confidence if v else 0,
                supporting_urls=v.supporting_urls if v else [],
                contradicting_urls=v.contradicting_urls if v else [],
                explanation=v.explanation if v else "No independent coverage was found for this claim.",
            )
        )

    related_sources_out = [
        schemas.RelatedSourceOut(
            url=ra["url"],
            title=ra.get("title") or "",
            domain=ra["domain"],
            outlet_name=rsource.name,
            reliability_score=rsource.reliability_score,
        )
        for ra, _am, rsource in related_models
    ]

    framing_out = [
        schemas.OutletFramingOut(url=f["url"], outlet_name=f["outlet_name"], domain=f["domain"], framing_summary=f["framing_summary"], tone=f["tone"])
        for f in framing_payload
    ]

    return schemas.StoryProfileResponse(
        analysis_id=db_analysis.id,
        article=schemas.ArticleInfo(
            url=article.url,
            title=article.title,
            author=article.author,
            published_at=primary.get("published_at"),
            domain=primary_domain,
            source_name=source.name,
        ),
        summary=analysis.summary,
        trust_score=scoring_result.trust_score,
        scores=schemas.ScoreBreakdown(
            source=scoring_result.source_score,
            corroboration=scoring_result.corroboration_score,
            evidence=scoring_result.evidence_score,
            consistency=scoring_result.consistency_score,
            sensationalism=scoring_result.sensationalism_score,
            anti_sensationalism=scoring_result.anti_sensationalism_score,
        ),
        weights_used=scoring_result.weights_used,
        bias=schemas.BiasOut(
            label=analysis.bias.label,
            confidence=analysis.bias.confidence,
            explanation=analysis.bias.explanation,
        ),
        reasons=scoring_result.reasons,
        warnings=scoring_result.warnings,
        claims=claims_out,
        related_sources=related_sources_out,
        framing=framing_out,
        independent_source_count=scoring_result.independent_source_count,
    )
