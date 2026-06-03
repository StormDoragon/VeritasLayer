"""Tests for ContentFingerprint and convenience wrapper."""
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from veritaslayer.core.fingerprinting import ContentFingerprint, fingerprint_text_sha256

# ---------------------------------------------------------------------------
# Existing test (preserved)
# ---------------------------------------------------------------------------

def test_fingerprint_text_sha256_is_stable() -> None:
    text = "veritas"
    assert fingerprint_text_sha256(text) == fingerprint_text_sha256(text)


# ---------------------------------------------------------------------------
# ContentFingerprint.compute — text input
# ---------------------------------------------------------------------------

def test_compute_text_returns_sha256() -> None:
    result = ContentFingerprint.compute("hello world")
    assert "sha256" in result["hashes"]
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert result["hashes"]["sha256"] == expected


def test_compute_text_returns_sha3_256() -> None:
    result = ContentFingerprint.compute("hello world")
    assert "sha3_256" in result["hashes"]


def test_compute_text_type_field() -> None:
    result = ContentFingerprint.compute("any text")
    assert result["type"] == "text"


def test_compute_bytes_input() -> None:
    result = ContentFingerprint.compute(b"\x00\x01\x02")
    assert result["type"] == "bytes"
    assert result["hashes"]["sha256"] == hashlib.sha256(b"\x00\x01\x02").hexdigest()


# ---------------------------------------------------------------------------
# ContentFingerprint.compute — file input
# ---------------------------------------------------------------------------

def test_compute_file_path() -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"file content")
        tmp_path = Path(f.name)

    try:
        result = ContentFingerprint.compute(tmp_path)
        assert result["type"] == "file"
        assert result["hashes"]["sha256"] == hashlib.sha256(b"file content").hexdigest()
    finally:
        tmp_path.unlink(missing_ok=True)


def test_compute_missing_file_records_warning() -> None:
    result = ContentFingerprint.compute(Path("/nonexistent/file.txt"))
    assert result.get("error") is True
    assert any(
        "does not exist" in w or "Fingerprint error" in w
        for w in result["warnings"]
    )


# ---------------------------------------------------------------------------
# Empty / adversarial input
# ---------------------------------------------------------------------------

def test_compute_empty_string() -> None:
    result = ContentFingerprint.compute("")
    assert result["type"] == "text"
    assert "sha256" in result["hashes"]


def test_compute_source_url_stored() -> None:
    result = ContentFingerprint.compute("text", source_url="https://example.com")
    assert result["source_url"] == "https://example.com"
