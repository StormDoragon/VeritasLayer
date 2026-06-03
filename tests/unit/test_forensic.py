"""Tests for the baseline heuristic forensic analyser."""
from __future__ import annotations

from veritaslayer.core.forensic import analyze_text_forensic

# ---------------------------------------------------------------------------
# Existing test (preserved)
# ---------------------------------------------------------------------------

def test_forensic_signal_shape() -> None:
    signal = analyze_text_forensic("Simple factual sentence.")
    assert 0.0 <= float(signal["score"]) <= 1.0
    assert 0.0 <= float(signal["confidence"]) <= 1.0


# ---------------------------------------------------------------------------
# Heuristic behaviour
# ---------------------------------------------------------------------------

def test_synthetic_markers_lower_score() -> None:
    clean = analyze_text_forensic("The report confirmed the findings.")
    marked = analyze_text_forensic(
        "As an AI, in conclusion, it is important to note this."
    )
    assert float(clean["score"]) > float(marked["score"])


def test_punctuation_spikes_lower_score() -> None:
    clean = analyze_text_forensic("This is a calm sentence.")
    spiked = analyze_text_forensic("Wow!!! Can you believe it??? This is huge...")
    assert float(clean["score"]) > float(spiked["score"])


def test_confidence_capped_at_072() -> None:
    # Feed a very long text — confidence should never exceed 0.72
    long_text = " ".join(["word"] * 1000)
    signal = analyze_text_forensic(long_text)
    assert float(signal["confidence"]) <= 0.72


def test_analyser_field_present() -> None:
    signal = analyze_text_forensic("Some text.")
    assert signal.get("analyser") == "baseline_heuristic_v0"


# ---------------------------------------------------------------------------
# Adversarial / edge cases
# ---------------------------------------------------------------------------

def test_empty_string() -> None:
    # Should not raise — token_count clamps to 1
    signal = analyze_text_forensic("")
    assert 0.0 <= float(signal["score"]) <= 1.0


def test_only_punctuation() -> None:
    signal = analyze_text_forensic("!!! ??? ...")
    assert 0.0 <= float(signal["score"]) <= 1.0


def test_very_short_text_low_confidence() -> None:
    signal = analyze_text_forensic("Hi.")
    assert float(signal["confidence"]) < 0.72
