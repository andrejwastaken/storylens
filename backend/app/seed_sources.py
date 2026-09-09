"""Small curated table of known outlet reputations, used as a *prior signal only*.

This is intentionally NOT a comprehensive source-rating database (out of scope for this
project). Unknown domains fall back to a neutral default. These numbers are directional
signals, not objective truth about any outlet.

reliability_score: 0-100, rough editorial/fact-checking track record proxy.
bias_score: -1.0 (left-leaning) .. 0.0 (center) .. 1.0 (right-leaning).
"""

from __future__ import annotations

KNOWN_SOURCES: dict[str, dict] = {
    "reuters.com": {"name": "Reuters", "reliability_score": 96, "bias_score": 0.0},
    "apnews.com": {"name": "Associated Press", "reliability_score": 95, "bias_score": 0.0},
    "bbc.com": {"name": "BBC News", "reliability_score": 92, "bias_score": -0.05},
    "bbc.co.uk": {"name": "BBC News", "reliability_score": 92, "bias_score": -0.05},
    "npr.org": {"name": "NPR", "reliability_score": 88, "bias_score": -0.15},
    "theguardian.com": {"name": "The Guardian", "reliability_score": 82, "bias_score": -0.35},
    "nytimes.com": {"name": "The New York Times", "reliability_score": 86, "bias_score": -0.25},
    "washingtonpost.com": {"name": "The Washington Post", "reliability_score": 84, "bias_score": -0.25},
    "wsj.com": {"name": "The Wall Street Journal", "reliability_score": 87, "bias_score": 0.15},
    "bloomberg.com": {"name": "Bloomberg", "reliability_score": 88, "bias_score": 0.05},
    "economist.com": {"name": "The Economist", "reliability_score": 87, "bias_score": 0.0},
    "aljazeera.com": {"name": "Al Jazeera", "reliability_score": 78, "bias_score": -0.2},
    "cnn.com": {"name": "CNN", "reliability_score": 74, "bias_score": -0.4},
    "foxnews.com": {"name": "Fox News", "reliability_score": 68, "bias_score": 0.55},
    "nbcnews.com": {"name": "NBC News", "reliability_score": 78, "bias_score": -0.25},
    "abcnews.go.com": {"name": "ABC News", "reliability_score": 79, "bias_score": -0.2},
    "cbsnews.com": {"name": "CBS News", "reliability_score": 79, "bias_score": -0.2},
    "politico.com": {"name": "Politico", "reliability_score": 80, "bias_score": -0.1},
    "axios.com": {"name": "Axios", "reliability_score": 82, "bias_score": -0.05},
    "thehill.com": {"name": "The Hill", "reliability_score": 76, "bias_score": 0.05},
    "usatoday.com": {"name": "USA Today", "reliability_score": 78, "bias_score": -0.1},
    "time.com": {"name": "TIME", "reliability_score": 78, "bias_score": -0.15},
    "forbes.com": {"name": "Forbes", "reliability_score": 72, "bias_score": 0.1},
    "techcrunch.com": {"name": "TechCrunch", "reliability_score": 75, "bias_score": 0.0},
    "theverge.com": {"name": "The Verge", "reliability_score": 78, "bias_score": -0.1},
    "arstechnica.com": {"name": "Ars Technica", "reliability_score": 84, "bias_score": -0.05},
    "wired.com": {"name": "Wired", "reliability_score": 79, "bias_score": -0.1},
    "reason.com": {"name": "Reason", "reliability_score": 70, "bias_score": 0.35},
    "breitbart.com": {"name": "Breitbart", "reliability_score": 45, "bias_score": 0.75},
    "dailymail.co.uk": {"name": "Daily Mail", "reliability_score": 48, "bias_score": 0.35},
    "nypost.com": {"name": "New York Post", "reliability_score": 60, "bias_score": 0.4},
    "buzzfeednews.com": {"name": "BuzzFeed News", "reliability_score": 65, "bias_score": -0.3},
    "huffpost.com": {"name": "HuffPost", "reliability_score": 65, "bias_score": -0.45},
    "skynews.com": {"name": "Sky News", "reliability_score": 82, "bias_score": 0.1},
    "france24.com": {"name": "France 24", "reliability_score": 82, "bias_score": -0.05},
    "dw.com": {"name": "Deutsche Welle", "reliability_score": 84, "bias_score": -0.05},
    "propublica.org": {"name": "ProPublica", "reliability_score": 90, "bias_score": -0.1},
    "vox.com": {"name": "Vox", "reliability_score": 70, "bias_score": -0.45},
    "slate.com": {"name": "Slate", "reliability_score": 68, "bias_score": -0.4},
    "nationalreview.com": {"name": "National Review", "reliability_score": 70, "bias_score": 0.55},
    "motherjones.com": {"name": "Mother Jones", "reliability_score": 68, "bias_score": -0.55},
}

DEFAULT_RELIABILITY = 50.0
DEFAULT_BIAS = 0.0


def lookup(domain: str) -> dict:
    domain = domain.lower().lstrip("www.")
    if domain in KNOWN_SOURCES:
        return KNOWN_SOURCES[domain]
    # try stripping a leading "www."
    if domain.startswith("www."):
        stripped = domain[4:]
        if stripped in KNOWN_SOURCES:
            return KNOWN_SOURCES[stripped]
    return {"name": domain, "reliability_score": DEFAULT_RELIABILITY, "bias_score": DEFAULT_BIAS}
