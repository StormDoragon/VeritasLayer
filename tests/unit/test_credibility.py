"""Tests for source credibility scoring and domain normalisation."""
from __future__ import annotations

import pytest

from veritaslayer.core.credibility import _normalize_domain, score_source_credibility

# ---------------------------------------------------------------------------
# Existing test (preserved)
# ---------------------------------------------------------------------------

def test_credibility_for_trusted_domain() -> None:
    signal = score_source_credibility("https://reuters.com/example")
    assert float(signal["score"]) >= 0.8


# ---------------------------------------------------------------------------
# Domain normalisation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("reuters.com", "reuters.com"),
    ("www.reuters.com", "reuters.com"),
    ("Reuters.COM", "reuters.com"),
    ("reuters.com:443", "reuters.com"),
    ("www.reuters.com:443", "reuters.com"),
    ("en.wikipedia.org", "en.wikipedia.org"),   # subdomain — not stripped, but matched
])
def test_normalize_domain(raw: str, expected: str) -> None:
    assert _normalize_domain(raw) == expected


# ---------------------------------------------------------------------------
# www-prefixed and subdomain variants resolve correctly
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "https://www.reuters.com/world",
    "https://reuters.com:443/world",
    "https://en.wikipedia.org/wiki/Python",
    "https://www.bbc.com/news",
])
def test_trusted_domain_variants(url: str) -> None:
    signal = score_source_credibility(url)
    assert signal["label"] == "high credibility", f"Failed for {url}: {signal}"
    assert float(signal["score"]) == pytest.approx(0.85)


def test_flagged_domain() -> None:
    signal = score_source_credibility("https://viral-shock-media.co/story")
    assert signal["label"] == "low credibility"
    assert float(signal["score"]) == pytest.approx(0.2)


def test_unknown_domain() -> None:
    signal = score_source_credibility("https://some-random-blog.io/post")
    assert signal["label"] == "unknown credibility"
    assert float(signal["score"]) == pytest.approx(0.55)


def test_empty_url() -> None:
    signal = score_source_credibility("")
    assert signal["label"] == "no source provided"
    assert signal["domain"] is None
    assert float(signal["confidence"]) == pytest.approx(0.5)
