"""Tests for report schema construction and validation."""
from __future__ import annotations

import json

import pytest

from veritaslayer.core.credibility import score_source_credibility
from veritaslayer.core.fingerprinting import ContentFingerprint
from veritaslayer.core.forensic import analyze_text_forensic
from veritaslayer.core.propagation import analyze_propagation
from veritaslayer.utils.report import (
    AuthenticityReport,
    AuthenticitySignal,
    build_report,
)


def _make_report(url: str = "") -> AuthenticityReport:
    text = "A perfectly ordinary sentence for testing."
    return build_report(
        source_url=url or None,
        fingerprint=ContentFingerprint.compute(text),
        forensic_signal=analyze_text_forensic(text),
        credibility_signal=score_source_credibility(url),
        propagation_signal=analyze_propagation(0, 1, 0),
    )


# ---------------------------------------------------------------------------
# Basic shape
# ---------------------------------------------------------------------------

def test_report_has_required_fields() -> None:
    report = _make_report()
    assert hasattr(report, "overall_synthetic_probability")
    assert hasattr(report, "signals")
    assert hasattr(report, "fingerprint")
    assert hasattr(report, "version")
    assert hasattr(report, "security_note")


def test_report_three_signals() -> None:
    report = _make_report()
    assert len(report.signals) == 3
    names = {s.name for s in report.signals}
    assert names == {"forensic", "credibility", "propagation"}


def test_overall_probability_in_range() -> None:
    report = _make_report()
    assert 0.0 <= report.overall_synthetic_probability <= 1.0


def test_all_signal_probabilities_in_range() -> None:
    report = _make_report()
    for sig in report.signals:
        assert 0.0 <= sig.probability_synthetic <= 1.0
        assert 0.0 <= sig.confidence <= 1.0


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def test_model_dump_json_is_valid_json() -> None:
    report = _make_report("https://reuters.com/article")
    raw = report.model_dump_json()
    parsed = json.loads(raw)
    assert "overall_synthetic_probability" in parsed
    assert "signals" in parsed


def test_model_dump_returns_dict() -> None:
    report = _make_report()
    d = report.model_dump()
    assert isinstance(d, dict)
    assert "signals" in d


# ---------------------------------------------------------------------------
# JSON schema stability (regression guard)
# ---------------------------------------------------------------------------

def test_json_schema_keys_stable() -> None:
    report = _make_report()
    d = report.model_dump()
    expected_top_level = {
        "overall_synthetic_probability",
        "signals",
        "fingerprint",
        "source_url",
        "timestamp",
        "version",
        "security_note",
    }
    assert expected_top_level.issubset(d.keys())


def test_signal_keys_stable() -> None:
    report = _make_report()
    for sig in report.signals:
        d = report.model_dump()["signals"][report.signals.index(sig)]
        expected_keys = {
            "name", "probability_synthetic", "explanation", "confidence", "details"
        }
        assert expected_keys.issubset(d.keys())


# ---------------------------------------------------------------------------
# Pydantic strict mode — extra fields rejected (Pydantic path only)
# ---------------------------------------------------------------------------

try:
    from pydantic import ValidationError

    def test_pydantic_rejects_extra_fields() -> None:
        with pytest.raises(ValidationError):
            AuthenticitySignal(
                name="test",
                probability_synthetic=0.5,
                explanation="ok",
                confidence=0.8,
                injected_field="evil",  # type: ignore[call-arg]
            )

except ImportError:
    pass  # Pydantic not installed — skip


# ---------------------------------------------------------------------------
# Dataclass fallback — manual range validation
# ---------------------------------------------------------------------------

try:
    from pydantic import BaseModel  # noqa: F401
    _has_pydantic = True
except ImportError:
    _has_pydantic = False

if not _has_pydantic:
    def test_dataclass_rejects_out_of_range_probability() -> None:
        with pytest.raises(ValueError):
            AuthenticitySignal(
                name="bad",
                probability_synthetic=1.5,  # out of range
                explanation="test",
                confidence=0.5,
            )
