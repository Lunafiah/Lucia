# Persistence Topology Map — Lucia Cold-Restart Persistence (F-02-A Audit)

**Audit Scope:** Code archaeology and verification of all persistent stores, writers, readers, timestamps, and synchronization barriers in the Lucia repository post-Phase 24 / F-02 baseline.  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Execution Date:** 2026-10-07  
**Rule Set:** AGENTS.md Invariants, INV-1 (One Continuous Life), INV-5, INV-6, INV-8. Zero code changes.

---

## 1. Subsystem Persistence Topology Table

| Component | Storage File / Medium | Writer Class & Function | Reader Class & Function | Timestamp Metric | Atomic with Others? | Subsystem Status |
|---|---|---|---|---|---|---|
| **Dynamical State** (`h_fast` $\in \mathbb{R}^{32}$, `s_slow` $\in \mathbb{R}^{16}$) | `data/dynamical_state.json` (+ `.json.bak`) | `EmotionCore.checkpoint()` / `save_dynamical_checkpoint()` in `src/core/emotion/persistence.py` | `EmotionCore.restore_from_checkpoint()` in `src/core/emotion/emotion_core.py` | `created_at` (POSIX UTC float via `time.time()`) | **NO** (Standalone atomic replace) | **PERSISTED / PARTIALLY SYNCHRONIZED** |
| **Relational Attractor Context** (`EmotionCore._R_t`) | Ephemeral RAM (`EmotionCore._R_t`) | `EmotionCore.update_relationship_context()` (Stage 16.3 of turn) | `EmotionCore._ode_step()` & `integrate_unforced_idle()` | None (in-memory numpy array) | **NO** (Not persisted in dynamical checkpoint) | **DESYNCHRONIZED ON RESTART** |
| **Relationship State** ($R \in [0, 1]^4$) | `data/relationship.json` | `RelationshipUpdater.step()` / `save_relationship()` in `src/core/relationship/persistence.py` | `RelationshipUpdater.__init__()` / `load_relationship()` | `RelationshipState.timestamp` (`time.time()`) | **NO** (Standalone atomic replace) | **PERSISTED / INDEPENDENT** |
| **Homeostatic Somatic Markers** (`m_homeo`) | `data/dynamical_state.json` (metadata payload) | `EmotionCore.snapshot_dynamical_state()` | `EmotionCore.apply_dynamical_snapshot()` | `created_at` from dynamical snapshot | **NO** (Overwritten on Turn 1 Stage 5) | **EPHEMERAL / OVERWRITTEN** |
| **Homeostatic Engine State** (`_energy`, timestamps) | Ephemeral RAM only (`HomeostaticEngine`) | None | None | `time.monotonic()` (in RAM deque) | **NO** (Zero disk persistence) | **VOLATILE / RESET ON RESTART** |
| **SDM Memory Traces** (`SDMCore` / `AffectiveMemory`) | Ephemeral RAM only (`_hard_locs`, `_accumulator`, `_index`) | None | None | `time.monotonic()` (per trace) | **NO** (Zero disk persistence) | **VOLATILE / WIPED ON RESTART** |
| **Dialogue Working Memory** (`CognitiveOrchestrator._history`) | Ephemeral RAM only (`self._history`) | Stage 16.4 append | Stage 11 prompt assembly | None (list of tuples) | **NO** (Zero disk persistence) | **VOLATILE / WIPED ON RESTART** |
| **Chat History / Session Store** | `data/chat_history.json` | `ChatHistoryStore.append_turn()` in `src/core/storage/history_store.py` | `ChatHistoryStore._read_data()` | `time.time()` & ISO 8601 string | **NO** (Standalone JSON write) | **PERSISTED / DISCONNECTED FROM CORE PIPELINE** |
| **Genesis Onboarding Profile** | `data/profile.json` | Immutable / Locked Genesis Gate | `POST /onboarding` (lifecycle guard) | ISO 8601 / Genesis spec | **NO** (Read-only baseline) | **LOCKED INVARIANT (`is_onboarded: false`)** |

---

## 2. Execution Timing & Persistence Call Graph

### 2.1 Live Conversational Turn (`POST /process`)

