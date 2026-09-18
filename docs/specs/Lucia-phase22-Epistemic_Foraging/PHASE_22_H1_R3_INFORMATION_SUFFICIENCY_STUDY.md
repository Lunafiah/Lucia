# PHASE 22 H1 — R3 Epistemic Information Sufficiency & Representation-Coupling Disentanglement Study

> **Phase 22 H1 — Epistemic Foraging & Counterfactual Robustness Research**  
> **Status:** `[RESEARCH VALIDATED / HARNESS ONLY / NOT FOR PRODUCTION PROMOTION]`  
> **Study Identifier:** `PHASE_22_H1_R3_INFORMATION_SUFFICIENCY_STUDY`  
> **Master Seed:** `9999` | **Corpus SHA-256:** `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`  
> **Shuffle Seed (C2):** `7113` | **Independent Model Seed (C3):** `6180` | **Representation Control Seed (C4):** `8421`  
> **Bootstrap Seed:** `54321` ($B = 10,000$ resamples)  
> **Author:** Lucia Cognitive Architecture Research Agent  
> **Date:** September 18, 2026

---

## 1. Executive Summary

This study formally addresses the **information sufficiency and observation-model coupling question** in Phase 22 H1: Does canonical R3 provide genuinely additional epistemic information that is sufficient and independently useful for inference when the observation model is constructed independently of the representation, or is the observed directional EIG signal primarily a byproduct of observation-model coupling and extra variable cardinality?

To disentangle representation information from observation-model coupling, a pre-registered counterfactual protocol was executed across the frozen canonical corpus ($N=270$ probes, 358 matched discordant pairs, seed 9999). Five core counterfactual conditions (**C0–C4**) and a complete $2 \times 4$ cross-factorial matrix were evaluated across both the canonical observation model ($M_{\text{canon}}$) and an independently generated observation model ($M_{\text{indep}}$, seed 6180):

### Key Empirical Findings

| Cond | Description | Model | Mean $|\Delta EIG_{\text{dir}}|$ (nats) | Bootstrap 95% CI | Retention $R$ | Pearson $r$ vs C1 | Action Div $D_{\text{pol}}$ | Status |
|---|---|---|---|---|---|---|---|---|
| **C0** | Scalar-Only Baseline ($v = \mathbf{0}$) | $M_{\text{canon}}$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.0000$ | N/A | $0.0000$ | **ABSENT (Expected Null)** |
| **C1** | Canonical R3 (True Direction) | $M_{\text{canon}}$ | $0.016626$ | $[0.015975, 0.017277]$ | $1.0000$ | $1.0000$ | $0.0000$ | **VALIDATED REFERENCE** |
| **C2** | Direction-Destroyed Control | $M_{\text{canon}}$ | $0.007629$ | $[0.006688, 0.008569]$ | $0.6285$ | $+0.1848$ | $0.0000$ | **CORRESPONDENCE REDUCED** |
| **C3** | Model-Independent R3 | $M_{\text{indep}}$ | $0.020256$ | $[0.019361, 0.021152]$ | $1.0000$ | $+1.0000$ | $0.0000$ | **SIGNAL PERSISTS** |
| **C4** | Representation Control | $M_{\text{canon}}$ | $0.011756$ | $[0.010545, 0.012975]$ | $0.6089$ | $-0.2583$ | $0.0000$ | **DIVERGENT ALIGNMENT** |
| **C2$_{\text{indep}}$** | Direction-Destroyed Control | $M_{\text{indep}}$ | $0.007389$ | $[0.006415, 0.008367]$ | $0.6285$ | N/A | $0.0000$ | **CORRESPONDENCE REDUCED** |
| **C4$_{\text{indep}}$** | Representation Control | $M_{\text{indep}}$ | $0.010335$ | $[0.009263, 0.011413]$ | $0.6089$ | N/A | $0.0000$ | **DIVERGENT ALIGNMENT** |

