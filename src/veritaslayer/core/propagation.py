from __future__ import annotations


def analyze_propagation(
    repost_count: int,
    source_count: int,
    time_to_viral_minutes: int,
) -> dict[str, float | str]:
    repost_pressure = min(1.0, max(0, repost_count) / 1200)
    source_bonus = min(1.0, max(1, source_count) / 8)
    velocity_penalty = 0.25 if (0 < time_to_viral_minutes < 45) else 0.0

    score = max(0.0, min(1.0, 0.55 + source_bonus * 0.35 - repost_pressure * 0.35 - velocity_penalty))

    return {
        "score": round(score, 4),
        "confidence": 0.7,
        "label": "healthy" if score >= 0.6 else "anomalous",
    }
