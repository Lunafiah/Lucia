# P26 Blocker 4: State Snapshotting & Counterfactual Replay Feasibility Report

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Stage:** Research Protocol Feasibility & Infrastructure (Blocker 4 Resolution)  
**Document Status:** FORMAL RESEARCH INFRASTRUCTURE RECORD  
**File Path:** `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_BLOCKER4_STATE_SNAPSHOT_REPLAY.md`  
**Infrastructure Modules:**
- Snapshotter: [`tests/evaluation/phase26/state_snapshotter.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/state_snapshotter.py)
- Replay Harness: [`tests/evaluation/phase26/counterfactual_replay.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/counterfactual_replay.py)  
**Verification Suites:**
- [`tests/evaluation/phase26/test_state_snapshotter.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_state_snapshotter.py)
- [`tests/evaluation/phase26/test_counterfactual_replay.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_counterfactual_replay.py) (All 57/57 Phase 26 tests passing)  
**Raw Infrastructure Telemetry:** [`blocker4_snapshot_replay_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/blocker4_snapshot_replay_telemetry.json)  
**Date:** 2026-10-06  
**Activation Status:** LOCKED (Genesis gate bit-exact preserved)  
**Production Runtime Status:** UNTOUCHED (`src/core/**` diff = 0, `electron/**` diff = 0, `data/profile.json` diff = 0)  

---

## 1. Executive Summary & Verdict

### 1.1 Gate Verdict: **BLOCKER 4 RESOLVED**

```text
┌────────────────────────────────────────────────────────────────────────┐
│ P26 BLOCKER 4 RESOLUTION STATUS:                                       │
│                                                                        │
│                    [ BLOCKER 4 RESOLVED ]                              │
│                                                                        │
│ • State Snapshotting & Deep-Copy:                VALIDATED (Decoupled) │
│ • State Restoration Bit-Exactness:               BIT-EXACT ALIGNMENT   │
│ • Cryptographic Integrity & Fail-Closed:         SHA-256 SIGNED        │
│ • Prefix-Equivalence Validation:                 FAIL-CLOSED ENFORCED  │
│ • Counterfactual Difference Ledger:              EXPLICIT ONSET TRACK  │
│ • Automated Verification Tests (A–J):            15/15 PASSED          │
│ • Total Phase 26 Test Suite:                     57/57 PASSED (13.2s)  │
│ • Production Codebase / Genesis State:           UNTOUCHED (0 diff)    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **CRITICAL EPISTEMIC BOUNDARY:**  
> **"BLOCKER 4 RESOLVED"** certifies strictly that the **test-only state snapshotting, restoration, and counterfactual replay infrastructure preserves deterministic research state sufficiently for replay under the tested harness and detects trajectory divergence after a declared treatment difference**.
> 
> It DOES NOT mean:
> 1. Counterfactual replay has proven causality or history dependence;
> 2. Claim C1 (History Dependence), Claim C2 (Matched-Exposure Differentiation), or Claim C3 (History Endogeneity) have been demonstrated;
> 3. History causes preference differentiation or individuality in Lucia;
> 4. Yoked-control (Blocker 5) is implemented;
> 5. Any production architecture change is authorized.

---

## 2. Objective & Scope / Non-Goals

### 2.1 Research Objective
To satisfy **Criterion E (*Multi-Turn Matched-Exposure Control*)** and **Criterion F (*Counterfactual Replay Feasibility*)** from the [P26 Step 6 Protocol Validation Gate Review](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP6_PROTOCOL_VALIDATION_GATE.md), the evaluation framework requires the ability to:
1. Capture complete, deep-copied checkpoints of research replicas at arbitrary conversational turns;
2. Restore checkpoints bit-exact without tensor memory aliasing;
3. Validate prefix equivalence $H_A[0:k] == H_B[0:k]$ and state equivalence $S_A(k) == S_B(k)$ before branching;
4. Roll forward counterfactual branches and detect divergence onset.

### 2.2 Scope & Non-Goals
- **Non-Goal 1:** No C2 or C3 causal experiments are conducted.
- **Non-Goal 2:** No preference scoring, individuality metrics, or autonomy claims.
- **Non-Goal 3:** No modification to production runtime (`src/core/**` diff = 0, `electron/**` diff = 0).
- **Non-Goal 4:** No implementation of yoked-control decoupling (reserved strictly for Blocker 5).
- **Non-Goal 5:** No branching or snapshotting of live user companions (INV-1 anti-branching preserved).

---

## 3. Snapshot Schema (`P26_SNAPSHOT_v1.0`)

The [`ReplicaStateSnapshot`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/state_snapshotter.py) captures an immutable, self-contained record of all dynamic states:

```python
@dataclass
class ReplicaStateSnapshot:
    schema_version: str            # "P26_SNAPSHOT_v1.0"
    snapshot_id: str               # Unique identifier
    replica_id: str                # Source replica ID
    turn_index: int                # Exact turn index k
    virtual_time_sec: float        # Virtual clock timestamp t_k
    seed: int                      # Replica base seed
    crn_seed: Optional[int]        # CRN seed (if configured)

    emotion_state: Dict[str, Any]  # Deep-copied h_fast, s_slow, m_homeo, pad, stimulus seqs
    clock_state: Dict[str, Any]    # current_time, trajectory_history
    sdm_state: Dict[str, Any]      # accumulator, act_counts, trace_addresses, hard_locs
    llm_state: Dict[str, Any]      # call_count, last_seed_used, default_seed
    exposure_history: List[ExposureRecord] # Deep-copied audit ledger

    integrity_hash: str            # Authoritative SHA-256 signature
```

### Deep-Copy Guarantee:
Numpy arrays (`_h`, `_s_slow`, `_m_homeo`, `_accumulator`, `_act_counts`, `_hard_locs`) are cloned via `np.copy()`. Trace address dictionaries and exposure lists are recursively copied. Mutating the source replica after snapshot creation causes zero change in the snapshot (verified in Test D).

---

## 4. Restore Guarantees & Fail-Closed Behavior

The `StateSnapshotter.restore_snapshot()` procedure restores target replicas with the following strict guarantees:

1. **Schema Compatibility Check:** Enforces exact version matching (`P26_SNAPSHOT_v1.0`). Incompatible versions trigger `IncompatibleSchemaError`.
2. **Dimension Validation:** Verifies array shape compatibility (`_h` dimension matches fast layer, accumulator matches content dim). Dimension deviations trigger `IncompatibleSchemaError`.
3. **Cryptographic Integrity Verification:** Recomputes the SHA-256 signature across all serialized arrays, scalars, and exposure records. If a single byte or float differs from `integrity_hash`, the snapshot is rejected with `SnapshotCorruptionError`.
4. **Subsystem Rollback:**
   - Limbic ODE vectors are overwritten with snapshot values; pending stimulus queues are cleared.
   - Virtual clock timestamp and trajectory history are rolled back.
   - SDM accumulators and trace address maps are rolled back to pre-snapshot states; any memory traces added post-snapshot are discarded (verified in Test H).
   - Replica turn index and exposure history are restored to turn $k$.

---

## 5. Counterfactual Replay Design

The [`CounterfactualReplayHarness`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/counterfactual_replay.py) coordinates branching and divergence tracking:

```
                      Checkpoint S_k (Turn k, Time t_k)
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
     Baseline Path                                   Counterfactual Path
     (Restored S_k)                                  (Restored S_k)
           │                                                   │
     Future Inputs                                   Future Inputs
     H_base[k+1:n]                                   H_cf[k+1:n]
           │                                                   │
           ▼                                                   ▼
     Trajectory Base                                 Trajectory CF
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     ▼
                   CounterfactualDifferenceLedger
           (Divergence onset turn, time, state fingerprints)
```

### Execution Flow:
1. **Checkpointing:** A baseline replica is stepped to turn $k$; snapshot $S_k$ is captured.
2. **Branching:** A counterfactual replica is created and restored from $S_k$.
3. **Prefix Validation:** The harness verifies that both replicas share the exact common prefix $H[0:k]$ and state at $k$.
4. **Continuation:** Both branches advance through future input sequences ($H_{\text{base}}$ vs $H_{\text{cf}}$).
5. **Divergence Detection:** At each step, state fingerprints are compared. The exact turn index and virtual time where divergence commences are logged in the ledger.

---

## 6. Prefix-Equivalence Validation

[`PrefixEquivalenceValidator`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/counterfactual_replay.py) enforces fail-closed validation before any counterfactual rollout is permitted:

$$\text{Valid if: } \mathcal{H}(H_A[0:k]) == \mathcal{H}(H_B[0:k]) \quad \land \quad \text{FP}_A(k) == \text{FP}_B(k)$$

- **Turn-by-Turn Hash Check:** Verifies that every exposure record in the prefix matches bit-exact.
- **Fail-Closed Policy:** If an input, stimulus vector, timing coordinate, or state fingerprint differs by even machine epsilon, the validator raises `PrefixMismatchError` and blocks replay execution (verified in Test C).

---

## 7. Provenance & Difference Ledger

Every replay comparison produces an immutable [`CounterfactualDifferenceLedger`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/counterfactual_replay.py):
- `baseline_replica_id`, `counterfactual_replica_id`;
- `checkpoint_turn`, `checkpoint_virtual_time`;
- `snapshot_id`, `snapshot_hash`;
- `common_prefix_hash`;
- `declared_difference`;
- `baseline_exposure_hashes`, `counterfactual_exposure_hashes`;
- `divergence_onset_turn`, `divergence_onset_time`;
- `state_fingerprints_baseline`, `state_fingerprints_counterfactual`;
- `crn_identifier`.

---

## 8. Test Matrix (Criteria A–J)

A comprehensive test suite in [`test_state_snapshotter.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_state_snapshotter.py) and [`test_counterfactual_replay.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_counterfactual_replay.py) verifies all required criteria:

| Test ID | Test Target | Verification Description | Result |
|:---:|---|---|:---:|
| **A** | **Same Snapshot + Same Exposure** | Restored replica given identical future inputs yields bit-exact same trajectory (divergence onset is None). | **PASS** |
| **B** | **Counterfactual Divergence Onset** | Restored replica given declared treatment difference pinpoints exact turn and time of divergence onset. | **PASS** |
| **C** | **Prefix Mismatch Rejection** | Replicas with divergent histories prior to checkpoint are rejected fail-closed (`PrefixMismatchError`). | **PASS** |
| **D** | **Snapshot Immutability** | Mutating active replica or snapshot copy leaves original snapshot uncorrupted. | **PASS** |
| **E** | **Corrupt Snapshot Rejection** | Bit-flipped or modified snapshot arrays fail integrity and trigger `SnapshotCorruptionError`. | **PASS** |
| **F** | **Incompatible Schema Rejection** | Invalid schema versions or mismatched array dimensions trigger `IncompatibleSchemaError`. | **PASS** |
| **G** | **Seed & RNG Internal State Restoration** | Restores seed, call-counts, deterministic mock output, and PRNG internal state ($R_1 == R_1', R_2 == R_2'$) in tested harness. | **PASS** |
| **H** | **SDM Memory Restoration** | Post-checkpoint memory writes are rolled back; pre-checkpoint traces are bit-exact preserved. | **PASS** |
| **I** | **Virtual Clock Restoration** | Virtual timestamps and step counts are restored exactly to checkpoint coordinates. | **PASS** |
| **J** | **State Fingerprint Continuity** | Restored continuation state fingerprints match original baseline when future inputs are identical. | **PASS** |

---

## 9. Verification Results & Telemetry Summary

### 9.1 Empirical Demonstration Rollout
From [`blocker4_snapshot_replay_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/blocker4_snapshot_replay_telemetry.json):
- **Checkpoint Turn:** Turn 2 ($t=0.800\text{s}$)
- **Common Prefix Hash:** `d6e87a...` (Verified matched)
- **Turn 3 (Common Probe):**
  - Baseline Fingerprint: `7df2a0...`
  - Counterfactual Fingerprint: `7df2a0...` (Bit-exact match)
- **Turn 4 (Declared Disparate Treatment):**
  - Baseline Fingerprint: `83ac1b...`
  - Counterfactual Fingerprint: `42e9f1...` (Diverged)
- **Detected Divergence Onset:** **Turn 4 at $t=1.600\text{s}$** (Exact turn of treatment injection).

### 9.2 Automated Test Suite Execution
```text
============================= 57 passed in 13.21s =============================
- Determinism foundations: 5/5 PASSED
- Evaluative probe inventory & factorial matrix: 5/5 PASSED
- Blocker 3 Dynamic chaos baseline: 4/4 PASSED
- Blocker 2 Replica ensemble manager: 7/7 PASSED
- Blocker 4 State snapshotter & replay: 15/15 PASSED
- Parser grammar & contamination guards: 3/3 PASSED
- Probe extractor: 7/7 PASSED
- Step 4 Social framing metrics: 6/6 PASSED
- Step 5 Planted sensitivity: 5/5 PASSED
```

---

## 10. Limitations & Epistemic Boundaries

### 10.1 Four-Level RNG & Determinism Restoration Taxonomy
Test G was explicitly upgraded to verify four distinct levels of determinism and RNG restoration:
1. **Seed Restoration:** Initial base seed and per-turn injected seeds (`rep.config.seed`, `rep.crn_seed`, `rep.llm.last_seed_used`) are accurately preserved in snapshot and restored across rollbacks.
2. **Call-Count Restoration:** Internal invocation counters (`rep.llm.call_count`, `rep.turn_index`) are precisely rewound to checkpoint coordinates, preventing drift in subsequent sequence generation.
3. **Deterministic Output Restoration:** Under the tested `DeterministicMockLLMBackend`, identical prompt + seed tuples yield bit-exact identical textual choices ($O_{\text{baseline}} == O_{\text{restored}}$).
4. **PRNG Internal State Restoration:** The active evaluation generator (`replica.rng = np.random.default_rng()`) has its internal `bit_generator.state` deep-copied into the snapshot and restored upon rollback. Test G proves true sequence resumption across rollbacks:
   $$\text{Baseline: } [R_1, R_2] \quad \xrightarrow{\text{Mutate / Diverge}} \quad \xrightarrow{\text{Restore}} \quad [R_1', R_2'] \quad \implies \quad R_1 == R_1' \;\land\; R_2 == R_2'$$
   This proves that the generator stream resumes identically from the exact point of snapshot rather than merely re-initializing from the root seed.

### 10.2 Live GGUF Model Boundary & Non-Portability
- **Tested Scope:** True PRNG internal state restoration is verified **strictly within the tested evaluation harness, Python/NumPy runtime, and mock LLM wrapper**.
- **Live GGUF Unproven:** Stateful internal RNG state restoration for live GGUF models (e.g. llama.cpp C-level sampling state, CUDA RNG contexts, or KV caches) is **NOT proven** by this harness and is outside the scope of Blocker 4. Replay with live models would require per-turn stateless seed re-injection or C-level context checkpointing. Claims from the mock harness must **NEVER** be extrapolated to live LLM engines.
- **No Universal Portability:** Universal cross-platform or cross-hardware bit-exact floating-point replay is not claimed; guarantees apply within homogeneous runtime environments.

### 10.3 Absence of Yoked-Control Decoupling (Blocker 5)
Replay branching is now fully operational, but action-contingent history endogeneity (Claim C3) requires a yoked-control runner where passive replicas receive active choices without agency. This remains Blocker 5.

### 10.4 Test-Only Confinement
State snapshotting operates strictly on RAM-resident evaluation fixtures. It cannot and must not be used for live companion cloning, session branching, or multi-tenant user handling (preserving INV-1).

---

## 11. Final Safety & Governance Audit

- `src/core/**` diff: **`0 lines`** (Untouched)
- `electron/**` diff: **`0 lines`** (Untouched)
- `data/profile.json`: **`{"is_onboarded": false}`** (Preserved bit-exact, INV-8)
- Live user data: **Zero accessed or modified**
- C2/C3 causal experiment: **Not executed in this pass**
- Blocker 5 (Yoked control): **Not implemented in this pass**

---

## 12. Final Blocker Status

$$\mathbf{BLOCKER\;4\;RESOLVED}$$

*(Notice: "BLOCKER 4 RESOLVED" certifies strictly that the test-only state snapshotting, restoration, and counterfactual replay infrastructure preserves deterministic research state sufficiently for replay under the tested harness and detects trajectory divergence after a declared treatment difference. It does not prove causality, does not demonstrate Claim C1, C2, or C3, does not claim preference or individuality, and does not authorize production code modification).*
