# F-02 Implementation Scope & Acceptance Gates Specification

**Document ID:** `SPEC-SCOPE-F02-20261007`  
**Classification:** Engineering Implementation Blueprint (Pending Authorization)  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`FINAL_RATIFICATION_PACKAGE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_FINAL_RATIFICATION/FINAL_RATIFICATION_PACKAGE.md)  

---

## 1. Governance Boundary

> [!CAUTION]
> **IMPLEMENTATION IS CURRENTLY NOT AUTHORIZED.**  
> This document defines the exact technical scope, file modification plans, and verification gates to be executed **only after Human Owner approval of Decisions D-01, D-02, and D-03**.

---

## 2. Authorized Remediation Scope (10 Work Packages)

Upon formal Owner authorization, implementation shall execute the following 10 work packages:

### WP-01: Startup Dependency Inversion (`cognitive_orchestrator.py`)
- **Action:** Invert component instantiation order in `build_cognitive_orchestrator()`.
- **Target File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)
- **Detail:** Construct `RelationshipUpdater` before `EmotionCore`. Instantiate `EmotionCore` with `auto_restore=False`. Call `emotion_core.update_relationship_context(rel_state)` prior to calling `emotion_core.restore_from_checkpoint()`.

### WP-02: Relational Attractor Coupling at Boot
- **Action:** Ensure `EmotionCore._R_t` is set to the loaded mature relational vector prior to any elapsed physical time ODE integration.
- **Detail:** Completely eliminates finding **E-01/E-02/E-03** (startup attractor desynchronization).

### WP-03: Two-Stage Hybrid Downtime Recovery (`emotion_core.py`)
- **Action:** Replace unbounded forward Euler loop in `EmotionCore.integrate_unforced_idle()` with the ratified two-stage hybrid recovery model.
- **Target File:** [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py)
- **Detail:** For $\Delta t \le \tau_{\text{candidate}} = 180\text{s}$, step Euler loop (max 900 steps). For $180\text{s} < \Delta t < 300\text{s}$, apply exponential asymptotic decay toward $s^*_{\text{eff}}(R_t)$. For $\Delta t \ge 300\text{s}$, evaluate direct $O(1)$ projection.

### WP-04: Commit Barrier & Consistency Detection Mechanism (`persistence.py`)
- **Action:** Implement `data/epoch_manifest.json` recording `{"epoch_id": int, "t_checkpoint": float, "status": "committed"}`.
- **Target File:** [`src/core/emotion/persistence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/persistence.py)
- **Detail:** Atomic write sequence in Stage 16 commits domain stores first, followed by the manifest commit barrier.

### WP-05: Deterministic Crash Recovery Protocol
- **Action:** Implement consistency verification in `restore_from_checkpoint()`.
- **Detail:** If `relationship.json` or `dynamical_state.json` contains an uncommitted epoch relative to `epoch_manifest.json`, automatically rollback the uncommitted store using its `.bak` file, ensuring causal synchronization.

### WP-06: Derived PAD Reprojection on Startup
- **Action:** Ensure `EmotionCore` reprojects PAD coordinates on boot via `_project_to_pad(h, s)` rather than loading serialized PAD as an authoritative input.
- **Detail:** Eliminates duplicate sources of truth.

### WP-07: Dialogue Working Memory Reseeding
- **Action:** Reseed `CognitiveOrchestrator._history` from the trailing $K$ turns of `data/chat_history.json`.
- **Target File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)
- **Detail:** $K$ shall be exposed as an implementation configuration parameter (`context_history_turns`, default 10), preserving prompt continuity across cold restarts.

### WP-08: Bit-Exact Genesis Invariant Guard
- **Action:** Assert that `data/profile.json` remains strictly bit-exact `{"is_onboarded": false}` across all tests and recovery routines.
- **Detail:** Upholds INV-8.

### WP-09: Automated Multi-Store Crash Consistency Test Suite
- **Action:** Create automated integration tests simulating process kill (`taskkill /F`) between Stage 16.3 and Stage 16.5.
- **Target File:** [`tests/integration/test_f02_dynamical_persistence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/integration/test_f02_dynamical_persistence.py)
- **Detail:** Verify that the system automatically detects partial writes and recovers to the last coherent logical epoch.

### WP-10: Extended Downtime Latency & Equivalence Tests
- **Action:** Add integration tests for long downtime recovery across simulated offline intervals: 1 minute, 1 hour, 1 day, 1 month, and 1 year.
- **Target File:** [`tests/integration/test_f02_dynamical_persistence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/integration/test_f02_dynamical_persistence.py)
- **Detail:** Verify startup latency remains strictly $\le 5.0\,\text{ms}$ and slow tensor converges bit-exact to $s^*_{\text{eff}}(R_t)$.

---

## 3. Mandatory Acceptance Gates

| Gate ID | Gate Title | Verification Criterion | Automated Test |
|---|---|---|---|
| **GATE-F02-1** | **Attractor Synchrony** | On cold boot with $R \ne R_0$, $s_{\text{slow}}$ relaxes strictly toward $s^*_{\text{eff}}(R)$, not $s_{\text{philia}}$. | `test_cold_boot_relational_attractor_synchrony` |
| **GATE-F02-2** | **Startup Latency Bound** | Cold boot recovery latency $\le 5.0\,\text{ms}$ on CPU for $\Delta t = 10^7\,\text{s}$ ($>3\text{ months}$). | `test_long_downtime_recovery_latency_bound` |
| **GATE-F02-3** | **Causal Crash Consistency** | Process crash between Stage 16.3 and 16.5 rolls back cleanly; zero cross-subsystem epoch tears. | `test_multistore_commit_barrier_crash_recovery` |
| **GATE-F02-4** | **Working Memory Reseed** | Cold restart populates `_history` with trailing $K$ turns; prompt assembly contains dialogue context. | `test_orchestrator_history_reseeding` |
| **GATE-F02-5** | **Genesis Gate Bit-Exactness**| SHA-256 hash of `data/profile.json` matches pre-implementation baseline bit-exact. | `test_genesis_invariant_remains_bit_exact` |
