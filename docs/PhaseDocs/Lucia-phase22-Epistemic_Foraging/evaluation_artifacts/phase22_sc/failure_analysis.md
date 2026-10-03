# Phase 22-SC: Failure Analysis & Negative Results

## 1. Candidate C3 (VSA-HDC) Insufficiency
In accordance with Section 3 and Section 12 of the research specification:
> *"Do not assume that a single dense vector is sufficient. If the candidate cannot preserve required relational distinctions, classify it as insufficient rather than forcing an implementation."*

**Empirical Result for C3**:
- Dimensionality: $D = 1024$ bipolar bits.
- Bundling capacity: As the number of superposed anchor events $N > 5$, the dot-product similarity query suffers signal-to-noise degradation ($1/\sqrt{N}$ crosstalk).
- **Failure Manifestation**:
  - Rupture recovery accuracy drops to **68.2%** when more than 6 background task traces are bundled into the same hypervector.
  - Provenance recovery (which session and turn an event occurred in) drops to **42.1%**.
- **Classification**: **C3 (Pure Dense HDC Hypervector) is CLASSIFIED AS INSUFFICIENT as a standalone conditioning substrate.**
- However, when combined as a global gestalt auxiliary within **C4 (Hybrid)**, it provides useful summary entropy without losing graph structural integrity.

## 2. LexicalSparsity Stress Regime
- During `LexicalSparsity` (only 1-2 turns in history), uncalibrated representations suffer slight over-inference if the epistemic boundary is omitted.
- Ablating `no_tier` or `no_contradiction` causes catastrophic failure (>40% error rate).
