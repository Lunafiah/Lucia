# P26 Step 1 & Step 2 Implementation Report: Evaluative Probe Freeze & Determinism Foundations

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Stage:** Research Protocol Pre-Validation (Steps 1 & 2)  
**Document Status:** FROZEN / VALIDATED (Evaluation Harness Prototype)  
**Report Path:** `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP1_STEP2_FOUNDATIONS.md`  
**Test Suite Anchor:** [`tests/evaluation/phase26/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/) (17/17 tests passing)  
**Date:** 2026-10-06  
**Activation Status:** LOCKED (INV-8 Preserved)  
**Production Runtime Status:** UNTOUCHED (`src/core/**` diff = 0, `data/**` diff = 0)  

---

## 1. Executive Summary & Verdict

### 1.1 Executive Verdict

| Evaluation Dimension | Verdict | Rationale |
|---|---|---|
| **Step 1: Evaluative Probe Freeze** | **FROZEN & VERIFIED** | The 4-probe canonical battery across 2 domains (`INFO_FORAGING`, `TASK_STRATEGY`) and the 144-cell factorial design matrix are formally specified, implemented, and verified in code. Zero natural-language explanation is used as preference evidence. |
| **Step 2: Determinism Foundations** | **IMPLEMENTED & VERIFIED** | `SeededSDMFactory`, `VirtualClockHarness`, `SeededLLMWrapper`, and `ReproducibilityEvaluator` pass 17/17 unit and integration tests. Residual stochasticity is quantified at zero drift for memory, floating-point epsilon ($< 10^{-12}$) for affective dynamics, and 100% string match for seed-controlled generation. |
| **Readiness for Step 3 (Substrate Baseline)** | **READY FOR STEP 3** | The measurement instrument is now sufficiently clean, deterministic, and isolated to begin empirical characterization of substrate priors and positional order bias floors. |
| **Readiness for Causal Emergence Experiment** | **BLOCKED** | Governed strictly by Protocol §26 and §32. No causal experiment or claim of emergence is authorized. |

---

## 2. Step 1: Evaluative Probe Freeze Status

The probe matrix is frozen in [`tests/evaluation/phase26/probes/inventory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/probes/inventory.py) and documented in [`P26_EVALUATIVE_PROBE_SPEC_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_EVALUATIVE_PROBE_SPEC_v0.1.md).

### 2.1 The 4 Canonical Frozen Probes

```text
Domain 1: INFORMATION_FORAGING (Archival & Research Inquiry Dilemmas)
├── P26-FORAGE-01 (ACTIVE / CORE)
│   ├── Option A : Deep-sea hydrothermal ecosystems
│   └── Option B : Medieval maritime cartography
└── P26-FORAGE-02 (HELD-OUT — Generalization & Plasticity Reserve)
    ├── Option A : Superconducting qubit topologies
    └── Option B : Mechanisms of cellular senescence

Domain 2: TASK_STRATEGY (Methodological & Architectural Prioritization Dilemmas)
├── P26-STRAT-01 (ACTIVE / CORE)
│   ├── Option A : Exhaustive formal verification
│   └── Option B : Rapid empirical prototyping
└── P26-STRAT-02 (HELD-OUT — Cross-Domain Reserve)
    ├── Option A : Modular interface decoupling
    └── Option B : Unified single-pass optimization
```

### 2.2 Factorial Design Structure

Each probe is instantiated across 3 orthogonal axes, yielding exactly **144 factorial evaluation cells**:

$$\mathcal{M} = 4 \text{ Probes} \times 2 \text{ Presentation Orders} \times 3 \text{ Phrasing Variants} \times 6 \text{ Social Conditions} = 144 \text{ Cells}$$

* **Presentation Orders (2):** `A_THEN_B` vs `B_THEN_A` (eliminates linear primacy/recency bias).
* **Phrasing Variants (3):** `STANDARD` (conversational), `MINIMAL` (direct forced choice), `OPERATIONAL` (system directive).
* **Social Conditions (6):** `NEUTRAL`, `A_FAVORING`, `B_FAVORING`, `USER_PREFERS_A`, `USER_PREFERS_B`, `USER_ABSENT`.

### 2.3 Strict Epistemic Governance Rules
1. **Explanation Exclusion:** Natural-language justifications generated after the choice clause are captured strictly as text length/entropy covariates. They are **never** evaluated as evidence of an internal preference.
2. **No Latent Preference Scoring:** The harness records categorical choices $c \in \{\text{OPTION\_A}, \text{OPTION\_B}, \text{INDIFFERENT}, \text{REFUSAL}, \text{PARSE\_FAILED}\}$ and empirical frequencies $P(A)$. No speculative latent trait or preference scalar is constructed.
3. **No Premature Labeling:** Behavioral differences are documented as empirical path divergence; they are not labeled as "individuality".
4. **No Premature Thresholds:** Decision margins, settling thresholds ($||PAD - PAD^*||$), and sycophancy boundaries ($S_{\text{syc}}$) are declared as:
   ```text
   THRESHOLD_STATUS = EXPERIMENT_SPECIFIC / NOT_YET_DEFINED
   ```

---

## 3. Degrees-of-Freedom Inventory

To prevent researcher degrees of freedom (p-hacking / prompt adjustments):

| Dimension | Degree of Freedom State | Control Implementation |
|---|---|---|
| **Probe Phrasing** | **FROZEN** (12 templates total) | Stored as immutable constants in `CANONICAL_PROBES`. |
| **Option Labels** | **FROZEN** (Exact string literals) | Pre-registered in `inventory.py`. |
| **Choice Extraction** | **FROZEN** (Rule-based Regex) | `DeterministicChoiceExtractor` in `probe_models.py`. |
| **INV-2 Defect Check** | **FROZEN** (Banned ego regex) | Flags `contains_self_report = True` if introspective ego phrases appear. |
| **Evaluation Mode** | **FROZEN** (Read-Only) | Non-storage mode: probe turns do not write to SDM or KnowledgeStore. |

---

## 4. Step 2: Determinism Foundations Implementation Summary

Four isolated evaluation modules were constructed under `tests/evaluation/phase26/determinism/` to eliminate runtime stochasticity without touching production code:

### 4.1 `SeededSDMFactory`
* **File:** [`tests/evaluation/phase26/determinism/seeded_sdm_factory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/determinism/seeded_sdm_factory.py)
* **Problem Solved:** `src/core/memory/sdm.py` line 85 uses `rng = np.random.default_rng()` without a seed parameter, causing independent replicas to initialize differing hyper-planes.
* **Mechanism:** The factory re-seeds `_hard_locs` using `np.random.default_rng(seed)` or clones the coordinates of an existing SDM topology into clean replica instances.
* **Result:** Guaranteed bit-exact address space replication across matched replicas.

### 4.2 `VirtualClockHarness`
* **File:** [`tests/evaluation/phase26/determinism/virtual_clock_harness.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/determinism/virtual_clock_harness.py)
* **Problem Solved:** `EmotionCore`'s background thread executes ODE steps using wall-clock `time.monotonic()`, introducing timer jitter and thread scheduling variance.
* **Mechanism:** Leaves the background thread stopped (`core.start()` is never called) and drives the Coupled MT-LNN synchronously via `core.step_once(custom_timestamp=t_sim)` with a constant virtual step ($\Delta t = 0.200\text{s}$).
* **Result:** Complete elimination of thread jitter; bit-exact identical PAD trajectory evolution.

### 4.3 `SeededLLMWrapper`
* **File:** [`tests/evaluation/phase26/determinism/seeded_llm_wrapper.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/determinism/seeded_llm_wrapper.py)
* **Problem Solved:** `LLMBackend.generate()` does not expose a `seed` argument to callers.
* **Mechanism:** Wraps the underlying backend to pass `seed=effective_seed` directly to low-level `llama_cpp.__call__()` or deterministic evaluation simulators. Tracks call counts and seeds used.
* **Result:** Full seed control for Common Random Numbers (CRN) paired counterfactual replay.

### 4.4 `ReproducibilityEvaluator`
* **File:** [`tests/evaluation/phase26/determinism/reproducibility_evaluator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/determinism/reproducibility_evaluator.py)
* **Function:** Audits and quantifies residual stochasticity across memory, limbic dynamics, and LLM text generation.

---

## 5. Determinism & Reproducibility Audit Results

The reproducibility audit was executed via automated test suite [`test_determinism_foundations.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/determinism/test_determinism_foundations.py).

### 5.1 Subsystem Measurement Matrix

| Subsystem | Test Condition | Metric Measured | Measured Result | Verdict |
|---|---|---|---|---|
| **Kanerva SDM** | 2 replicas, identical seed (`seed=1234`), 20 random address probes | Hard location bit-equality & Activation mismatch rate | Bit-exact: `True`<br>Activation error: `0.000` | **PASS (BIT-EXACT)** |
| **Coupled MT-LNN** | 2 replicas, 30 steps identical stimulus, Virtual Clock ($\Delta t = 0.200$) | Max Euclidean PAD divergence ($\max \|PAD_1(t) - PAD_2(t)\|_2$) | Divergence: `0.000e+00` ($< 10^{-12}$) | **PASS (BIT-EXACT)** |
| **Philia Settling** | Convergence from perturbed state to resting attractor | Step count & final distance match | Step match: Identical<br>Dist diff: `< 10^{-12}` | **PASS (BIT-EXACT)** |
| **LLM Generation** | 10 evaluations, fixed seed (`seed=42`), identical prompt | Exact string match rate | String match: `100.0%` | **PASS (DETERMINISTIC)** |

### 5.2 Test Suite Execution Summary
* **Command:** `.venv\Scripts\python.exe -m pytest tests/evaluation/phase26/`
* **Results:** **17 passed in 16.63s**
  - `tests/evaluation/phase26/determinism/test_determinism_foundations.py`: 5 passed
  - `tests/evaluation/phase26/probes/test_probe_inventory.py`: 5 passed
  - `tests/evaluation/phase26/test_probe_extractor.py`: 7 passed

---

## 6. Analysis of Residual Stochasticity

While harness-level determinism is now established, the audit identifies where residual stochasticity can still arise during subsequent research stages:

1. **GPU Floating-Point Non-Associativity (CUDA cuBLAS):**
   - *Nature:* Parallel floating-point matrix multiplications across GPU warps are non-associative: $(a + b) + c \ne a + (b + c)$.
   - *Impact on Lucia:* At $T > 0$, slight logit variations at the 7th decimal place can occasionally flip token selection if two options have identical logits.
   - *Harness Mitigation:* Use greedy sampling ($T = 0.0$) as the primary deterministic baseline, and run repeated measures ($N \ge 30$) when sampling at $T > 0$.
2. **ODE RK45 Step Interpolation:**
   - *Nature:* Numerical integration with `scipy.integrate.solve_ivp(method="RK45")` produces identical results on the same CPU architecture, but can exhibit minor floating-point differences ($< 10^{-10}$) across different OS/CPU architectures (e.g. Windows x86_64 vs Linux ARM).
   - *Harness Mitigation:* All replica comparisons within an experimental trial must run on the exact same host node.

---

## 7. Known Limitations & New Blockers

### Known Limitations
1. **Probe Domain Specialization:** The 4 probes represent two domains (`INFO_FORAGING` and `TASK_STRATEGY`). They do not cover open-ended artistic, emotional, or social domain choices.
2. **Categorical Extraction Coverage:** The rule-based regex parser requires unambiguous selection phrases. Approximately $5\text{--}10\%$ of complex, rambling responses may trigger `PARSE_FAILED`.

### New Blockers
* **None for Step 3.** All foundational infrastructure required for Step 3 (Substrate Baseline & Positional Order Bias Measurement) is in place and verified.
* **Blocker for Full Causal Experiment Remains Active:** Steps 3, 4, 5, and 6 must be completed before the protocol validation gate can be reviewed.

---

## 8. Recommendations & Next Steps

### Recommendation: **READY FOR STEP 3**
The experimental apparatus is now clean, reproducible, and verifiable. The project is cleared to proceed to **Step 3 — Substrate Baseline & Positional Order Bias Measurement**.

### Recommended Action in Step 3:
1. Run unconditioned research replicas ($t = 0$, zero memory, resting Philia) across all 144 factorial probe cells ($N = 30$ trials per cell).
2. Quantify baseline option prior $\Delta_{\text{substrate}}$ and empirical positional order bias floor $\mathcal{B}_{\text{order}}$.
3. Record raw results in persistent evaluation artifacts without asserting any emergence.

---

## 9. Governance & Invariant Compliance Statement

1. **Zero Production Mutation:** `src/core/**`, `src/api/**`, `electron/**`, and `config/**` have zero modifications (`git status` diff = 0).
2. **Genesis Onboarding Invariant (INV-8):** `data/profile.json` remains untouched with `{"is_onboarded": false}`.
3. **No Preference / Individuality Mechanism:** Zero preference scoring, ego reflection, or individuality engines were implemented.
4. **No Causal P26 Experiment:** No causal history manipulations or emergence claims were made.
5. **Phase Containment Rule:** All code is strictly localized under `tests/evaluation/phase26/` and all documentation under `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/`.
