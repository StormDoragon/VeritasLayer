# Architecture

VeritasLayer is organized into modular layers. Each layer has a single responsibility and can be swapped independently.

## Layer overview

```
CLI (veritaslayer.cli.main)
  └── orchestrates signal modules + report composition

Core signal modules (veritaslayer.core.*)
  ├── credibility.py   — source domain credibility scoring
  ├── fingerprinting.py — cryptographic + perceptual fingerprinting
  ├── forensic.py      — text forensic analysis (baseline heuristic)
  └── propagation.py   — propagation pattern analysis

Report utilities (veritaslayer.utils.report)
  └── build_report()   — composes signals into AuthenticityReport (Pydantic v2)
```

## Design constraints

- **No certainty claims.** Every output is a probability in [0, 1] with an associated confidence score.
- **Explainability.** Every signal carries a human-readable `label` and `explanation`.
- **Strict schema.** `AuthenticityReport` uses `extra="forbid"` to prevent field injection.
- **Modularity.** Each core module is independently importable; the CLI is just one consumer.
- **No eval/exec.** Zero dynamic code execution in production paths.

## Report composition

The `build_report()` function weights signals as follows (subject to change as calibration data becomes available):

| Signal | Weight |
|---|---|
| Forensic | 40% |
| Credibility | 35% |
| Propagation | 25% |

## Current implementation status

See `README.md` for the up-to-date status table. Architecture documents may describe planned modules that are not yet implemented.
