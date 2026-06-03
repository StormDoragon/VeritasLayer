"""Tests for propagation analysis including the insufficient-data path."""
from __future__ import annotations

import pytest

from veritaslayer.core.propagation import analyze_propagation

# ---------------------------------------------------------------------------
# Insufficient data (all defaults)
# ---------------------------------------------------------------------------

def test_all_defaults_returns_insufficient_data() -> None:
    signal = analyze_propagation(
        repost_count=0, source_count=1, time_to_viral_minutes=0
    )
    assert signal["label"] == "insufficient data"
    assert float(signal["confidence"]) == pytest.approx(0.3)
    assert float(signal["score"]) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Healthy propagation
# ---------------------------------------------------------------------------

def test_many_sources_no_repost_pressure_is_healthy() -> None:
    signal = analyze_propagation(
        repost_count=10, source_count=8, time_to_viral_minutes=0
    )
    assert signal["label"] == "healthy"
    assert float(signal["score"]) >= 0.6


# ---------------------------------------------------------------------------
# Anomalous propagation
# ---------------------------------------------------------------------------

def test_high_repost_pressure_is_anomalous() -> None:
    signal = analyze_propagation(
        repost_count=1200, source_count=1, time_to_viral_minutes=0
    )
    assert signal["label"] == "anomalous"


def test_viral_velocity_penalty_applied() -> None:
    # Very fast viral spread from single source should score low
    signal = analyze_propagation(
        repost_count=50, source_count=1, time_to_viral_minutes=10
    )
    assert signal["label"] == "anomalous"


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------

def test_output_bounds() -> None:
    for repost, source, viral in [(0, 2, 0), (500, 4, 30), (1200, 8, 60)]:
        signal = analyze_propagation(repost, source, viral)
        assert 0.0 <= float(signal["score"]) <= 1.0
        assert 0.0 <= float(signal["confidence"]) <= 1.0
        assert isinstance(signal["label"], str)