```text
[API Request: POST /process] (src/api/server.py:180)
  │
  ├── 1. ChatHistoryStore.append_turn("user", req.input) ────> Writes data/chat_history.json
  │
  ├── 2. CognitiveOrchestrator.process(req.input) (src/core/orchestrator/cognitive_orchestrator.py:236)
  │     ├── Stage 1: Lexical Stimulus Processing
  │     ├── Stage 2: Temporal Stimulus Commitment (L2 Limbic)
  │     ├── Stage 3: Limbic Integration
  │     │     └── HomeostaticEngine.record_input() ──────────> Mutates in-memory _energy (-0.05)
  │     ├── Stage 4: Prediction Surprise & Belief Update
  │     ├── Stage 5: Homeostatic Modulation
  │     │     ├── HomeostaticEngine.compute_somatic_markers()
  │     │     └── EmotionCore.update_homeostatic_context() ──> Mutates in-memory _m_homeo
  │     ├── Stage 6-8: Affective Ecphory, Context, Knowledge
  │     ├── Stage 9: Relationship Read (rel_state = updater.get_state())
  │     ├── Stage 10-15: Prompt Assembly, LLM Inference, Safety Validation
  │     ├── Stage 16.1: Memory Encoding (affective_memory.store()) ──> Ephemeral RAM only
  │     ├── Stage 16.3: Relationship Update:
  │     │     ├── RelationshipUpdater.step(signal=sig)
  │     │     │     └── save_relationship() ─────────────────> Writes data/relationship.json (ATOMIC FILE 1)
  │     │     └── EmotionCore.update_relationship_context(rel_state_updated.to_array()) ──> Updates RAM _R_t
  │     ├── Stage 16.4: Working dialogue history append ─────> Ephemeral RAM only
  │     └── Stage 16.5: Dynamical State Checkpoint:
  │           └── EmotionCore.checkpoint()
  │                 └── save_dynamical_checkpoint() ─────────> Writes data/dynamical_state.json (ATOMIC FILE 2)
  │
  └── 3. ChatHistoryStore.append_turn("companion", resp_text) ─> Writes data/chat_history.json (FILE 3)
```

### 2.2 Cold Startup & Restore Sequence

```text
[Backend Startup: src/api/server.py -> build_cognitive_orchestrator()]
  │
  ├── Step 1 (line 804): EmotionCore.__init__(storage_path="data/dynamical_state.json")
  │     ├── Reads data/dynamical_state.json
  │     ├── apply_dynamical_snapshot(snapshot, apply_elapsed_time=True)
  │     │     ├── Sets _h = snapshot.h_fast, _s_slow = snapshot.s_slow
  │     │     └── integrate_unforced_idle(duration_s = now - snapshot.created_at)
  │     │           └── !!! USES self._R_t = self.R_0 (DEFAULT STRANGER BASELINE [0.0, 0.5, 0.0, 0.5]) !!!
  │     │               Because RelationshipUpdater HAS NOT BEEN CONSTRUCTED YET!
  │
  ├── Step 2 (line 808): HomeostaticEngine.__init__()
  │     └── Initializes _energy = 1.0 (Completely resets metabolic fatigue to full battery)
  │
  ├── Step 3 (line 810): AffectiveMemory.__init__()
  │     └── Initializes empty SDMCore (ALL PAST TRACES WIPED)
  │
  ├── Step 4 (line 833): RelationshipUpdater.__init__(storage_path="data/relationship.json")
  │     └── Loads data/relationship.json into RelationshipUpdater._current_state
  │
  └── Step 5 (line 837): CognitiveOrchestrator.__init__()
        ├── Starts EmotionCore fast loop background thread
        └── !!! NEVER FORWARDS relationship_updater._current_state TO EmotionCore._R_t !!!
```

---

## 3. Subsystem Inter-Store Coupling & Lock Boundaries

### 3.1 Lock Discipline
- `EmotionCore`: Snapshot taken under `_step_lock` $\rightarrow$ `_state_lock` within $\le 1\text{ms}$. Serialization performed after release.
- `RelationshipUpdater`: Lock `_lock` (RLock) held during update, but disk write occurs within the lock context block (`with self._lock:`).
- `ChatHistoryStore`: Uses independent threading lock `_lock`.
- **Zero cross-store locking:** There is no coordinator lock or transaction manager synchronizing `EmotionCore`, `RelationshipUpdater`, and `ChatHistoryStore`.
