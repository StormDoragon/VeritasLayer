# Methodology

VeritasLayer produces probabilistic authenticity signals. This document describes the methodology for each signal module, distinguishing implemented heuristics from planned research work.

## Core principles

1. **No certainty claims.** All outputs are probabilities in [0.0, 1.0].
2. **Explainable module outputs.** Every signal carries a label and confidence score.
3. **Auditable report composition.** Weights and formulas are documented here.

---

## Module A — Content Fingerprinting

**Status: Implemented (partial)**

### Implemented
- SHA-256 and SHA3-256 cryptographic hashes of raw content bytes.
- Byte-level entropy proxy (standard deviation of byte values) as a rough measure of content randomness.

### Planned
- Perceptual hash (pHash) for images — detects near-duplicate images that differ in compression or minor edits.
- Frame-level hashing for video.
- Text shingling / MinHash for near-duplicate text detection.

---

## Module B — Forensic Text Analysis

**Status: Baseline heuristic — not calibrated**

### Current implementation (`baseline_heuristic_v0`)
Detects two signal types:
- **Punctuation spikes**: consecutive `!!`, `???`, `...` patterns inflate a pressure score.
- **Synthetic phrase markers**: exact phrases (`as an ai`, `in conclusion`, `it is important to note`, `i cannot`, `i can not`) contribute to pressure.

Synthetic probability = pressure score. Confidence is capped at 0.72 to reflect the heuristic nature of the module.

### Limitations
- Trivially bypassed by rephrasing.
- False-positive and false-negative rates have not been measured.
- Confidence scaling with token count is a proxy, not a calibration.

### Planned
- Perplexity-based scoring using a reference language model.
- Stylometric features (sentence length distribution, vocabulary richness).
- Calibrated confidence intervals from benchmark datasets.

---

## Module C — Source Credibility

**Status: Domain-list matching — not ML-backed**

### Current implementation
- Normalises URLs (strips `www.`, port numbers, lowercases).
- Matches normalised domain and subdomains against a hard-coded trusted set (`apnews.com`, `reuters.com`, `bbc.com`, `nature.com`, `wikipedia.org`) and a flagged set.
- Returns fixed scores: 0.85 (trusted), 0.20 (flagged), 0.55 (unknown), 0.45 (no source).

### Limitations
- Trusted/flagged lists are very small and manually maintained.
- Does not check domain age, WHOIS, or historical credibility signals.

### Planned
- Domain age and registration data (via RDAP/WHOIS).
- Historical credibility scoring from third-party datasets.
- Weighted ensemble with ML-backed source reputation model.

---

## Module D — Propagation Analysis

**Status: Formula heuristic — not benchmarked**

### Current implementation
Uses three inputs: `repost_count`, `source_count`, `time_to_viral_minutes`.

```
repost_pressure = min(1.0, repost_count / 1200)
source_bonus    = min(1.0, source_count / 8)
velocity_penalty = 0.25 if 0 < time_to_viral_minutes < 45 else 0.0

score = 0.55 + source_bonus × 0.35 − repost_pressure × 0.35 − velocity_penalty
```

When all inputs are at default values (no real propagation data supplied), the module returns `label="insufficient data"` and `confidence=0.3`.

### Limitations
- Constants (1200, 8, 45, 0.25, 0.35) are not empirically derived.
- Does not model network topology or bot-amplification patterns.

### Planned
- Graph-based propagation mapping.
- Bot-detection integration.
- Empirically calibrated thresholds from labelled datasets.

---

## Report composition

Signals are combined into `overall_synthetic_probability` using a fixed weighted sum:

```
overall = forensic_synthetic × 0.40
        + credibility_synthetic × 0.35
        + propagation_synthetic × 0.25
```

Where `*_synthetic = 1.0 − signal_score`.

These weights are initial estimates and will be updated as calibration data becomes available.
