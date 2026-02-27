from __future__ import annotations

import re


def analyze_text_forensic(text: str) -> dict[str, float | str]:
    token_count = max(1, len(text.split()))
    punctuation_spikes = len(re.findall(r"[!?]{2,}|\.\.\.", text))
    synthetic_markers = len(
        re.findall(
            r"\b(as an ai|in conclusion|it is important to note|i cannot|i can not)\b",
            text.lower(),
        )
    )

    pressure = min(1.0, (punctuation_spikes / token_count) * 4.0 + synthetic_markers * 0.08)
    score = max(0.0, 1.0 - pressure)

    return {
        "score": round(score, 4),
        "confidence": round(min(1.0, 0.55 + min(token_count, 500) / 1500), 4),
        "label": "low synthetic signature" if score >= 0.5 else "synthetic markers detected",
    }
