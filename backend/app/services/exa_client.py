"""Exa integration: finds independent coverage of a story/claim across the web.

Docs: https://docs.exa.ai
Get a free API key at https://dashboard.exa.ai/api-keys (new accounts get $20
free credit, plus $10/month on the free tier - no card required).
"""

from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


class ExaError(RuntimeError):
    pass


def search_related_coverage(
    query: str,
    num_results: int = 8,
    exclude_domain: str | None = None,
) -> list[dict]:
    """Search the web for independent coverage of a story/claim.

    Returns a list of {url, title, published_at, author, snippet} dicts,
    ranked by Exa's relevance, most recent 60 days of news preferred.
    """
    if not settings.exa_api_key:
        raise ExaError("EXA_API_KEY is not set. Get one at https://dashboard.exa.ai/api-keys")

    headers = {"x-api-key": settings.exa_api_key, "Content-Type": "application/json"}
    payload: dict = {
        "query": query,
        "numResults": num_results,
        "type": "auto",
        "category": "news",
        "contents": {"text": {"maxCharacters": 2000}},
    }
    if exclude_domain:
        payload["excludeDomains"] = [exclude_domain]

    try:
        resp = httpx.post(f"{settings.exa_base_url}/search", headers=headers, json=payload, timeout=30.0)
    except httpx.HTTPError as exc:
        raise ExaError(f"Exa request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise ExaError(f"Exa returned {resp.status_code}: {resp.text[:300]}")

    body = resp.json()
    results = []
    for item in body.get("results", []):
        results.append(
            {
                "url": item.get("url"),
                "title": item.get("title") or "",
                "published_at": item.get("publishedDate"),
                "author": item.get("author"),
                "snippet": (item.get("text") or "")[:1000],
            }
        )
    return results
