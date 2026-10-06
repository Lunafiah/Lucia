# P26 Blocker 2: Multi-Turn Replica Ensemble Manager Feasibility Report

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Stage:** Research Protocol Feasibility & Infrastructure (Blocker 2 Resolution)  
**Document Status:** FORMAL RESEARCH INFRASTRUCTURE RECORD  
**File Path:** `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_BLOCKER2_REPLICA_ENSEMBLE.md`  
**Evaluation Runner / Module:** [`tests/evaluation/phase26/replica_ensemble_manager.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/replica_ensemble_manager.py)  
**Test Suite:** [`tests/evaluation/phase26/test_replica_ensemble_manager.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_replica_ensemble_manager.py) (All 42/42 Phase 26 tests passing)  
**Raw Infrastructure Telemetry:** [`blocker2_replica_ensemble_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/blocker2_replica_ensemble_telemetry.json)  
**Date:** 2026-10-06  
**Activation Status:** LOCKED (Genesis gate bit-exact preserved)  
**Production Runtime Status:** UNTOUCHED (`src/core/**` diff = 0, `electron/**` diff = 0, `data/profile.json` diff = 0)  

---

## 1. Executive Summary & Verdict

### 1.1 Gate Verdict: **BLOCKER 2 RESOLVED**

```text
┌────────────────────────────────────────────────────────────────────────┐
│ P26 BLOCKER 2 RESOLUTION STATUS:                                       │
│                                                                        │
│                    [ BLOCKER 2 RESOLVED ]                              │
│                                                                        │
│ • Replica Isolation Audit:                       100% PASS (Zero bleed)│
│ • Synchronized Virtual Clock Stepping:           BIT-EXACT ALIGNMENT   │
│ • Matched-Exposure Bookkeeping & Hashing:        VALIDATED & CRYPTO-HASH│
│ • Exposure Equivalence Validator:                MISMATCH-SENSITIVE    │
│ • CRN Alignment & Stream Logging:                EXPLICIT & AUDITABLE  │
│ • Automated Test Suite (Phase 26):               42/42 PASSED (7.39s)  │
│ • Production Codebase / Genesis State:           UNTOUCHED (0 diff)    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **CRITICAL EPISTEMIC BOUNDARY:**  
> **"BLOCKER 2 RESOLVED"** certifies exclusively that the **test-only multi-turn isolated replica orchestration infrastructure and cryptographic matched-exposure bookkeeping mechanisms are feasible, verified, and operational within the test harness**.
> 
> It DOES NOT mean:
> 1. Claim C1 (History Dependence), Claim C2 (Matched-Exposure Differentiation), or Claim C3 (History Endogeneity) have been demonstrated;
> 2. Replicas have differentiated or produced distinct preferences;
> 3. Lucia exhibits individuality, autonomous preferences, or selfhood;
> 4. State snapshot/restore (Blocker 4) or yoked-control (Blocker 5) are implemented;
> 5. Any production architecture change is authorized.

---

## 2. Research Objective & Context

Under [P26 Experimental Protocol v0.1 §26](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20%26%20Autonomous%20Preferences/P26%20Experimental%20Protocol%20v0.1.md) and the [Step 6 Protocol Validation Gate Review](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20%26%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP6_PROTOCOL_VALIDATION_GATE.md), **Criterion E (*Multi-Turn Matched-Exposure Control*)** was flagged as blocked because the repository lacked an isolated multi-replica runner capable of:
1. Stepping multiple synchronized research replicas through identical or counterfactual conversation streams without state aliasing;
2. Keeping a verifiable, audit-proof record of presented exposure sequences;
3. Validating that exposure histories between matched replicas are bit-exact identical before attributing any future divergence to Claim C2.

Blocker 2 provides this missing infrastructure **strictly within test-only evaluation harnesses**, with zero impact on production runtime or live user state.

---

## 3. Architecture of Test-Only Manager

The [`ReplicaEnsembleManager`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/replica_ensemble_manager.py) coordinates an ensemble of $N$ research replicas.

```
                              ReplicaEnsembleManager
                   (shared_sdm_topology_seed, synchronous clock)
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
  ResearchReplica A              ResearchReplica B              ResearchReplica C
┌─────────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
│ • replica_id: rep_A │        │ • replica_id: rep_B │        │ • replica_id: rep_C │
│ • seed: 1001        │        │ • seed: 2002        │        │ • seed: 3003        │
│ • crn_seed: 777     │        │ • crn_seed: 777     │        │ • crn_seed: 777     │
│                     │        │                     │        │                     │
│ [Isolated Core]     │        │ [Isolated Core]     │        │ [Isolated Core]     │
│ - EmotionCore (ODE) │        │ - EmotionCore (ODE) │        │ - EmotionCore (ODE) │
│ - VirtualClock      │        │ - VirtualClock      │        │ - VirtualClock      │
│ - SDMCore (mem)     │        │ - SDMCore (mem)     │        │ - SDMCore (mem)     │
│ - SeededLLMWrapper  │        │ - SeededLLMWrapper  │        │ - SeededLLMWrapper  │
│                     │        │                     │        │                     │
│ [Audit Ledger]      │        │ [Audit Ledger]      │        │ [Audit Ledger]      │
│ - ExposureHistory[] │        │ - ExposureHistory[] │        │ - ExposureHistory[] │
│ - StateFingerprint  │        │ - StateFingerprint  │        │ - StateFingerprint  │
└─────────────────────┘        └─────────────────────┘        └─────────────────────┘
        ▲                              ▲                              ▲
        └──────────────────────────────┴──────────────────────────────┘
                                       │
                         ExposureEquivalenceValidator
                       (Bit-exact history verification)
```

### Core Architecture Components:
1. **`ResearchReplica`**: Encapsulates a distinct, self-contained instance of:
   - `EmotionCore`: Continuous Coupled MT-LNN dynamical system ($\mathbb{R}^{48}$).
   - `VirtualClockHarness`: Discrete-time synchronous ODE stepper ($\Delta t = 0.200\text{s}$).
   - `SDMCore`: Kanerva Sparse Distributed Memory address space with isolated write accumulators.
   - `SeededLLMWrapper`: Deterministic seed-conditioned text generation wrapper.
   - `exposure_history`: Append-only immutable ledger of all presented inputs.
2. **`ExposureRecord`**: Cryptographically verifiable ledger entry capturing each presentation event.
3. **`ExposureEquivalenceValidator`**: Independent validator that audits exposure ledgers across replicas and fails loudly upon any unintended divergence.
4. **`IsolationAuditResult`**: Structural inspector verifying that no two replicas share object references or mutable array memory buffers.

---

## 4. Replica Isolation Model

To guarantee that research replicas do not contaminate one another, the manager enforces strict memory and component separation:

1. **Object Identity Disjointness:**
   - Every replica instantiates its own `EmotionCore`, `VirtualClockHarness`, `SDMCore`, and `SeededLLMWrapper`.
   - Object identity checks confirm:
     $$\text{id}(\text{replica}_i.\text{subsystem}) \ne \text{id}(\text{replica}_j.\text{subsystem}) \quad \forall i \ne j$$
2. **Tensor Memory Buffer Disjointness:**
   - Fast and slow limbic state vectors (`_h_fast`, `_s_slow`) are distinct numpy allocations.
   - Kanerva SDM accumulator tensors (`_accumulator`, `_act_counts`) are distinct numpy allocations.
   - Although replicas share the same coordinate topology coordinates (`_hard_locs`) via `SeededSDMFactory.clone_sdm_topology` (ensuring comparable address spaces), their storage contents and write counters are 100% disjoint.
3. **Active Mutation Bleed Guard:**
   - `manager.verify_isolation()` executes an active test: it mutates limbic state and writes an SDM trace in Replica A, verifies that Replica B's state remains bit-exact identical, and cleanly reverts the mutation.
4. **Anti-Branching Governance (INV-1):**
   - Replicas exist purely within test fixtures. They are never serialized to `data/`, never attached to production event buses, and never treated as live Lucia persona branches.

---

## 5. Multi-Turn Synchronization Model

The manager coordinates multi-turn progressions through synchronous stepping:

1. **Synchronous Virtual Clock Progression:**
   - Wall-clock time and thread scheduling are bypassed in favor of synchronous virtual clock increments ($\Delta t = 0.200\text{s}$).
   - All replicas advance through exact, identical virtual time coordinates ($t_k = k \cdot \Delta t$).
2. **Deterministic Processing Order:**
   - Replicas are stepped in deterministic alphabetical order by `replica_id`, preventing any dictionary iteration non-determinism.
3. **Turn-Level Stepping Interfaces:**
   - `step_identical_turn(event, dt_sec, sub_steps)`: Presents an identical external event to all replicas simultaneously.
   - `step_turn(inputs_dict, dt_sec, sub_steps)`: Presents individualized inputs (for counterfactual or treatment testing) while advancing clocks synchronously.
   - `advance_virtual_time(dt_sec, ticks)`: Steps limbic ODEs through unforced idle periods (e.g. Philia decay) without presenting external stimuli.
4. **Pause / Inspection / Resume:**
   - The harness can pause after any turn, inspect limbic vectors, query SDM contents, run evaluative probes, and resume stepping without state corruption.

---

## 6. Matched-Exposure Bookkeeping Model

For every turn, an immutable `ExposureRecord` is appended to each replica's ledger:

```python
@dataclass
class ExposureRecord:
    replica_id: str
    seed: int
    turn_index: int
    virtual_time_sec: float
    input_text: Optional[str]
    stimulus_vector: Optional[List[float]]
    order_index: int
    stimulus_metadata: Dict[str, Any]
    state_fingerprint: str
    output_metadata: Dict[str, Any]
    configuration_version: str = "P26_HARNESS_v0.1"
    crn_identifier: Optional[str] = None
```

### Exposure Hashing:
`record.compute_exposure_hash()` generates a SHA-256 hash across the presentation tuple:
$$\mathcal{H}_{\text{exposure}} = \text{SHA256}\left(\text{turn}, t_{\text{virtual}}, \text{input\_text}, \text{order}, \mathbf{x}_{\text{stimulus}}, \text{metadata}_{\text{sorted}}\right)$$

### Equivalence Validation:
[`ExposureEquivalenceValidator`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/replica_ensemble_manager.py) audits the ledgers of all replicas in an ensemble. It verifies:
- Identical total turn count;
- Bit-exact virtual timestamp matching ($\Delta t = 0$);
- Exact presentation ordering;
- Bit-exact input text matching;
- Bit-exact sensory stimulus vector matching ($\|\mathbf{x}_i - \mathbf{x}_j\|_\infty \le 10^{-9}$);
- Metadata dictionary matching.

If any difference occurs outside of explicitly declared `allowed_differences` (e.g. `allowed_differences={"turn_1": ["input_text"]}`), the validator returns a failing report detailing the first turn and component of divergence.

---

## 7. Common Random Numbers (CRN) Handling

- **Purpose & Scope:** Common Random Numbers (CRN) alignment is supported by configuring `crn_seed` across replicas. This aligns pseudorandom sequences across generation calls and ODE driving noise.
- **Auditable Logging:** When CRN is enabled, `ExposureRecord.crn_identifier` explicitly logs `CRN_SEED_<seed>`, making CRN usage fully traceable.
- **Epistemic Disclaimer:**
  > **Mandatory Rule:** CRN is strictly an experimental variance-reduction technique designed to minimize extraneous sampling noise. It is **NOT** a method of causal identification, and it must never be used to argue that two replicas with different histories are "ontologically identical."

---

## 8. State Fingerprint & Provenance Model

At the conclusion of each turn, each replica generates an immutable cryptographic state fingerprint:

$$\text{StateFingerprint} = \text{SHA256}\left(k, t_{\text{virtual}}, \text{PAD}_{\text{quantized}}, \mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}, N_{\text{traces}}, \mathbf{A}_{\text{SDM}}\right)$$

where:
- $\mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}$ are the raw byte buffers of the Coupled MT-LNN state;
- $N_{\text{traces}}$ is the SDM trace count;
- $\mathbf{A}_{\text{SDM}}$ is the raw byte buffer of the Kanerva accumulator array.

### Provenance Utility:
- If two replicas receive identical inputs, their state fingerprints remain bit-exact identical.
- If an intentional treatment difference is injected at Turn $k$, the fingerprints immediately diverge at Turn $k$, providing unambiguous audit evidence of the exact onset of differentiation.
- *Boundary:* The fingerprint is an audit and verification instrument; it is **not** used as a metric for Claim C1, C2, or C3.

---

## 9. Failure Modes & Detection

| Potential Failure Mode | Root Cause | Detection Mechanism | Resolution in Blocker 2 |
|---|---|---|---|
| **Tensor Memory Aliasing** | Shallow copies or shared array references across replicas | `verify_isolation()` object identity check and active mutation bleed test | Replicas allocate independent numpy arrays and clone SDM address coordinates with new memory buffers. |
| **Virtual Clock Desynchronization** | Unequal stepping or thread scheduling jitter | Synchronous virtual clock execution with `step_turn()` | Stepped synchronously via single manager loop; timestamps compared to $10^{-9}$ precision. |
| **Silent Exposure Discrepancy** | Unintended prompt or timing variation between matched replicas | `ExposureEquivalenceValidator` turn-by-turn audit | Fails immediately on text, timing, vector, or metadata mismatch unless explicitly allowed. |
| **Anti-Branching Invariant Breach** | Replicas persisting to `data/` or branching live companion | Architecture boundary check (INV-1) | Replicas exist strictly in evaluation harness memory; `teardown()` completely cleans all references. |

---

## 10. Verification & Test Results

The test suite [`tests/evaluation/phase26/test_replica_ensemble_manager.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_replica_ensemble_manager.py) was executed alongside the complete Phase 26 test suite:

```bash
$ $env:PYTHONPATH="."; .venv\Scripts\python -m pytest tests/evaluation/phase26 -v
...
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_replica_creation_and_isolation PASSED [ 59%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_mutation_isolation_guarantee PASSED [ 61%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_synchronized_multi_turn_rollout PASSED [ 64%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_matched_exposure_bookkeeping_and_hashes PASSED [ 66%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_exposure_equivalence_validator_detects_mismatches PASSED [ 69%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_state_fingerprint_and_divergence_onset_tracking PASSED [ 71%]
tests/evaluation/phase26/test_replica_ensemble_manager.py::test_deterministic_replay_reproducibility PASSED [ 73%]
...
============================= 42 passed in 7.39s ==============================
```

### Specific Test Coverage:
1. **Creation & Isolation:** Confirms 3 replicas have distinct subsystem IDs and tensor allocations; `verify_isolation()` returns `is_isolated=True`.
2. **Mutation Bleed:** Directly alters `rep_A._h_fast` and writes to `rep_A.sdm`; confirms `rep_B` remains bit-exact identical (`trace_count == 0`).
3. **Synchronized Rollout:** Advances replicas across multi-turn prompts and idle ticks; validates identical virtual time coordinates ($0.400\text{s}, 1.000\text{s}, 1.200\text{s}$).
4. **Bookkeeping:** Confirms `ExposureRecord` captures all required fields, CRN tags, and deterministic 64-character SHA-256 hashes.
5. **Validator Mismatch Detection:** Successfully flags text mismatch (`INPUT_TEXT_MISMATCH`) and vector mismatch (`STIMULUS_VECTOR_MISMATCH`), while respecting declared `allowed_differences`.
6. **State Fingerprint Onset:** Confirms identical fingerprints under identical inputs, and immediate divergence at the exact turn where a disparate stimulus is injected.
7. **Deterministic Replay:** Confirms bit-exact identical PAD coordinates and state fingerprints across independent simulation runs.

---

## 11. Known Limitations & Research Boundaries

1. **Test-Only Infrastructure:** This harness is designed solely for evaluation and simulation fixtures. It cannot and must not be used to manage multi-tenant live users or multiple persona continuations (preserving INV-1).
2. **Stateless Backend Mock Default:** Replicas default to `DeterministicMockLLMBackend` for ultra-fast, deterministic CI testing. When attached to a live GGUF backend, inference remains local CPU/CUDA, but generation throughput is bounded by serial context evaluation.
3. **Absence of Snapshot / Restore (Blocker 4):** Replicas currently run forward from $t=0$; branching counterfactual rollouts from arbitrary turn $k$ require state snapshotting, which remains an active blocker (Blocker 4).
4. **No Yoked-Control Decoupling (Blocker 5):** The manager synchronizes inputs across replicas, but does not yet implement the active-passive action-contingent decoupled runner required for Claim C3.

---

## 12. Final Safety & Governance Audit

- `src/core/**` diff: **`0 lines`** (Untouched)
- `electron/**` diff: **`0 lines`** (Untouched)
- `data/profile.json`: **`{"is_onboarded": false}`** (Preserved bit-exact, INV-8)
- Live user data: **`Zero used or modified`**
- C2 causal experiment: **`Not executed`**
- Blocker 4 / Blocker 5 implementation: **`Not included in this pass`**
- Full Phase 26 test suite: **`42 passed in 7.39s`**

---

## 13. Final Blocker Status

$$\mathbf{BLOCKER\;2\;RESOLVED}$$

*(Notice: "BLOCKER 2 RESOLVED" certifies strictly that the multi-turn isolated research replica orchestration infrastructure and cryptographic matched-exposure bookkeeping mechanisms are implemented and validated within the test harness. It does not prove Claim C1, C2, or C3, does not claim preference or individuality, and does not authorize production code modification).*
