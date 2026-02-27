"""Pydantic v2 strict report schema — extra='forbid' blocks injection."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from pydantic import BaseModel, ConfigDict, Field

    _PYDANTIC = True
except ModuleNotFoundError:
    _PYDANTIC = False


if _PYDANTIC:

    class AuthenticitySignal(BaseModel):
        model_config = ConfigDict(extra="forbid")

        name: str
        probability_synthetic: float = Field(..., ge=0.0, le=1.0)
        explanation: str
        confidence: float = Field(..., ge=0.0, le=1.0)
        details: dict[str, Any] = Field(default_factory=dict)

    class AuthenticityReport(BaseModel):
        model_config = ConfigDict(extra="forbid")

        overall_synthetic_probability: float = Field(..., ge=0.0, le=1.0)
        signals: list[AuthenticitySignal]
        fingerprint: dict[str, Any]
        source_url: str | None = None
        timestamp: str = Field(
            default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
        )
        version: str = "0.1.0"
        security_note: str = (
            "Report is deterministic given input. Signed commits required upstream."
        )

else:
    # Fallback dataclass for envs without pydantic installed
    from dataclasses import asdict, dataclass, field

    @dataclass(frozen=True)
    class AuthenticitySignal:  # type: ignore[no-redef]
        name: str
        probability_synthetic: float
        explanation: str
        confidence: float
        details: dict[str, Any] = field(default_factory=dict)

    @dataclass(frozen=True)
    class AuthenticityReport:  # type: ignore[no-redef]
        overall_synthetic_probability: float
        signals: list[AuthenticitySignal]
        fingerprint: dict[str, Any]
        source_url: str | None = None
        timestamp: str = field(
            default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
        )
        version: str = "0.1.0"
        security_note: str = (
            "Report is deterministic given input. Signed commits required upstream."
        )

        def model_dump(self, **_: Any) -> dict[str, Any]:
            return asdict(self)

        def model_dump_json(self) -> str:
            import json

            return json.dumps(self.model_dump())


def build_report(
    text: str,
    source_url: str | None,
    fingerprint: dict[str, Any],
    forensic_signal: dict[str, Any],
    credibility_signal: dict[str, Any],
    propagation_signal: dict[str, Any],
) -> AuthenticityReport:
    forensic_score: float = float(forensic_signal.get("score", 0.5))
    cred_score: float = float(credibility_signal.get("score", 0.5))
    prop_score: float = float(propagation_signal.get("score", 0.5))

    # Synthetic probability is inverse of authenticity
    forensic_synthetic = round(1.0 - forensic_score, 4)
    cred_synthetic = round(1.0 - cred_score, 4)
    prop_synthetic = round(1.0 - prop_score, 4)

    overall = round(
        forensic_synthetic * 0.4 + cred_synthetic * 0.35 + prop_synthetic * 0.25, 4
    )

    signals = [
        AuthenticitySignal(
            name="forensic",
            probability_synthetic=forensic_synthetic,
            explanation=str(forensic_signal.get("label", "")),
            confidence=float(forensic_signal.get("confidence", 0.5)),
            details={
                k: v
                for k, v in forensic_signal.items()
                if k not in {"score", "confidence", "label"}
            },
        ),
        AuthenticitySignal(
            name="credibility",
            probability_synthetic=cred_synthetic,
            explanation=str(credibility_signal.get("label", "")),
            confidence=float(credibility_signal.get("confidence", 0.5)),
            details={
                k: v
                for k, v in credibility_signal.items()
                if k not in {"score", "confidence", "label"}
            },
        ),
        AuthenticitySignal(
            name="propagation",
            probability_synthetic=prop_synthetic,
            explanation=str(propagation_signal.get("label", "")),
            confidence=float(propagation_signal.get("confidence", 0.5)),
            details={
                k: v
                for k, v in propagation_signal.items()
                if k not in {"score", "confidence", "label"}
            },
        ),
    ]

    return AuthenticityReport(
        overall_synthetic_probability=overall,
        signals=signals,
        fingerprint=fingerprint,
        source_url=source_url,
    )