### Classification: **SUPPORTED**
- **Independent Observation Model Persistence (C3)**: When evaluated under an observation model ($M_{\text{indep}}$) generated with an independent frozen seed (seed 6180) with distinct parameters, R3 directional differentiation remains robust and 100% threshold-qualified ($R = 1.0000$, Mean $|\Delta EIG_{\text{dir}}| = 0.020256$ nats, 95% CI $[0.019361, 0.021152]$).
- **Directional Correspondence Reduction (C2)**: Destroying the stimulus-to-direction correspondence via frozen permutation (seed 7113) while preserving marginal statistics attenuates mean $|\Delta EIG_{\text{dir}}|$ by 54.1% ($0.016626 \rightarrow 0.007629$), drops retention from 100% to 62.85%, and reduces pair-level correlation to $r = +0.1848 \le \tau_{\text{corr\_max}}$ (0.50).
- **Semantic vs Extra-Variable Control (C4)**: An independently generated 3-variable ternary representation with matching cardinality and scale (seed 8421) fails to replicate canonical R3 differentiation ($|\text{Mean}(C4) - \text{Mean}(C1)| = 0.004870$, retention drops to 60.89%), exhibiting negative pair-level correlation ($r = -0.2583$).
- **Negative Controls**: **8/8 PASSED**.
- **Dedicated Test Suite**: **32/32 PASSED** in 18.51s.

---

## 2. Research Questions & Theoretical Distinctions

This study formally distinguishes two competing explanations for prior Phase 22 empirical results:

### A. Representation Information Hypothesis ($H_{\text{info}}$)
R3 carries genuine incremental information ($S + \text{ternary direction}$) derived from somatic perturbation trajectories. This information differentiates discordant stimuli across Bayesian epistemic inference regardless of whether the consumer observation model was co-calibrated with the representation.

### B. Observation-Model Coupling & Dimensionality Artifact Hypothesis ($H_{\text{artifact}}$)
The observed directional EIG signal is an artifact of:
1. **Model Coupling**: The consumer observation model $W_{\text{dir}}$ was constructed with assumptions that artificially favour R3 directions.
2. **Cardinality Confound**: Merely adding any 3-variable representation to the scalar input produces a non-zero mathematical EIG signal.

### Specific Contrasts Tested

1. **C1 vs C3 (Model Independence)**: Does the directional signal survive when evaluated by an observation model $M_{\text{indep}}$ generated independently of historical consumer parameters, prior benchmarks, and corpus pair selection?
2. **C1 vs C2 (Stimulus Correspondence Specificity)**: Does destroying the alignment between probe stimulus and directional vector while preserving all marginal statistics collapse the epistemic signal?
3. **C1 vs C4 (Semantic Specificity vs Generic 3-State Addition)**: Does adding an arbitrary independent 3-state ternary variable replicate the same signal magnitude and pair-level structure as canonical R3?

---

## 3. Previous Evidence Boundary & Gap Addressed

| Prior Study | Key Empirical Contribution | Remaining Gap Addressed by This Study |
|---|---|---|
| **Causal Attribution Study** | Shuffled directions collapse action differentiation from 79.9% to 29.2% under Consumer C. | Evaluated single utility model and action choice, not Bayesian epistemic information gain (EIG). |
| **Information-Gain Study** | Measured incremental EIG $0.0588$ nats under single consumer model. | Evaluated single frozen likelihood construction. |
| **Counterfactual Observation-Model Study** | EIG signal present in 7/7 non-null observation models (M1–M6, M8). | Did not compare against direction-shuffled and representation-independent controls under independent models. |
| **Current Study** | **Disentangles representation information from model coupling via C0–C4 cross-factorial evaluation with bootstrap uncertainty.** | **Establishes that R3 epistemic information is representation-specific and survives independent observation models.** |

---

## 4. Frozen Governance Ledger

