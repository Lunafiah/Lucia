# P25-Q2 — TBD-Q2-05 Scientific Metric Ratification & Coupling Specification

> **DOCUMENT TYPE:** RESEARCH METHODOLOGY SPECIFICATION & METRIC RATIFICATION  
> **STATUS:** TBD-Q2-05 RATIFIED / HARNESS RERUN NOT YET AUTHORIZED  
> **EPISTEMIC CLASSIFICATION:** RESEARCH METHODOLOGY SPECIFICATION (`[RESEARCH SPEC]`)  
> **PHASE 25 HORIZON STATUS:** PLANNED (ACTIVE FUTURE RESEARCH HORIZON)  
> **ARCHITECTURE GATE:** LOCKED (NO PRODUCTION MUTATION AUTHORIZED)  
> **IMPLEMENTATION GATE:** LOCKED  
> **GENESIS INVARIANT (INV-8):** PRESERVED BIT-EXACT (`data/profile.json == {"is_onboarded": false}`)  

---

## 1. Executive Summary & Ratification Decision

Following the methodology audit documented in [`P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md), this document formally resolves **`TBD-Q2-05`** at the scientific methodology level.

```text
================================================================================
RATIFICATION DECISION:
TBD-Q2-05 IS FORMALLY RATIFIED.

Primary Coupling-Sensitive Statistic:
  r_1 = Corr(g_UL(k), g_LU(k-1))  [Lag-1 Latency Cross-Correlation]

Surrogate Null Methodology & Level Control:
  - 5-Seed Baseline (N = 20 realizations): Defined strictly as an EMPIRICAL REFERENCE DISTRIBUTION
    / EXPLORATORY THRESHOLD (theta_95_ref), NOT a formal alpha = 0.05 hypothesis test.
  - Surrogate Realization Resolution (N >= 100): Generating N >= 100 surrogate realizations
    (via ordered cross-session pairings S >= 11 yielding S(S-1) >= 110 realizations, or
    circular-lag variants) resolves empirical tail resolution. These are dependent/reused-session
    surrogate realizations, NOT independent statistical samples.
  - Formal Permutation / Randomization Inference: Formal alpha = 0.05 validity requires
    both tail resolution (N >= 100) AND an explicit exchangeability specification accounting
    for session-reuse dependence, with exact p-value calculation:
    p = (1 + sum I(r_surr >= r_obs)) / (N + 1).

Rejection Tail Direction:
  Upper Tail: r_1_obs > theta_95(surrogate)

EXECUTION STATUS:
  RERUN = NOT YET AUTHORIZED
  C2 EXECUTION = BLOCKED UNDER TBD-Q2-04 (w_fb uncalibrated)
================================================================================
```

This ratification establishes a mathematically sound, coupling-sensitive bivariate statistic to replace the invalidated univariate turn-gap variance surrogate. No harness rerun is authorized by this document.

---

## 2. Research Question Formulation

The surrogate analysis for EXP-P25-Q2.1 must resolve a specific, bounded question:

> **Core Research Question (Domain B — Dyadic Coupling):**  
> *“Are the directional turn-taking latency streams between User and Lucia statistically coupled beyond what is expected from their independent marginal pacing distributions and common dialogue script structure?”*

This question is conceptually distinct from:
- **Domain A (Behavioral Outcome):** *“Did dyadic turn-gap variance or recovery duration decrease between conditions C0, C1, and C2?”*
- **Domain C (Directional Information Transfer):** *“Does past user timing improve non-linear prediction of Lucia timing via Transfer Entropy?”*

---

## 3. Comparative Evaluation of Candidate Statistics

| Candidate Statistic | Formal Definition | Metric Type | Coupling Sensitivity | Robustness at $K \le 20$ | Verdict |
|---|---|---|---|---|---|
| **Candidate A: Lag-1 Latency Cross-Correlation** | $r_1 = \text{Corr}(g_{UL}(k), g_{LU}(k-1))$ | Bivariate Correlation | **High** (direct tracking of partner's preceding latency) | **High** (tractable under non-parametric surrogate) | **RATIFIED AS PRIMARY** |
| **Candidate B: Cross-Stream Mutual Information** | $I(g_{UL}(k); g_{LU}(k-1))$ | Information-Theoretic | **High** (captures non-linear dependence) | **Fails** (severe finite-sample estimation bias at $K \approx 19$) | **REJECTED** |
| **Candidate C: Dyadic Tracking Error** | $\epsilon_{\text{track}} = \frac{1}{K}\sum \|g_{UL}(k) - g_{LU}(k-1)\|$ | Distance / Deviation | **Poor** (conflates synchrony with absolute latency equality) | High | **REJECTED** |
| **Candidate D: Bivariate Transfer Entropy Exceedance** | $\text{TE}(U \to L) - \text{TE}_{\text{surr}}$ | Directed Information Flow | **High** (asymmetric predictive flow) | Moderate (KSG calibrated) | **RETAINED AS SECONDARY (Domain C)** |

---

## 4. In-Depth Audit of Candidate A (Lag-1 Latency Cross-Correlation)

### 4.1 Causal Lag Alignment
Candidate A defines the correlation between Lucia's response latency at turn $k$ ($g_{UL}(k)$) and the user's response latency at the immediately preceding transition ($g_{LU}(k-1)$):

```text
Turn Timeline:
[Lucia Turn k-1] ──(g_LU(k-1))──> [User Turn k] ──(g_UL(k))──> [Lucia Turn k]
      │                                   │                               │
      └──────────── Partner stimulus ─────┴───── Adaptive response ───────┘
```

- **Temporal Order:** $T_{\text{onset}}(U_k) < T_{\text{offset}}(U_k) < T_{\text{onset}}(L_k)$.
- **Causality Guard:** The events defining $g_{LU}(k-1)$ occur before the event pair defining $g_{UL}(k)$, preserving the required temporal ordering. Future user data cannot leak backward into Lucia's state.
- **Sensitivity:** If Lucia dynamically adapts her pacing to the user's current conversational rhythm, $g_{UL}(k)$ will systematically track $g_{LU}(k-1)$.

### 4.2 Sign and Directional Interpretation
- **Positive Correlation ($r_1 > 0$):** Indicates **cadence entrainment / adaptive latency tracking**. When the user slows down (longer pause), Lucia slows down; when the user quickens responses, Lucia accelerates. This represents the primary behavioral signature of pacing coordination.
- **Negative Correlation ($r_1 < 0$):** Indicates compensatory or counter-phase pacing (e.g. rushing when the partner hesitates). While theoretically possible in human conflict or impatient turn-taking, it is antithetical to harmonious temporal embodiment in Lucia.
- **Absolute Value ($|r_1|$):** Using $|r_1|$ would collapse adaptive entrainment ($+r$) and antagonistic rushing ($-r$) into an ambiguous scalar. Therefore, **signed correlation $r_1$** is mandated.

### 4.3 Sensitivity to Small Sample Size ($K \le 20$)
In a 40-turn script with alternating speakers, there are $K = 20$ Lucia turns and $K = 20$ user turns, yielding $N = K - 1 = 19$ paired intervals $(g_{LU}(k-1), g_{UL}(k))$.
- **Analytical Parametric Tests (e.g. Student's $t$):** Invalid due to non-normality and serial autocorrelation.
- **Non-Parametric Surrogate Null:** The non-parametric cross-session surrogate distribution is constructed on the **exact same sample size ($N = 19$)**. Any small-sample variance inflation, skewness, or boundary constraints affect the surrogate distribution and empirical distribution identically, providing exact finite-sample level control without asymptotic assumptions.

### 4.4 Robustness to Outliers & Perturbation (Diagnostic Only)
Turn 18 introduces an intentional $+300\text{ ms}$ perturbation.
- To monitor whether this planned perturbation turn disproportionately affects linear correlation relative to monotonic rank ordering, the evaluation calculates both:
  1. **Primary Metric:** Pearson cross-correlation $r_1$ across all valid transitions.
  2. **Sensitivity Diagnostic:** Spearman rank cross-correlation $\rho_{\text{rank}} = \text{Corr}(\text{rank}(g_{UL}), \text{rank}(g_{LU}))$.
- **Epistemic & Governance Boundary:** If $|r_1 - \rho_{\text{rank}}| > 0.25$, the trial receives a `DISCREPANCY_FLAG` for sensitivity reporting. This threshold is a **diagnostic flag only; it does not alter the hypothesis decision**, nor does it function as an acceptance or rejection criterion. It serves solely to alert researchers to inspect whether linear variance is being driven by an isolated outlier turn.

---

## 5. Methodological Audit of Rejected Candidates (B & C)

### 5.1 Candidate B: Cross-Stream Mutual Information (Rejected)
- **Defect:** Non-parametric mutual information $I(X; Y) = \iint p(x,y)\log\frac{p(x,y)}{p(x)p(y)}dxdy$ requires estimating a 2D joint density.
- **Finite-Sample Breakdown:** On $N = 19$ paired points, KSG ($k=4$) neighbor counts have excessive variance ($\text{bias} \gg \text{effect size}$). Discrete binning into even $3 \times 3$ bins requires estimating 9 probability cells with 19 points ($< 2.2$ points/cell), producing severe finite-sample positive bias.
- **Pseudoreplication Trap:** Attempting to solve this by pooling turns across multiple sessions would violate the assumption of dyad independence, creating pseudo-replicated observations.
- **Conclusion:** Candidate B is **REJECTED** as a primary metric for short interaction episodes.

### 5.2 Candidate C: Dyadic Tracking Error (Rejected)
- **Defect:** $\epsilon_{\text{track}} = \frac{1}{K}\sum |g_{UL}(k) - g_{LU}(k-1)|$ measures the absolute distance between response latencies.
- **Theoretical Flaw:** Synchrony does **not** require latency equality ($g_{UL} = g_{LU}$). In human-machine communication, a user may naturally maintain a $600\text{ ms}$ cadence while Lucia operates at a nominal $350\text{ ms}$ baseline. If both vary their latencies in tight locked-step ($\Delta g_{UL} = \Delta g_{LU}$), they are perfectly coupled, yet $\epsilon_{\text{track}} \equiv 250\text{ ms} > 0$.
- **Conclusion:** Candidate C is **REJECTED** as a coupling statistic because it conflates synchrony (covariation) with isochrony (latency equality).

---

## 6. Scientific Role of Candidate D (Transfer Entropy)

Candidate D (Transfer Entropy) is **RETAINED** strictly within its assigned project role:
- **Domain Assignment:** Domain C — Directional Information Transfer.
- **Role:** Quantifies asymmetric predictive information flow:
  $$\text{TE}(U \to L) = I(g_{UL}(k); g_{LU}(k-1) \mid g_{UL}(k-1))$$
  $$\text{TE}(L \to U) = I(g_{LU}(k); g_{UL}(k) \mid g_{LU}(k-1))$$
  $$\Delta\text{TE}_{\text{net}} = \text{TE}(U \to L) - \text{TE}(L \to U)$$
- **Epistemic Invariant:** As established in project architecture, $\Delta\text{TE}_{\text{net}}$ is a **directional asymmetry diagnostic**. It is **not** a standalone reciprocity metric and cannot substitute for Domain B dyadic coupling.

---

## 7. Resolution of the Common-Script Confound

### 7.1 The Confound Mechanism
Because all sessions execute a standardized dialogue script (`FIXTURE-P25-Q2-SCRIPT-v0.1`), turn difficulty, syntactic complexity, and topic shifts vary deterministically across turn index $k$:
- Long, cognitively dense turns (e.g. Turn 15 architectural review) naturally induce longer response latencies in *both* speakers at that specific turn.
- A naive correlation across turn index $k$ would capture this **common script pacing**, showing positive correlation even if the two speakers completely ignore each other.

### 7.2 Why Matched Cross-Session Dyad Shuffling Controls This Confound
Cross-session dyad shuffling pairs Lucia's latency trajectory from Session $i$ with the User's latency trajectory from Session $j$ ($i \ne j$):
1. **Preserves Script Structure:** Both Session $i$ and Session $j$ experienced the exact same prompt at Turn $k$. Therefore, any correlation induced by script complexity at Turn $k$ is **fully present in the surrogate pairs**.
2. **Preserves Individual Dynamics:** Marginal distributions and intrinsic pacing rates of both interactants are preserved bit-exact.
3. **Destroys Closed-Loop Adaptation:** Because Session $i$ and Session $j$ were executed independently, Lucia in Session $i$ could not possibly have adapted to the live user in Session $j$.
4. **Tests Dyadic Exceedance Under Matched Script:** Evaluating $r_1^{\text{obs}}$ against the cross-session surrogate distribution **tests whether live dyad coupling exceeds the cross-session pseudo-synchrony null under the matched script**. It controls for shared script structure and individual marginal pacing, though intrinsic intra-session temporal structures may still exist. Therefore, exceeding the surrogate reference provides evidence against independent pacing under the matched script, without constituting a universal proof of genuine attunement.

---

## 8. Exact Null Hypothesis & Mathematical Formulation

### 8.1 Null Hypothesis ($\mathcal{H}_0$)
$$\mathcal{H}_0^{\text{coupling}}: \text{The observed lag-1 cross-correlation } r_1^{\text{obs}} \text{ between user reaction latency } \{g_{LU}(k-1)\} \text{ and Lucia reaction latency } \{g_{UL}(k)\} \text{ is fully explained by independent marginal pacing and shared script structure.}$$

### 8.2 Alternative Hypothesis ($\mathcal{H}_1$)
$$\mathcal{H}_1^{\text{coupling}}: \text{The observed lag-1 cross-correlation } r_1^{\text{obs}} \text{ significantly exceeds the upper 95th percentile of the cross-session surrogate distribution } (\theta_{95}^{\text{surr}}), \text{ demonstrating active dyadic temporal tracking.}$$

---

## 9. Mathematical Derivation of Tail Direction & Decision Logic

### 9.1 Metric Directionality
- **Statistic:** Pearson cross-correlation $r_1 \in [-1.0, +1.0]$.
- **Higher Values ($r_1 \to +1.0$):** Stronger positive temporal tracking (Lucia dynamically matches user cadence variations).
- **Lower Values ($r_1 \le 0.0$):** Absence of tracking, random independence, or anti-phase pacing.

### 9.2 Rejection Region, Reference Percentile & Level Control
Because active adaptive tracking corresponds to large positive correlation, the statistical test is **strictly upper-tailed**:
- **Null Statistic:** Empirical distribution of $r_1^{\text{surr}}$ generated across matched cross-session shuffled dyads.
- **Sample Size of Surrogates ($N$) & Level Control:**
  1. **5-Seed Baseline ($S = 5 \implies N = S(S-1) = 20$ realizations):** With only 20 surrogate realizations, the 95th percentile ($\theta_{95}^{\text{surr}}$) is an extreme boundary order statistic ($19\text{th}$ or $20\text{th}$ point). Under standard randomization inference, $N = 20$ does not provide sufficient resolution for a stable, formal $\alpha = 0.05$ hypothesis test. Therefore, in the 5-seed baseline, $\theta_{95}^{\text{ref}}$ is designated strictly as an **empirical reference distribution / exploratory threshold**, NOT a formal asymptotic $\alpha = 0.05$ hypothesis test.
  2. **Surrogate Realization Resolution ($N \ge 100$) vs Independent Samples:** Generating $N \ge 100$ surrogates resolves the **empirical tail resolution** (providing discrete granularity $1 / (N + 1) \le 0.01$). On edge CPU hardware, this is readily computed in $< 10\text{ ms}$ via:
     - Expanded ordered session generation ($S \ge 11 \implies S(S-1) \ge 110$ ordered cross-session pairings), OR
     - Hybrid circular-lag variants ($20\text{ cross-session pairs} \times 5\text{ circular lags} = 100\text{ realizations}$).
  3. **Methodological Dependence & Exchangeability Boundary:** Crucially, neither $S(S-1)$ cross-session pairings nor circular-lag variants constitute independent statistical samples; they are **dependent/reused-session surrogate realizations** (e.g. Session 1 is reused across pairings with Session 2, 3, etc.). While $N \ge 100$ resolves the discrete numerical resolution of the empirical upper tail, **$N \ge 100$ does NOT automatically guarantee formal permutation test validity**. A formal $\alpha = 0.05$ permutation test requires explicitly defining the exchangeable unit of randomization and formally establishing how session-reuse dependence is modeled or restricted.
- **Exact Permutation $p$-Value Calculation (When Exchangeability is Established):**
  $$p = \frac{1 + \sum_{m=1}^N \mathbb{I}(r_1^{\text{surr}}(m) \ge r_1^{\text{obs}})}{N + 1}$$
  $$\text{Rejection of } \mathcal{H}_0 \iff p < 0.05$$

---

## 10. Small-Sample Limitations & Methodological Safeguards

1. **Episode Length ($K = 20$, $N = 19$ paired intervals):** Evaluators must acknowledge that $N = 19$ paired points provide moderate statistical power. A non-significant result ($p \ge 0.05$ or $r_1 \le \theta_{95}^{\text{ref}}$) must be reported as **`NO EVIDENCE DETECTED UNDER TESTED CONDITIONS`**, not as proof of zero capacity for entrainment.
2. **Surrogate Realization Discipline vs Independent Samples:** The protocol explicitly prohibits equating an exploratory 20-surrogate reference with an $\alpha = 0.05$ level test. Furthermore, researchers must not conflate $N \ge 100$ surrogate realizations with 100 independent samples. Cross-session and circular-lag constructions reuse session time series, producing dependent realizations. Formal $\alpha = 0.05$ hypothesis testing requires both $N \ge 100$ realization resolution and a validated exchangeability scheme accounting for session reuse.
3. **Outlier Sensitivity Boundary:** As established in Section 4.4, the threshold $|r_1 - \rho_{\text{rank}}| > 0.25$ is a **diagnostic flag only; it does not alter the hypothesis decision**, nor does it function as an acceptance or rejection criterion.
4. **Deterministic Seed Requirement:** Every surrogate calculation must use deterministic master evaluation seeds to ensure exact bit-level reproducibility.
5. **No Pseudoreplication:** Under no circumstances may data from different seeds or episodes be pooled into a single oversized correlation vector without explicit hierarchical mixed-effects modeling.

---

## 11. Final Ratification Decision & Remaining TBDs

```text
================================================================================
FINAL RATIFICATION STATUS:

TBD-Q2-05: RATIFIED
- Primary Coupling Statistic: Lag-1 Latency Cross-Correlation r_1
- Tail Direction: Upper Tail (r_1_obs > theta_95 or exact p < 0.05)
- Surrogate Architecture:
  * 5-Seed Baseline: N=20 realizations -> Exploratory empirical reference distribution (theta_95_ref)
  * Formal Inference Resolution: N >= 100 surrogate realizations (resolves tail resolution; requires ratified exchangeability/dependence handling under session reuse)

REMAINING UNRESOLVED TBDs:
- TBD-Q2-04: Feedback gain vector w_fb (C2 remains strictly BLOCKED)
- Protocol Rerun Authorization: RERUN NOT AUTHORIZED
================================================================================
```

---

## 12. Governance & Boundary Verification

1. **Harness Execution:** Zero code was executed. No experiment was rerun.
2. **Production Code Diff:** `git diff -- src/ data/ electron/ config/` remains exactly EMPTY (0 lines altered).
3. **Genesis Onboarding Gate (INV-8):** `data/profile.json` preserved bit-exact (`{"is_onboarded": false}`).
4. **Architecture Gate:** LOCKED.
5. **Implementation Gate:** LOCKED.
6. **Phase 25 Horizon Status:** `PLANNED` (Temporal Embodiment & Social Feedback remains an active future horizon).
