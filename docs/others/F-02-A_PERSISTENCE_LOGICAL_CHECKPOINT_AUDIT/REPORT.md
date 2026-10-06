# F-02-A — Persistence / Logical Checkpoint Audit Report

**Document ID:** `AUDIT-F02A-20261007`  
**Classification:** Code Archaeology & Technical Verification Report  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Date:** 2026-10-07  
**Auditor:** Antigravity (Pair Programming with Lunafiah)  
**Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  
**Companion Artifacts:**  
- Topology Map: [`PERSISTENCE_TOPOLOGY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02-A_PERSISTENCE_LOGICAL_CHECKPOINT_AUDIT/PERSISTENCE_TOPOLOGY.md)  
- Evidence Ledger: [`EVIDENCE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02-A_PERSISTENCE_LOGICAL_CHECKPOINT_AUDIT/EVIDENCE.md)  

---

## 1. Executive Verdict

**Verdict:** **PARTIALLY COHERENT**  
**Confidence Level:** **HIGH (100% verified via code archaeology and execution tracing)**  

### Executive Summary
The current Lucia implementation does **not** possess an atomic logical checkpoint across subsystems. Instead of an integrated state tuple:
$$\mathcal{C} = \langle t, h, s, m_{\text{homeo}}, R, \text{memory}, \text{PAD}, \text{epoch\_id}, \text{schema\_version}\rangle$$
Lucia currently maintains **four independent, uncoordinated persistence fragments**:
1. `data/dynamical_state.json` (writes $h_{\text{fast}}$, $s_{\text{slow}}$, $m_{\text{homeo}}$, `pad`, `created_at` at Stage 16.5)
2. `data/relationship.json` (writes $R \in [0, 1]^4$ and update history at Stage 16.3)
3. `data/chat_history.json` (writes conversation turns at `/process` entry and exit)
4. `data/profile.json` (static, immutable Genesis onboarding gate)

While individual file writes for `dynamical_state.json` and `relationship.json` are crash-resilient (using tempfile write + atomic `os.replace`), **there is no multi-store coordination, transaction manager, or shared causal sequence number.** 

Most critically, code archaeology has uncovered a major temporal tear on startup: **`EmotionCore` auto-restores and executes downtime idle ODE integration before `RelationshipUpdater` is constructed.** During this idle integration, `EmotionCore._R_t` defaults to `R_0` (stranger baseline), causing slow latent state $s_{\text{slow}}$ to relax towards the unconditioned Philia attractor ($s^*_{\text{philia}}$) rather than the relationally conditioned attractor ($s^*_{\text{eff}}(R)$). Furthermore, the loaded relationship state is never pushed to `EmotionCore` until the user completes their first turn post-restart.

---

## 2. Persistence Topology Summary

