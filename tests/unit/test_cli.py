"""Tests for the CLI entry point."""
from __future__ import annotations

import json
import subprocess
import sys


def _run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed interpreter/module invocation in tests
        [sys.executable, "-m", "veritaslayer.cli.main", *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Basic JSON output
# ---------------------------------------------------------------------------

def test_cli_text_arg_produces_json() -> None:
    result = _run(["Simple test sentence.", "--json"])
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert "overall_synthetic_probability" in parsed


def test_cli_stdin_produces_json() -> None:
    result = _run(["--json"], stdin="Text from stdin.")
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert "signals" in parsed


def test_cli_with_source_url() -> None:
    result = _run(["Test.", "--source-url", "https://reuters.com/article", "--json"])
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["source_url"] == "https://reuters.com/article"


# ---------------------------------------------------------------------------
# Propagation flags
# ---------------------------------------------------------------------------

def test_cli_propagation_flags_accepted() -> None:
    result = _run([
        "Some news text.",
        "--repost-count", "100",
        "--source-count", "5",
        "--time-to-viral-minutes", "60",
        "--json",
    ])
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    prop_signal = next(s for s in parsed["signals"] if s["name"] == "propagation")
    assert prop_signal["explanation"] != "insufficient data"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_cli_no_input_exits_nonzero() -> None:
    result = _run(["--json"], stdin="")
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# JSON schema from CLI output
# ---------------------------------------------------------------------------

def test_cli_output_json_schema_stable() -> None:
    result = _run(["Schema stability test.", "--json"])
    parsed = json.loads(result.stdout)
    assert "version" in parsed
    assert "fingerprint" in parsed
    assert "signals" in parsed
    assert len(parsed["signals"]) == 3