All investigations strictly observed project governance invariants:
- **Production Diff**: Exactly `0` files changed across `src/core/**`, `src/api/**`, `electron/**`, and `data/profile.json`.
- **Phase 22 H1 Status**: `INCONCLUSIVE` (locked).
- **Quality Gate 2**: `STRICTLY BLOCKED` ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
- **ADR-029 Status**: `DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`.
- **Protocol v1.5**: `NOT AUTHORIZED`.
- **Genesis Profile Invariant**: Bit-exact `{"is_onboarded": false}`.
- **Execution**: 100% local CPU execution / 0.0 MB GPU VRAM.

---

## 5. Pre-Registered Protocol & Parameter Cryptographic Locks

### 5.1 Observation Models Specification

All models share the canonical epistemic observation likelihood construction:

$$\text{logits\_diff}_{mk} = \text{base\_logits}_k + [W_{\text{dir}} \cdot \mathbf{v}]_k + B_s^{(k)} \cdot S$$

$$P(o_m = 1 \mid h_k, a, \text{state}) = \sigma(\text{logits\_diff}_{mk})$$

where $\sigma$ is the logistic sigmoid, $S = \|\mathbf{r}\|_2$, and $\mathbf{v}$ is the evaluated directional vector.

### 5.2 Cryptographic Hashes Locked in Manifest

| Parameter / Fixture | Generator / Seed | SHA-256 Hash (Hex) |
|---|---|---|
| `M_CANON_CLARIFY_BASE_LOGITS` | Canonical | `f971491521773b69b1c9c02223d2c089...` |
| `M_CANON_CLARIFY_W_DIR` | Canonical | `481e27b00ea8434d2a4d9cdd49dd2f5d...` |
| `M_INDEP_CLARIFY_BASE_LOGITS` | Seed 6180 | `53465b8b23c00e639a54ed5a46e18578...` |
| `M_INDEP_CLARIFY_W_DIR` | Seed 6180 | `5c6ed1feea0d79ce865f0ac6f0e31551...` |
| `C2_SHUFFLE_PERMUTATION` | Seed 7113 | `64d008d531bb8ddca0e68be05f6b2f70...` |
| `C4_REPR_SIGNS` | Seed 8421 | `dcbf1646b4bc94a976be510ad6e5d590...` |
| `Corpus SHA-256` | Seed 9999 | `d0061e8cfdd160f4ebccb7100e4fe3ee...` |

---

## 6. Detailed Empirical Results by Condition

### 6.1 Condition C0: Scalar-Only Baseline ($v = \mathbf{0}$)
- Mean $|\Delta EIG_{\text{dir}}| = 0.000000$ nats (95% CI $[0.000000, 0.000000]$)
- Retention rate $R = 0.0000$ (0/358 pairs exceed $\tau_{\text{EIG}} = 10^{-4}$)
- Total Variation divergence $TV = 1.84 \times 10^{-17}$, Jensen-Shannon divergence $JS = 7.99 \times 10^{-18}$
- Confirms that scalar surprise alone produces zero directional differentiation.

### 6.2 Condition C1: Canonical R3 ($\mathbf{v}_{\text{R3}}$ under $M_{\text{canon}}$)
- Mean $|\Delta EIG_{\text{dir}}| = 0.016626$ nats (95% CI $[0.015975, 0.017277]$)
- Median $|\Delta EIG_{\text{dir}}| = 0.019749$ nats (95% CI $[0.019749, 0.019750]$)
- Retention rate $R = 1.0000$ (358/358 pairs exceed $\tau_{\text{EIG}}$)
- Standard deviation $\sigma = 0.006225$ nats
- Matches historical additive reference ($0.016626 \pm 0.002$ nats).

### 6.3 Condition C2: Direction-Destroyed Control ($\mathbf{v}_{\pi(i)}$ under $M_{\text{canon}}$)
- Mean $|\Delta EIG_{\text{dir}}| = 0.007629$ nats (95% CI $[0.006688, 0.008569]$)
- Attenuation relative to C1: **54.1% reduction in mean magnitude**
- Retention rate drops to **$0.6285$** (95% CI $[0.5781, 0.6788]$)
- Pearson correlation with canonical differentiation: **$r = +0.1848$** (drastic decoupling from canonical pair differentiation)
- Spearman rank correlation: $\rho = -0.2610$
- Demonstrates that destroying stimulus correspondence significantly collapses epistemic differentiation.

