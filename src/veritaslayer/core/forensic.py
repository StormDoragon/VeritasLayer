"""Baseline heuristic forensic text analyser.

.. warning::
    This module implements a simple rule-based heuristic, **not** a
    calibrated statistical or ML model.  Scores should be interpreted
    as weak prior signals only.  False-positive and false-negative rates
    have not been measured.  See docs/methodology.md for the roadmap
    toward a benchmarked replacement.
"""
from __future__ import annotations

import re


def analyze_text_forensic(text: str) -> dict[str, float | str]:
    """Return a heuristic forensic signal for *text*.

    Signals detected
    ----------------
    - Punctuation spikes (``!!``, ``???``, ``...``)
    - Common synthetic-text phrase markers

    Confidence scales with token count but is capped at 0.72 to reflect
    the heuristic nature of this analyser.
    """
    token_count = max(1, len(text.split()))
    punctuation_spikes = len(re.findall(r"[!?]{2,}|\.\.\.", text))
    synthetic_markers = len(
        re.findall(
            r"\b(as an ai|in conclusion|it is important to note|i cannot|i can not)\b",
            text.lower(),
        )
    )

    pressure = min(
        1.0,
        (punctuation_spikes / token_count) * 4.0 + synthetic_markers * 0.08,
    )
    score = max(0.0, 1.0 - pressure)

    # Cap confidence at 0.72 — this is a heuristic, not a calibrated model
    confidence = round(min(0.72, 0.55 + min(token_count, 500) / 1500), 4)

    return {
        "score": round(score, 4),
        "confidence": confidence,
        "label": (
            "low synthetic signature" if score >= 0.5 else "synthetic markers detected"
        ),
        "analyser": "baseline_heuristic_v0",
    }
