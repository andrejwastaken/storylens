"""Firecrawl integration: turns a URL into clean article text + metadata.

Docs: https://docs.firecrawl.dev
Get a free API key at https://www.firecrawl.dev/app (1,000 free credits/month).
Without a key, Firecrawl's "Keyless" tier still works but is rate-limited -
fine for local demo/dev, but add a key before a live demo to avoid surprises.
"""

from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


class FirecrawlError(RuntimeError):
    pass


def _first(value) -> str | None:
    """Firecrawl metadata fields can be a string or a list of strings."""
    if value is None:
        return None
    if isinstance(value, list):
        return value[0] if value else None
    return str(value)


def scrape_article(url: str) -> dict:
    """Scrape a single URL and return normalized article fields.

    Returns: {url, title, author, published_at, markdown, site_name}
    Raises FirecrawlError on failure.
    """
    headers = {"Content-Type": "application/json"}
    if settings.firecrawl_api_key:
        headers["Authorization"] = f"Bearer {settings.firecrawl_api_key}"

    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
    }

    try:
        resp = httpx.post(
            f"{settings.firecrawl_base_url}/v2/scrape",
            headers=headers,
            json=payload,
            timeout=45.0,
        )
    except httpx.HTTPError as exc:
        raise FirecrawlError(f"Firecrawl request failed for {url}: {exc}") from exc

    if resp.status_code >= 400:
        raise FirecrawlError(f"Firecrawl returned {resp.status_code} for {url}: {resp.text[:300]}")

    body = resp.json()
    data = body.get("data", body)
    metadata = data.get("metadata", {}) or {}

    title = _first(metadata.get("title")) or ""
    author = _first(metadata.get("author")) or _first(metadata.get("article:author"))
    published_at = (
        _first(metadata.get("publishedTime"))
        or _first(metadata.get("article:published_time"))
        or _first(metadata.get("date"))
    )
    site_name = _first(metadata.get("og:site_name")) or _first(metadata.get("ogSiteName"))
    image_url = _first(metadata.get("og:image")) or _first(metadata.get("ogImage"))

    return {
        "url": _first(metadata.get("sourceURL")) or url,
        "title": title,
        "author": author,
        "published_at": published_at,
        "markdown": data.get("markdown") or "",
        "site_name": site_name,
        "image_url": image_url,
    }