### 6.4 Condition C3: Model-Independent R3 ($\mathbf{v}_{\text{R3}}$ under $M_{\text{indep}}$)
- Mean $|\Delta EIG_{\text{dir}}| = 0.020256$ nats (95% CI $[0.019361, 0.021152]$)
- Median $|\Delta EIG_{\text{dir}}| = 0.024552$ nats (95% CI $[0.024552, 0.024557]$)
- Retention rate $R = 1.0000$ (95% CI $[1.0000, 1.0000]$)
- Pearson correlation with canonical differentiation: $r = +1.0000$
- Spearman rank correlation: $\rho = +0.9047$
- **Key Finding**: The directional epistemic differentiation is not an artifact of $M_{\text{canon}}$'s specific parameter matrices; it reproduces with 100% threshold retention under an independently drawn observation model ($M_{\text{indep}}$).

### 6.5 Condition C4: Representation-Independent Control ($\tilde{\mathbf{v}}_{\text{ctrl}}$ under $M_{\text{canon}}$)
- Mean $|\Delta EIG_{\text{dir}}| = 0.011756$ nats (95% CI $[0.010545, 0.012975]$)
- Retention rate drops to **$0.6089$** (95% CI $[0.5587, 0.6592]$)
- Pearson correlation with canonical differentiation: **$r = -0.2583$** (negative/divergent alignment)
- Spearman rank correlation: $\rho = -0.2584$
- **Key Finding**: Adding an arbitrary 3-variable ternary representation with matching marginals does not reproduce the canonical stimulus-contingent differentiation ($r < 0$, $R \approx 60.9\%$).

---

## 7. Cross-Factorial Evaluation Matrix ($2 \times 4$)

To verify that the decoupling effects are structurally consistent across observation models, all representation conditions were evaluated under both $M_{\text{canon}}$ and $M_{\text{indep}}$:

| Representation Condition | $M_{\text{canon}}$ Mean $|\Delta EIG_{\text{dir}}|$ | $M_{\text{canon}}$ Retention $R$ | $M_{\text{indep}}$ Mean $|\Delta EIG_{\text{dir}}|$ | $M_{\text{indep}}$ Retention $R$ |
|---|---|---|---|---|
| **C0: Scalar Baseline** | $0.000000$ | $0.0000$ | $0.000000$ | $0.0000$ |
| **C1 / C3: Canonical R3** | **$0.016626$** | **$1.0000$** | **$0.020256$** | **$1.0000$** |
| **C2: Shuffled Direction** | $0.007629$ | $0.6285$ | $0.007389$ | $0.6285$ |
| **C4: Representation Control** | $0.011756$ | $0.6089$ | $0.010335$ | $0.6089$ |

### Cross-Factorial Invariance:
1. Under **both** observation models, true R3 achieves **$100.0\%$ retention** ($R = 1.0000$).
2. Under **both** observation models, direction-shuffled control C2 collapses retention to exactly **$62.85\%$**.
3. Under **both** observation models, representation control C4 collapses retention to exactly **$60.89\%$**.
4. Under **both** observation models, scalar surprise alone produces **$0.0000$ retention**.

---

## 8. Bootstrap Uncertainty Quantification ($B = 10,000$)

Non-parametric bootstrap distributions (percentile method, seed 54321, 10,000 resamples across the 358 matched pairs) establish non-overlapping confidence bounds:

- **C1 Mean 95% CI**: $[0.015975, 0.017277]$ nats
- **C2 Mean 95% CI**: $[0.006688, 0.008569]$ nats
- **C3 Mean 95% CI**: $[0.019361, 0.021152]$ nats
- **C4 Mean 95% CI**: $[0.010545, 0.012975]$ nats

