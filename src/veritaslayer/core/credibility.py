from __future__ import annotations

from urllib.parse import urlparse


def score_source_credibility(source_url: str) -> dict[str, float | str | None]:
    domain = urlparse(source_url).netloc.lower() if source_url else ""
    trusted = {"apnews.com", "reuters.com", "bbc.com", "nature.com", "wikipedia.org"}
    flagged = {"example-news-now.biz", "viral-shock-media.co"}

    if domain in trusted:
        score = 0.85
        label = "high credibility"
    elif domain in flagged:
        score = 0.2
        label = "low credibility"
    elif domain:
        score = 0.55
        label = "unknown credibility"
    else:
        score = 0.45
        label = "no source provided"

    return {
        "score": round(score, 4),
        "confidence": 0.75 if domain else 0.5,
        "domain": domain or None,
        "label": label,
    }
