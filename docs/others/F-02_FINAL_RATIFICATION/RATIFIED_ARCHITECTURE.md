# Ratified Architecture Blueprint: Option D/F Two-Tier Persistent Life State (F-02)

**Document ID:** `ARCH-BLUEPRINT-F02-20261007`  
**Classification:** Canonical Architecture Blueprint (Pending Ratification)  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`FINAL_RATIFICATION_PACKAGE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_FINAL_RATIFICATION/FINAL_RATIFICATION_PACKAGE.md)  

---

## 1. Architectural Philosophy: Decoupled Two-Tier Life State

The core design principle of Option D/F is the separation of **authoritative interpersonal/identity invariants** from **continuous physical-time dynamical evolution**.

Rather than forcing the entire cognitive architecture into an unmaintainable monolithic state file, Option D/F defines two cleanly decoupled tiers linked by a lightweight **Commit Barrier**:

```
                                 LUCIA PERSISTENT LIFE STATE
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ TIER 1: AUTHORITATIVE PERSISTENT STATE                                                 │
 │ (Invariants, Identity & Cumulative Social History - Must Survive Cold Restart)         │
 │                                                                                        │
 │  • Genesis Profile Gate:    data/profile.json (Bit-exact {"is_onboarded": false})      │
 │  • Relational Vector & Log: data/relationship.json (R_t in [0,1]^4, update history)     │
 │  • Autobiographical Log:    data/chat_history.json (Complete conversational transcript)│
 │  • Dynamical Checkpoint:    data/dynamical_state.json (h_fast, s_slow, created_at)     │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                              SYNCHRONIZED COMMIT BARRIER
                               data/epoch_manifest.json
                                             │
 ┌───────────────────────────────────────────▼────────────────────────────────────────────┐
 │ TIER 2: RECONSTRUCTIBLE DYNAMICAL & METABOLIC STATE                                    │
 │ (Recovered via Continuous Physical-Time Evolution Across Offline Downtime Delta t)     │
 │                                                                                        │
 │  • Fast Reactive State:     Decays toward 0 across short downtime                      │
 │  • Slow Latent Field:       Relaxes toward relationally conditioned attractor s*_eff(R)│
 │  • Metabolic Energy & Load: Settles analytically toward resting equilibrium (E=1, C=0) │
 │  • Expressive PAD State:    Reprojected on-the-fly via W_proj * [h, s]                 │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Inverted Startup Dependency Sequence (Remediating E-01/E-02/E-03)

In the current code, `EmotionCore` restores and integrates idle relaxation before `RelationshipUpdater` is constructed, leading to stranger Philia relaxation ($R_0$).

Under the ratified architecture, the constructor and recovery graph in `src/core/orchestrator/cognitive_orchestrator.py` is inverted:

```
                              INVERTED STARTUP RESTORE SEQUENCE
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Validate Commit Barrier & Consistency:                                                │
│    Read data/epoch_manifest.json. Verify that relationship.json and dynamical_state.json│
│    share the committed epoch. If partial write detected, execute deterministic recovery.│
│                                                                                          │
│ 2. Load Tier 1 Relational Invariants:                                                    │
│    Construct RelationshipUpdater(storage_path=relationship_storage_path).                │
│    Loads mature relational vector: R_t = relationship_updater.get_state().to_array()     │
│                                                                                          │
│ 3. Instantiate EmotionCore without Auto-Restore:                                         │
│    Construct EmotionCore(config, storage_path=dynamical_storage_path, auto_restore=False)│
│                                                                                          │
│ 4. Inject Relational Attractor Context (Critical Barrier):                               │
│    emotion_core.update_relationship_context(R_t)                                         │
│    -> EmotionCore._R_t is now R_t (NOT stranger baseline R_0!)                           │
│                                                                                          │
│ 5. Restore Dynamical Snapshot & Apply Two-Stage Recovery:                                │
│    emotion_core.restore_from_checkpoint(apply_elapsed_time=True)                         │
│    -> Advances state across Delta t = now - created_at toward s*_eff(R_t) bit-exact!     │
│                                                                                          │
│ 6. Reconstruct Derived State:                                                            │
│    PAD is reprojected via _project_to_pad(h, s). Serialized PAD is treated as metadata.  │
│                                                                                          │
│ 7. Construct Supporting Subsystems & Reseed Working Context:                             │
│    Construct HomeostaticEngine, ActiveInferenceEngine, etc.                              │
│    Reseed CognitiveOrchestrator._history from trailing K turns of chat_history.json.    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Commit Barrier & Consistency Detection Mechanism

### 3.1 Clarification: Commit Barrier vs. Atomic Commit
`epoch_manifest.json` is explicitly defined as a **Commit Barrier + Consistency Detection mechanism**. It is **not** an atomic multi-file transaction engine (like an ACID database engine).

- **How it Works:**
  During Stage 16 of `CognitiveOrchestrator.process()`:
  1. `data/relationship.json.tmp` is written with `epoch_id = N+1` and committed via `os.replace`.
  2. `data/dynamical_state.json.tmp` is written with `epoch_id = N+1` and committed via `os.replace`.
  3. `data/epoch_manifest.json.tmp` is written with `committed_epoch = N+1` and committed via `os.replace`.
  4. Step 3 constitutes the **Commit Barrier**: a state transition is only considered valid if `epoch_manifest.json` confirms it.

### 3.2 Deterministic Crash Recovery Protocol
If an unhandled crash or power failure occurs mid-write:
- **Scenario A: Crash after Step 1, before Step 2:**
  `relationship.json` has `epoch = N+1`, but `manifest.json` has `committed_epoch = N`.
  - *Recovery Action:* Startup detects that `relationship.json` is uncommitted. It rolls back `relationship.json` using `relationship.json.bak` (which contains epoch $N$). Both stores remain at epoch $N$.
- **Scenario B: Crash after Step 2, before Step 3:**
  Both domain stores have `epoch = N+1`, but manifest is at epoch $N$.
  - *Recovery Action:* Startup detects unfinalized commit barrier. It rolls back both stores to their `.bak` versions (epoch $N$), preserving bit-exact causal synchronization.
- **Result:** Complete immunity to cross-subsystem temporal and causal tears.

---

## 4. Working Dialogue Memory Reseeding Architecture

To resolve the discrepancy between persistent chat history and runtime cognitive context:

- **`data/chat_history.json`**: Permanent, append-only autobiographical transcript.
- **`CognitiveOrchestrator._history`**: In-RAM working context ring-buffer for `PromptAssembler`.
- **Startup Protocol:**
  On cold restart, `build_cognitive_orchestrator()` loads the trailing $K$ turns from `data/chat_history.json` and populates `_history`.
- **Calibration Parameter:**
  $K$ is recorded as an **implementation configuration parameter** (e.g., `default_context_turns = 10`), **NOT** an immutable architectural invariant. It can be tuned based on the active hardware tier and model context size (`n_ctx`).