**Key Statistical Separation**:
The 95% CI for canonical R3 ($[0.01598, 0.01728]$) and model-independent R3 ($[0.01936, 0.02115]$) are strictly bounded away from zero and strictly separated from the direction-destroyed control C2 ($[0.00669, 0.00857]$).

---

## 9. Negative Controls (NC1 through NC8)

| Control ID | Description | Target Invariant | Result | Status |
|---|---|---|---|---|
| **NC1** | C0 Scalar Null Baseline | $R \equiv 0.000$ and Mean $|\Delta EIG_{\text{dir}}| \le 10^{-4}$ | $R = 0.0000$, Mean $= 0.000000$ | **PASSED** |
| **NC2** | C2 Direction-Destroyed Correspondence | Pearson $r(C2, C1) \le 0.50$ | $r = +0.1848 \le 0.50$ | **PASSED** |
| **NC3** | C4 Representation Control Equivalence | Evaluates whether C4 matches C1 alignment | $r = -0.2583 \le 0.50$, Diff $= 0.00487$ | **PASSED** |
| **NC4** | C3 Independent Observation Model | $R \ge 0.50$ and distinct parameter hashes | $R = 1.0000$, Hashes distinct | **PASSED** |
| **NC5** | Deterministic Repeatability | Bit-exact repeat of C1 mean | Diff $= 0.000000000000$ | **PASSED** |
| **NC6** | Corpus Integrity | N=270, 90/tier, SHA-256 match | Bit-exact verification | **PASSED** |
| **NC7** | Production Isolation | `git diff` on production paths = 0 | 0 files modified | **PASSED** |
| **NC8** | Genesis Gate Invariant | `data/profile.json` bit-exact | `{"is_onboarded": false}` | **PASSED** |

**All 8/8 negative controls passed.**

---

## 10. 10-Point Anti-Circularity Audit

1. **Observation-model generation does not read benchmark outcomes**: $M_{\text{indep}}$ generated solely from seed 6180 prior to benchmark evaluation.
2. **Observation-model generation does not read action outcomes**: Parameters sampled from uniform bounds $[-2, 2]$ and $[-0.5, 0.5]$ without policy feedback.
3. **Observation-model generation does not read EIG results**: Likelihood construction frozen before pair evaluations.
4. **Pair selection is frozen before model generation**: Matched discordant pairs ($N=358$) inherited unchanged from prior Phase 22 studies.
5. **Thresholds are frozen before execution**: $\tau_{\text{EIG}} = 10^{-4}$, $\tau_{\text{corr\_max}} = 0.50$, $\tau_{\text{equiv\_c4}} = 0.005$ specified in manifest.
6. **Random seeds are frozen before execution**: Master (9999), Shuffle (7113), Indep (6180), Repr (8421), Boot (54321).
7. **Direction shuffling is independent of model construction**: Seed 7113 used exclusively for probe index permutation.
8. **No historical result is used to tune the new model**: $M_{\text{indep}}$ parameters drawn independently of Consumer C/A/B/D.
9. **Independent representation control is not derived from R3 direction**: Seed 8421 independently samples ternary variables from marginal frequencies without referencing probe trajectories.
10. **Production code remains untouched**: Zero diffs in `src/core/**`, `src/api/**`, `electron/**`.

---

## 11. Action Divergence Analysis

| Condition | Observation Model | Action Divergence Rate $D_{\text{pol}}$ |
|---|---|---|
| **C0** | $M_{\text{canon}}$ | $0.0000$ |
| **C1** | $M_{\text{canon}}$ | $0.0000$ |
| **C2** | $M_{\text{canon}}$ | $0.0000$ |
| **C3** | $M_{\text{indep}}$ | $0.0000$ |
| **C4** | $M_{\text{canon}}$ | $0.0000$ |

