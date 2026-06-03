from __future__ import annotations

import re
from urllib.parse import urlparse


def _normalize_domain(raw: str) -> str:
    """Strip port, leading 'www.' and lowercase so matching is robust.

    Examples
    --------
    www.reuters.com  -> reuters.com
    reuters.com:443  -> reuters.com
    en.wikipedia.org -> wikipedia.org   (only strips bare 'www.' prefix)
    """
    netloc = raw.lower()
    # Strip port
    netloc = re.sub(r":\d+$", "", netloc)
    # Strip leading www. only
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def score_source_credibility(source_url: str) -> dict[str, float | str | None]:
    raw_netloc = urlparse(source_url).netloc.lower() if source_url else ""
    domain = _normalize_domain(raw_netloc) if raw_netloc else ""

    trusted = {"apnews.com", "reuters.com", "bbc.com", "nature.com", "wikipedia.org"}
    flagged = {"example-news-now.biz", "viral-shock-media.co"}

    # Also match subdomains of trusted domains (e.g. en.wikipedia.org)
    def _matches_trusted(d: str) -> bool:
        return d in trusted or any(d.endswith("." + t) for t in trusted)

    def _matches_flagged(d: str) -> bool:
        return d in flagged or any(d.endswith("." + f) for f in flagged)

    if _matches_trusted(domain):
        score = 0.85
        label = "high credibility"
    elif _matches_flagged(domain):
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