*(Full mapping in [`PERSISTENCE_TOPOLOGY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02-A_PERSISTENCE_LOGICAL_CHECKPOINT_AUDIT/PERSISTENCE_TOPOLOGY.md))*

| Subsystem | Storage Mechanism | Serialization Trigger | Deserialization Trigger | Temporal Metadata |
|---|---|---|---|---|
| **Dynamical State** ($h_{\text{fast}}, s_{\text{slow}}$) | `data/dynamical_state.json` (+ `.bak`) | Stage 16.5 of turn | `EmotionCore.__init__` | Wall-clock UTC float (`created_at`) |
| **Relational Attractor Context** ($\_R\_t$) | In-memory RAM in `EmotionCore` | Stage 16.3 update | None (lost on shutdown) | None |
| **Relationship State** ($R$) | `data/relationship.json` | Stage 16.3 of turn | `RelationshipUpdater.__init__` | Wall-clock float (`timestamp`) |
| **Homeostatic State** ($m_{\text{homeo}}$) | Snapshot metadata / RAM | Stage 16.5 (metadata) | `EmotionCore.__init__` | Overwritten Turn 1 Stage 5 |
| **Homeostatic Engine** ($\_energy$) | RAM only | None | None | Monotonic clock (lost on shutdown) |
| **SDM Memory Traces** | RAM only | None | None | Monotonic clock (lost on shutdown) |
| **Dialogue Working Memory** | RAM only (`_history`) | Stage 16.4 | None | Reset on startup |
| **Chat History** | `data/chat_history.json` | API `/process` start & end | API reads / Markdown export | Wall-clock ISO string & float |

---

## 3. Logical Snapshot Analysis

### Does the system represent $\mathcal{C}$ or independent fragments?
**FACT FROM CODE:** The system currently represents **independent fragments**.

1. **Absence of Coordinated Epoch / Transaction ID:**
   Neither `DynamicalStateSnapshot` nor `RelationshipState` nor `ChatHistoryStore` contains an `epoch_id`, commit sequence number, or mutual transaction token. Each subsystem increments its own internal counters (`_tick_counter`, `_step_counter`) which reset to zero on process restart.
2. **Timestamp Asynchrony:**
   - In a single turn, `relationship.json` is stamped with `time.time()` at Stage 16.3 (`updater.py:118`).
   - `dynamical_state.json` is stamped with a later `time.time()` at Stage 16.5 (`persistence.py:292`).
   - The two timestamps represent different physical instants separated by model generation and turn-finalization overhead.
3. **Missing State in Snapshot:**
   The canonical dynamical snapshot contains $h_{\text{fast}}$ and $s_{\text{slow}}$, but does **not** include the relational state $R_t$ that conditions the attractor field $s^*_{\text{eff}}(R_t)$, nor does it include the SDM memory state.

---

## 4. Restart Race / Temporal-Tear Scenarios

### Scenario 1: Startup Relational Attractor Desynchronization (Verified Defect)
- **Trigger:** Process cold restart (e.g., launching the application).
- **Actual Write Order:** Both files (`dynamical_state.json` and `relationship.json`) are already on disk from previous sessions.
- **Actual Restore Order:**
  1. [`cognitive_orchestrator.py:804`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L804): `EmotionCore` is instantiated with `storage_path="data/dynamical_state.json"`.
  2. Inside `EmotionCore.__init__` ([`emotion_core.py:218`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L218)), `restore_from_checkpoint()` runs.
  3. `apply_dynamical_snapshot()` computes $\Delta t = \text{now} - \text{created\_at}$ and executes `integrate_unforced_idle()`.
  4. At this moment, `EmotionCore._R_t` is initialized to default baseline `R_0 = [0.0, 0.5, 0.0, 0.5]` ([`emotion_core.py:201`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L201)).
  5. 29 lines later ([`cognitive_orchestrator.py:833`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L833)), `RelationshipUpdater` is instantiated and reads `data/relationship.json` (e.g., $R = [0.8, 0.9, 0.7, 0.8]$).
  6. Neither `build_cognitive_orchestrator()` nor `CognitiveOrchestrator.__init__()` calls `emotion_core.update_relationship_context()`.
- **Resulting State:**
  - During downtime ODE relaxation, $s_{\text{slow}}$ relaxes toward the stranger baseline $s^*_{\text{philia}}$ instead of the bonded attractor $s^*_{\text{eff}}(R)$.
  - Between startup and the user's first completed turn, `EmotionCore` runs with $R_t = R_0$, while `RelationshipUpdater` holds the mature relationship.
- **Continuous Life Impact:** **VIOLATION OF RELATIONAL DYNAMICAL CONTINUITY.** A bonded companion instance reverts to stranger dynamical relaxation during offline rest.

---

### Scenario 2: Mid-Turn Crash / Asynchronous Multi-File Write
- **Trigger:** Sudden termination (power loss, OOM, user force-kill) during Stage 16.
- **Actual Write Order:**
  1. Turn begins: User turn written to `data/chat_history.json`.
  2. Stage 16.3: `data/relationship.json` written atomically with new state $R_{N+1}$.
  3. *Crash occurs before Stage 16.5.*
  4. `data/dynamical_state.json` is NEVER written for turn $N+1$.
- **Actual Restore Order on Next Boot:**
  - `RelationshipUpdater` loads $R_{N+1}$.
  - `EmotionCore` loads $h_{\text{fast}}, s_{\text{slow}}$ from turn $N$.
- **Resulting State:**
  Relational state is from turn $N+1$, while dynamical state is from turn $N$. When recovery ODE executes, it uses timestamp from turn $N$ (calculating a longer $\Delta t$ than actual).
- **Continuous Life Impact:** **CAUSAL ASYNCHRONY.** Subsystems disagree on whether turn $N+1$ occurred.

---

### Scenario 3: Idle Shutdown Trajectory Loss (Force-Kill via Electron)
- **Trigger:** Electron app exit on Windows (`taskkill /F`).
- **Actual Write Order:**
  - During idle conversation gaps, `EmotionCore` continuously steps ODE every 200 ms in RAM.
  - No checkpoints are written during idle (checkpoints only trigger at Stage 16.5 of a turn).
  - App is closed after 2 hours of idle. `taskkill /pid <pid> /T /F` kills backend immediately ([`process-manager.js:167`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/main/process-manager.js#L167)).
- **Actual Restore Order on Next Boot:**
  - Checkpoint timestamp `created_at` reflects the end of the last conversational turn $T_{\text{last\_turn}}$, **not** the shutdown time $T_{\text{shutdown}}$.
  - `apply_dynamical_snapshot()` integrates unforced rest over $\Delta t = T_{\text{boot}} - T_{\text{last\_turn}}$ (e.g., 2 hours of live idle + 1 hour offline = 3 hours).
- **Resulting State:**
  Live idle dynamics are wiped; recovery simulates the live idle period as if Lucia were offline.
- **Continuous Life Impact:** **TEMPORAL DISTORTION.** Active awake idle time is converted into unforced offline sleep.

---

### Scenario 4: Autobiographical Memory Amnesia vs. Relational Metrics Survival
- **Trigger:** Normal restart.
- **Actual Write Order:**
  - Dialogue saved in `data/chat_history.json`.
  - Relationship metrics saved in `data/relationship.json`.
  - SDM memory traces in `AffectiveMemory` are NEVER written to disk.
- **Actual Restore Order:**
  - `RelationshipUpdater` loads familiarity, trust, closeness, reciprocity.
  - `AffectiveMemory` initializes with 0 traces ([`affective_memory.py:75`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/affective_memory.py#L75)).
  - `CognitiveOrchestrator._history` initializes with empty list `[]` ([`cognitive_orchestrator.py:191`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L191)).
- **Resulting State:**
  Lucia "knows" she has high closeness/trust ($R = [0.8, 0.9, 0.7, 0.8]$), but has **zero episodic recollection traces** in SDM and zero short-term conversational context.
- **Continuous Life Impact:** **DISSOCIATIVE AUTOBIOGRAPHICAL AMNESIA.** High intimacy without episodic recall.

---

## 5. Crash Consistency Evaluation

| Level | Mechanism Evaluated | Verification Result | Failure Mode / Behavior |
|---|---|---|---|
| **Level 1: Single File Write** | `save_dynamical_checkpoint()` in `src/core/emotion/persistence.py` | **VERIFIED SAFE** | Uses `tempfile.mkstemp` on same volume + `os.replace`. Partial file write is impossible. |
| **Level 2: Backup Ladder** | Target `.json` + `.json.bak` + Philia initial fallback | **VERIFIED SAFE** | Corrupted primary falls back to `.bak`. Corrupted backup falls back to Philia baseline without crash. |
| **Level 3: Multi-Store Transaction** | Cross-subsystem write coordination | **VERIFIED INCONSISTENT** | No two-phase commit, journal, or write-ahead log across `dynamical_state.json` and `relationship.json`. |
| **Level 4: Schema Mismatch** | Schema version check (`CURRENT_SCHEMA_VERSION = "1.0"`) | **VERIFIED SAFE** | Rejects incompatible version, logs warning, falls back cleanly to baseline. |

---

## 6. Semantic Continuity Matrix

| Dimension | Preserved Across Restart? | Reconstructed Dynamically? | Lost on Restart? | Architectural Status |
|---|---|---|---|---|
| **Fast Reactive Dynamics ($h_{\text{fast}}$)** | Yes (persisted in JSON) | Rapidly decays via unforced ODE ($\tau_f \le 1.5\text{s}$) | Transient momentum lost if $\Delta t \gg 5\text{s}$ | **CONDITIONALLY PRESERVED** |
| **Slow Latent Field ($s_{\text{slow}}$)** | Yes (persisted in JSON) | Relaxed via unforced ODE during rest interval | True attractor target distorted by $R_0$ desync | **PRESERVED WITH ATTRACTOR TEAR** |
| **Relational Vector ($R_t$)** | Yes (persisted in JSON) | Loaded into `RelationshipUpdater` | Disconnected from `EmotionCore` until Turn 1 | **FRAGMENTED CONTINUITY** |
| **Affective Projection (PAD)** | Metadata persisted | Recomputed via $W_{\text{proj}} \cdot [h, s]$ | Raw serialized PAD is not loaded (reprojected) | **CONSISTENT (BY DESIGN)** |
| **Homeostatic Energy ($E$)** | No (only in metadata) | Hardcoded to $1.0$ in `HomeostaticEngine` | Pre-shutdown metabolic fatigue completely wiped | **VOLATILE / RESET** |
| **SDM Episodic Traces** | No (RAM only) | None | 100% of Kanerva SDM traces lost | **TOTAL LOSS** |
| **Short-Term Dialogue Context** | No (RAM only) | None (chat_history not loaded into `_history`) | Previous dialogue turns unavailable to prompt assembler | **TOTAL LOSS IN PIPELINE** |

---

## 7. Architectural Gaps Demonstrated by Code Archaeology

1. **GAP-F02A-1: Startup Attractor Desynchronization (`_R_t` Initialization Gap)**
   `EmotionCore.__init__` restores dynamical state and runs downtime idle ODE before `RelationshipUpdater` is constructed, and `build_cognitive_orchestrator` never syncs loaded $R_t$ to `EmotionCore`.
2. **GAP-F02A-2: Lack of Atomic Multi-Store Commit Coordination**
   `relationship.json` and `dynamical_state.json` are written sequentially with independent locks and timestamps. No shared transaction ID or crash journal links them.
3. **GAP-F02A-3: Lack of Graceful Shutdown Checkpoint**
   Because process termination on Windows is executed via `taskkill /F` and no shutdown hooks exist in FastAPI, the dynamical state evolving during post-turn idle is discarded.
4. **GAP-F02A-4: Ephemeral SDM Affective Memory Substrate**
   `AffectiveMemory` and `SDMCore` operate purely in volatile RAM, leading to memory reset across restarts while relationship and emotional vectors persist.
5. **GAP-F02A-5: Disconnected Chat History Store**
   `data/chat_history.json` exists for UI/markdown logging but is never read by `CognitiveOrchestrator` to populate working dialogue memory `_history` on startup.

---

## 8. Recommendation & Status

### F-02-A Assessment
**Status:** **REQUIRES ARCHITECTURAL DECISION**

The current implementation satisfies the narrow requirement of serializing $h_{\text{fast}}$ and $s_{\text{slow}}$ across process restarts (F-02 baseline), but **fails to constitute a coherent logical checkpoint across subsystems.** 

Before F-02 can be marked as fully resolved for the Engineering Readiness Audit, an architectural decision must ratify:
1. **Startup Synchronization Contract:** Mandating that `EmotionCore` receives the loaded `RelationshipState` before downtime ODE integration begins.
2. **Attractor Coupling Contract:** Persisting $R_t$ within the dynamical checkpoint or ensuring atomic co-restoration.
3. **Shutdown Hook Protocol:** Establishing a graceful shutdown pathway to snapshot dynamical state at process termination rather than relying solely on turn-completion checkpoints.

---

## 9. Top 3 Most Important Findings

1. **Critical Attractor Desynchronization on Boot:**
   `EmotionCore` runs long-downtime recovery ODE with $R_t = R_0$ ([`cognitive_orchestrator.py:804`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L804), [`emotion_core.py:201`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L201)) because it auto-restores before `RelationshipUpdater` loads `data/relationship.json`, and `build_cognitive_orchestrator` never synchronizes them. Consequently, downtime relaxation relaxes toward unconditioned stranger Philia ($s^*_{\text{philia}}$) rather than the bonded attractor ($s^*_{\text{eff}}(R)$).
2. **Independent Fragmented Storage without Transaction Coordination:**
   Lucia stores state across four uncoordinated JSON files (`dynamical_state.json`, `relationship.json`, `chat_history.json`, `profile.json`) with different write timings, independent locks, no shared transaction ID, and no two-phase commit. A mid-turn crash leaves subsystems in mutually inconsistent states.
3. **Total Memory & Fatigue Reset (Ephemeral Subsystems):**
   While dynamical and relational vectors persist, `AffectiveMemory` (Kanerva SDM) and `HomeostaticEngine` ($\_energy$) are 100% volatile RAM. Every restart wipes all autobiographical memory traces and resets metabolic fatigue to full battery, breaking cross-session episodic continuity.

---

`F-02-A STATUS: REQUIRES ARCHITECTURAL DECISION`