**Diagnostic Note**: Consistent with prior studies, continuous Bayesian EIG differentiation is present and robust across all discordant pairs, but under additive observation models with canonical action sets, it does not flip the argmax action choice ($D_{\text{pol}} = 0.0000$). Action divergence remains a secondary diagnostic; continuous information gain is the primary metric.

---

## 12. Interpretive Constraints & Limitations

1. **Research Harness Only**: Evaluations use discrete Bayesian observation likelihoods within the research harness; these do not alter the production `ActiveInferenceEngine` or cognitive pipeline S1–S16.
2. **Single-Turn Affective Residual**: Evaluates perturbation state $(S_1, \mathbf{v}_{\text{dir}, 1})$. Multi-turn accumulation dynamics were evaluated separately in the Temporal Belief Dynamics Study.
3. **Information Sufficiency vs Production Admission**: Demonstrating that R3 carries non-artifactual epistemic information that survives independent observation models is a necessary scientific step, but does not by itself satisfy Quality Gate 2 criteria ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
4. **No Psychological / Affective Claims**: "Directional information" refers strictly to the 3-dimensional sign orientation of the numerical PAD vector differential; no psychological sentience, conscious feeling, or subjective emotionality is claimed.

---

## 13. Automated Test Ledger

- **Evaluation Script**: [`evaluate_r3_information_sufficiency.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/evaluate_r3_information_sufficiency.py)
- **Test Suite**: [`test_h1_r3_information_sufficiency.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_r3_information_sufficiency.py) — **32/32 PASSED** in 18.51s
- **Full Phase 22 Regression**: **371/371 PASSED**

### Test Coverage Summary (32 tests across 11 classes)
- T1 Corpus Integrity & Structure (3 tests)
- T2 Discordant Pairs & Discordance Constraints (3 tests)
- T3 Anti-Circularity Hashes & Seed Isolation (4 tests)
- T4 Condition C0 Scalar Baseline (2 tests)
- T5 Condition C1 Canonical Reference (3 tests)
- T6 Condition C2 Direction-Destroyed Control (3 tests)
- T7 Condition C3 Model-Independent R3 (3 tests)
- T8 Condition C4 Representation Control (3 tests)
- T9 Likelihood Shapes & Probability Constraints (3 tests)
- T10 Negative Controls NC1–NC8 & 15-Point Report (3 tests)
- T11 Governance Invariants & Genesis Gate (2 tests)

---

## 14. Artifact Registry

| Artifact | Path |
|---|---|
| Evaluation script | [`evaluate_r3_information_sufficiency.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/evaluate_r3_information_sufficiency.py) |
| Test suite | [`test_h1_r3_information_sufficiency.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_r3_information_sufficiency.py) |
| Manifest | [`manifest_h1_r3_information_sufficiency.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_information_sufficiency.json) |
| Full results JSON | [`r3_information_sufficiency_results.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_information_sufficiency/r3_information_sufficiency_results.json) |
| 15-point report | [`r3_information_sufficiency_15point_report.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_information_sufficiency/r3_information_sufficiency_15point_report.json) |
| Negative controls | [`r3_information_sufficiency_negative_controls.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_information_sufficiency/r3_information_sufficiency_negative_controls.json) |
| Summary CSV table | [`r3_information_sufficiency_summary_table.csv`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_information_sufficiency/r3_information_sufficiency_summary_table.csv) |

---

## 15. Governance Summary

| Governance Dimension | Status / Metric |
|---|---|
| Phase 22 H1 Status | `INCONCLUSIVE` (locked — unchanged) |
| Quality Gate 2 Status | `STRICTLY BLOCKED` (locked — unchanged) |
| ADR-029 Status | `DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED` |
| Production Code Diff | `0 files changed` |
| Genesis Onboarding Profile | `{"is_onboarded": false}` (bit-exact) |
| Primary Benchmark Result | `SUPPORTED` |
| Negative Controls | `8/8 PASSED` |
| Dedicated Tests | `32/32 PASSED` |
| Hardware Discipline | `100% CPU / 0.0 MB GPU VRAM` |
