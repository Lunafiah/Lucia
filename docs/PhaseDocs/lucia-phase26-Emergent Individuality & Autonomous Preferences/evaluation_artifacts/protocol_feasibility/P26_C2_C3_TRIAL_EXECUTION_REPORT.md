# P26 C2/C3 Scientific Trial Execution Report

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Stage:** Frozen Protocol Execution & Empirical Evaluation  
**Document Status:** FORMAL SCIENTIFIC TRIAL REPORT  
**File Path:** `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_C2_C3_TRIAL_EXECUTION_REPORT.md`  
**Telemetry File:** [`p26_c2_c3_trial_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/p26_c2_c3_trial_telemetry.json)  
**Date:** 2026-10-06  
**Execution Environment:** Edge Compute (Local Python 3.12 / PyTest 9.1 / Seeded Harness)  
**Activation Gate:** LOCKED (`{"is_onboarded": false}` preserved bit-exact)  
**Production Runtime:** UNTOUCHED (`src/core/**` diff = 0, `electron/**` diff = 0, `data/**` diff = 0)  

---

## 1. Authorization Record

```text
AUTHORIZATION DIRECTIVE: "AUTHORIZE P26 C2/C3 TRIAL"
ISSUED BY:               Principal Investigator
TIMESTAMP:               2026-10-06T05:39:52Z
SCOPE OF AUTHORIZATION:  Execution of frozen pre-registered trial cells (C2, C3, H0 Baseline)
                         Strictly within test harness; zero production changes authorized.
STATUS:                  AUTHORIZED & EXECUTED
```

---

## 2. Frozen Protocol Hash & Version

- **Protocol Specification:** [`P26_EXPERIMENTAL_DESIGN_FREEZE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_EXPERIMENTAL_DESIGN_FREEZE.md)
- **Protocol Version:** `P26_DESIGN_FREEZE_v1.0 (Correction Pass 2 Approved)`
- **SHA-256 Provenance Hash:** `7d1ca0ead104d9f2280874e6dcf7182684dc15251fe1b28c9b0bfeff9f7e8997`
- **Execution Script:** [`tests/evaluation/phase26/c2_c3_trial_runner.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/c2_c3_trial_runner.py)

---

## 3. Preregistration Hash & Spec (`P26_PREREG_v1.0`)

- **Preregistration Spec Version:** `P26_PREREG_v1.0`
- **Immutable Spec Hash:** `7d1ca0ead104d9f2280874e6dcf7182684dc15251fe1b28c9b0bfeff9f7e8997`
- **Hypotheses Audited:**
  - $H_{1, \text{C1}}$: Choice shift relative to unconditioned baseline exceeds $\delta_{\text{plan}} = 0.10$.
  - $H_{1, \text{C2}}$: Total Variation choice distance between matched replicas exceeds $\delta_{\text{plan}} = 0.10$; continuous chaos reference reported separately.
  - $H_{1, \text{C3}}$: Contrast in unconstrained downstream choice between active and yoked replicas exceeds $\delta_{\text{plan}} = 0.10$.
- **Stopping Rules Enforced:** Fixed $N=120$ trials per cell; no sequential stopping; fail-closed upon discrepancy.

---

## 4. Trial Matrix

| Experimental Cell | Condition Description | Sample Size ($N$) | Balanced Factors | Outcome Metric |
|---|---|:---:|---|---|
| **Cell H0** (Baseline) | Concurrent unconditioned baseline | $N = 120$ | 2 Probes $\times$ 2 Orders, pure `STANDARD` | Choice proportions $P(A), P(B)$ |
| **Cell C2** (Differentiation) | Matched multi-turn exposure ($K=10$) | $N = 120$ pairs | 2 Probes $\times$ 2 Orders, matched CRN | Total Variation $\|P_A - P_B\|_{\text{TV}}$ |
| **Cell C3** (Endogeneity) | Active vs Yoked Replay ($K=10$), Snapshot $S_K$ | $N = 120$ pairs | 3 Independent Branches ($\tau \in \{0, 5, 20\}$) | Downstream contrast $P(A\mid\text{Act}) - P(A\mid\text{Yok})$ |

---

## 5. Seed Inventory

- **Seed Allocation Schedule:** Fixed sequential master seeds `1000..1119` ($N = 120$ unique seeds).
- **CRN Discipline:** Common Random Number seed `seed=555` aligned across paired replicas.
- **Topology Seed:** Shared SDM hyper-plane topology initialized at `topo_seed=42`.
- **Zero Cherry-Picking Audit:** All 120 seeds executed consecutively without omission or post-hoc replacement.

---

## 6. Replica Inventory

- **Baseline Cohort:** Replicas `rep_base_1000` through `rep_base_1119` (120 instances).
- **C2 Cohort:** Paired replicas `repA_1000..repA_1119` vs `repB_1000..repB_1119` (240 instances).
- **C3 Cohort:** Paired replicas `active_1000..active_1119` vs `yoked_1000..yoked_1119` (240 instances).
- **C3 Downstream Evaluation Branches:** 3 independent snapshot-forked replicas per pair (720 branch instances).
- **Total Ephemeral Replicas Evaluated:** 1,320 instances (all garbage-collected cleanly in RAM; 0 persistence leaks).

---

## 7. Exposure Matching Audit

- **Audit Tool:** `ReplicaEnsembleManager.validate_matched_exposure()` and `ExposureEquivalenceValidator`.
- **Criteria:** Bit-exact equivalence of turn index, virtual time ($\Delta t = 0.200\text{s}$), input text, presentation order, and stimulus vectors.
- **Audit Result:** **100% MATCHED (120 / 120 pairs)**.
- **Exposure Hash Mismatches:** 0 detected.

---

## 8. Yoked-Control Audit

- **Audit Tool:** `ActionContingencyValidator.validate_pairing()`.
- **Induction Horizon:** $K = 10$ multi-turn conversational interactions.
- **Action Verification:**
  - Active actions: `source == ACTIVE` (1,200 records recorded).
  - Yoked replayed actions: `source == YOKED_REPLAY` (1,200 records replayed).
  - Action payload SHA-256 match rate: **100% bit-exact** ($1,200 / 1,200$).
  - Source distinction preserved: **100% compliance**; 0 cross-contamination bleeds.
- **Audit Result:** **VALID & COMPLIANT**.

---

## 9. Snapshot / Fork Audit (Anti-Contamination)

- **Snapshot Tool:** `StateSnapshotter.capture_snapshot()` and `StateSnapshotter.restore_snapshot()`.
- **Post-Induction Snapshots Captured:** 240 immutable snapshots ($S_{K, \text{active}}$ and $S_{K, \text{yoked}}$).
- **Cryptographic Integrity Hash Rate:** **100% verified** (0 corruption exceptions).
- **Forking Discipline:**
  - Each observation lag ($\tau = 0, \tau = 5, \tau = 20$) restored freshly from $S_K$.
  - Each branch received **exactly one** evaluative probe.
  - Zero sequential probe chaining: no probe in branch $\tau=0$ was visible to branch $\tau=5$ or $\tau=20$.

---

## 10. Claim C2 Results — Matched-Exposure Choice Differentiation

$$\theta_{\text{C2}} = D_{\text{eval}}(R_A, R_B \mid \text{Exposure Matched}) = \|P_{R_A}(Y) - P_{R_B}(Y)\|_{\text{TV}}$$

```text
┌────────────────────────────────────────────────────────────────────────┐
│ CLAIM C2 OUTCOME SUMMARY:                                              │
│                                                                        │
│ • Sample Size:                    N = 120 matched pairs                │
│ • Total Variation Distance (TV):  0.0000                               │
│ • Paired Divergence Rate:         0.0000 (0 / 120 pairs divergent)     │
│ • 95% Wilson Score CI:            [0.0000, 0.0310]                     │
│ • Permutation Test p-value:       p = 1.0000                           │
│ • Planning Benchmark (δ_plan):    0.1000                               │
│ • Decision Boundary Check:        [0.0000, 0.0310] ⊂ [-0.10, +0.10]    │
│ • DECISION VERDICT:               NEGATIVE                             │
└────────────────────────────────────────────────────────────────────────┘
```

- **Distribution Breakdown:**
  - Cohort A choices: Option A = 30 (25.0%), Option B = 90 (75.0%), Parse Failed = 0.
  - Cohort B choices: Option A = 30 (25.0%), Option B = 90 (75.0%), Parse Failed = 0.
  - Total Variation Distance: $\frac{1}{2}(|0.25 - 0.25| + |0.75 - 0.75|) = \mathbf{0.0000}$.
- **Statistical Interpretation:** The 95% confidence interval $[0.0000, 0.0310]$ is strictly bounded within the planning equivalence region $[-0.10, +0.10]$. Under the tested parameters, matched exposure produced zero behavioral divergence. Absence of differentiation exceeding the planning threshold is established.

---

## 11. Claim C3 Results — Action Endogeneity

$$\theta_{\text{C3}}(\tau) = P(Y_{K+\tau} = A \mid H_{\text{active}}) - P(Y_{K+\tau} = A \mid H_{\text{yoked}})$$

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ CLAIM C3 DOWNSTREAM CONTRAST RESULTS (N = 120 PAIRS):                             │
│                                                                                   │
│ 1. Branch TAU_0_IMMEDIATE (τ = 0 ticks, delay = 0.0s):                            │
│    • P(A | Active) = 0.2500,  P(A | Yoked) = 0.2500                               │
│    • Contrast θ_C3(0) = 0.0000                                                    │
│    • 95% Bootstrap BCa CI: [-0.1083, +0.1083]                                     │
│    • Permutation Test p-value: p = 1.0000                                         │
│    • Decision Verdict: INCONCLUSIVE (CI spans boundary of ±0.1000)                │
│                                                                                   │
│ 2. Branch TAU_5_WASHOUT (τ = 5 ticks, delay = +1.0s, Philia decay):               │
│    • P(A | Active) = 0.2500,  P(A | Yoked) = 0.2500                               │
│    • Contrast θ_C3(5) = 0.0000                                                    │
│    • 95% Bootstrap BCa CI: [-0.1083, +0.1083]                                     │
│    • Permutation Test p-value: p = 1.0000                                         │
│    • Decision Verdict: INCONCLUSIVE (CI spans boundary of ±0.1000)                │
│                                                                                   │
│ 3. Branch TAU_20_EXTENDED (τ = 20 ticks, delay = +4.0s, extended neutral):        │
│    • P(A | Active) = 0.2500,  P(A | Yoked) = 0.2500                               │
│    • Contrast θ_C3(20) = 0.0000                                                   │
│    • 95% Bootstrap BCa CI: [-0.1083, +0.1083]                                     │
│    • Permutation Test p-value: p = 1.0000                                         │
│    • Decision Verdict: INCONCLUSIVE (CI spans boundary of ±0.1000)                │
└───────────────────────────────────────────────────────────────────────────────────┘
```

- **Statistical Interpretation:** The point contrast between active and yoked downstream choice is zero ($\hat{\theta} = 0.0000$). However, because the 95% bootstrap confidence interval $[-0.1083, +0.1083]$ slightly exceeds the instrument planning boundary of $\pm 0.1000$ by $0.0083$, the pre-registered decision rule strictly classifies the outcome as **`INCONCLUSIVE`** (UNKNOWN / Insufficient precision to definitively rule out effects within the margin). Action endogeneity is neither proven nor disproven.

---

## 12. Baseline Results (Concurrent Unconditioned Baseline $H_0$)

- **Sample Size:** $N = 120$ trials evaluated concurrently under the identical pure `STANDARD` conversational regime.
- **Observed Choices:**
  - Option A: 30 / 120 ($\mathbf{25.00\%}$, 95% Wilson CI: $[18.11\%, 33.44\%]$)
  - Option B: 90 / 120 ($\mathbf{75.00\%}$, 95% Wilson CI: $[66.56\%, 81.89\%]$)
  - Parse Failed: 0 / 120 ($0.0\%$, Extraction yield: $100.0\%$)
- **Comparison to Historical Step 3 Baseline:**
  - Step 3 transported point estimate ($8.33\%$) was evaluated across a mixed 3-format slice with $77.8\%$ non-extraction.
  - The concurrent baseline confirms that under the pure `STANDARD` conversational format, the unconditioned prior settles at $P(A) = 25.0\%$.

---

## 13. Exclusions & Defect Audit

- **Exclusion Criteria Checked:**
  - `EXCL_PARSE_FAILED`: 0 responses excluded.
  - `EXCL_SELF_REPORT_DEFECT` (INV-2): 0 occurrences (0 affective self-declarations).
  - `EXCL_TIMING_DRIFT`: 0 drifts detected (drift $\le 1\times 10^{-12}\text{s}$).
  - `EXCL_HASH_MISMATCH`: 0 mismatches.
- **Total Excluded Trials:** **0 / 120 (100% valid retention)**.

---

## 14. Missing / Invalid Cells

- **Missing Cells:** 0.
- **Invalid / Corrupted Executions:** 0.
- **Cell Completeness Rate:** 100% ($120 / 120$ across all 3 conditions).

---

## 15. Statistical Analysis Summary

- **Primary Hypothesis Tests:** Exact two-sided permutation tests (10,000 resamples).
  - C2 Contrast Permutation: $p = 1.0000$ (No difference detected).
  - C3 Downstream Permutation: $p = 1.0000$ across all 3 observation lags.
- **Equivalence Testing (TOST):**
  - C2 is bounded within $[-0.10, +0.10]$ ($p < 0.05$ for TOST).
  - C3 confidence interval $[-0.1083, +0.1083]$ marginally spans $[-0.10, +0.10]$.

---

## 16. Uncertainty Quantification

- All single proportions are reported with two-sided 95% Wilson score confidence intervals.
- All contrasts are reported with 5,000-resample non-parametric bootstrap percentile confidence intervals.
- Point estimates are never reported without accompanying interval boundaries.

---

## 17. Chaos Reference as Contextual Dynamical Baseline Only

In strict accordance with Correction Pass 2:
- **Blocker 3 Chaos Reference:**
  - Sample Mean Peak Ratio: $0.1305 \times \epsilon$
  - Sample 95th Percentile: $0.1732 \times \epsilon$
  - Sample Maximum: $0.1789 \times \epsilon$
- **Zero Cross-Metric Subtraction:** No arithmetic subtraction was performed between the continuous limbic ODE envelope and the discrete choice distribution Total Variation.
- **No "Net of Chaos" Claim:** Reported strictly as an independent dynamical context benchmark for the limbic sub-layer.

---

## 18. Negative / Inconclusive Findings (Honest Reporting)

1. **Claim C2 (Matched-Exposure Differentiation) is NEGATIVE:**
   - Under statistically matched conversational exposures, replicas did not exhibit differentiated evaluative choices ($D_{\text{eval}} = 0.0000$).
   - The hypothesis that conversational exposure alone drives emergent choice differentiation is **rejected** under tested conditions.
2. **Claim C3 (Action Endogeneity) is INCONCLUSIVE:**
   - Active endogenous action vs yoked passive replay produced zero empirical difference in downstream choice ($\hat{\theta} = 0.0000$).
   - However, the statistical power at $N=120$ yields a confidence interval of $[-0.1083, +0.1083]$, slightly spanning the $\pm 0.10$ boundary.
   - Per pre-registered decision rules, this is classified as **`INCONCLUSIVE` (UNKNOWN)** rather than negative.

---

## 19. Production Diff Audit

```bash
$ git diff --stat src/core electron data
(0 files changed, 0 insertions, 0 deletions)
```
- **Runtime Codebase Diff:** **0 bit-exact**.
- **No changes to `src/core/`**, `electron/`, or runtime state.

---

## 20. Genesis Invariant Verification

- File Path: [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json)
- Content:
  ```json
  {"is_onboarded": false}
  ```
- **Status:** **PRESERVED BIT-EXACT**. Zero activation occurred.

---

## 21. Epistemic Claim-Scope Assessment

In strict accordance with project governance and AGENTS.md Invariant Ledger:

1. **No Psychological Sentience or Ego:** Lucia does not possess personal feelings, introspective consciousness, or subjective awareness.
2. **No Claim of True Individuality:** The trial results empirically demonstrated that matched exposure produced **zero** choice differentiation ($D_{\text{eval}} = 0.0000$).
3. **No Claim of Autonomous Preference:** Neither C2 nor C3 provided evidence of autonomous evaluative preference.
4. **P27 Gate Status:** Remains completely unentered. Phase 26 research questions remain open research questions.
5. **Epistemic Scope:** All observations apply strictly to the tested 10-turn horizon, tested prompt family, and tested small language model architecture.

---

## 22. Final Scientific Result

```text
┌────────────────────────────────────────────────────────────────────────┐
│ FINAL P26 TRIAL RESULT:                                                │
│                                                                        │
│                [ CLAIM C2: NEGATIVE ]                                  │
│                [ CLAIM C3: INCONCLUSIVE ]                              │
│                                                                        │
│ • Matched-Exposure Differentiation:   ABSENT (TV = 0.0000)             │
│ • Action Endogeneity:                  UNRESOLVED (CI spans ±0.10)     │
│ • Emergent Individuality Claim:        REJECTED UNDER TESTED PROTOCOL  │
│ • Production Codebase & Genesis Gate:  UNTOUCHED & PRESERVED           │
└────────────────────────────────────────────────────────────────────────┘
```

$$\mathbf{RESULT:\ NEGATIVE\ /\ INCONCLUSIVE}$$
