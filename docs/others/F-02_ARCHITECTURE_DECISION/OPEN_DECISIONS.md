# Open Architecture Decisions Requiring Owner Ratification (F-02)

**Document ID:** `DEC-OPEN-F02-20261007`  
**Classification:** Governance & Ratification Ledger  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`ADR_ANALYSIS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/ADR_ANALYSIS.md)  
**Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md)  

---

## 1. Governance Boundary Notice

> [!IMPORTANT]
> **MANDATORY GOVERNANCE INVARIANT:**  
> Autonomous agents are strictly prohibited from self-ratifying architecture decisions, mutating canonical schemas, altering `data/profile.json`, modifying production code, or committing changes during an architecture decision analysis task.  
> The decisions cataloged below belong **exclusively to the Lucia Human Owner (Lunafiah)**.

---

## 2. Ledger of Open Decisions

### Decision D-01: Canonical State Persistence Architecture
- **Question:** Which architectural pattern shall govern multi-store persistence across `EmotionCore`, `RelationshipUpdater`, and `ChatHistoryStore`?
- **Candidate Options:**
  - **Option 1 (Option A):** Maintain existing fragmented JSON persistence with independent file writes and no epoch coordination. *(Rejected by analysis)*
  - **Option 2 (Option C):** Consolidate all subsystem state into a single monolithic JSON envelope $\mathcal{C}$. *(Rejected by analysis)*
  - **Option 3 (Option D/F Synthesis - Recommended):** Adopt the Two-Tier Coherent Checkpoint Architecture. Decouple Tier 1 Authoritative Invariants from Tier 2 Reconstructible Dynamical State, synchronized via a unified Commit Epoch Barrier and Startup Dependency Inversion.
- **Agent Recommendation:** **Option 3 (Option D/F Synthesis).**
- **Impact of Ratification:** Resolves E-01 (startup attractor tear) and E-04 (multi-store causal inconsistency) while respecting the 20-Watt lock and latency constraints.

---

### Decision D-02: Long-Downtime Recovery Model & Parameters
- **Question:** Which mathematical model shall govern dynamical relaxation across extended offline downtime ($\Delta t \gg 0$)?
- **Candidate Options:**
  - **Option 1:** Unbounded Forward Euler ODE Replay. *(Current implementation; fails startup latency for long downtime)*
  - **Option 2:** Fixed Bounded Cutoff (e.g., hard cap at 300s). *(Rejected by analysis; ungrounded, leaves system in non-equilibrium)*
  - **Option 3:** Adaptive / Error-Budgeted Runge-Kutta. *(Viable research candidate; higher algorithmic complexity)*
  - **Option 4 (Alternative 5 - Recommended):** Hybrid Short Replay + Asymptotic Closed-Form Relaxation. Numerical Euler for $\Delta t \le \tau_{\text{cutoff}}$, and exact analytical exponential decay to $s^*_{\text{eff}}(R_t)$ for $\Delta t > \tau_{\text{cutoff}}$.
- **Parameter Choice for Option 4:** Selection of $\tau_{\text{cutoff}} \in \{30.0\text{s}, 60.0\text{s}, 120.0\text{s}\}$.
- **Agent Recommendation:** **Option 4 with $\tau_{\text{cutoff}} = 60.0\text{s}$.**
- **Impact of Ratification:** Bounded $O(1)$ startup latency ($\le 1\text{ms}$) on any cold boot, infinite time-horizon mathematical stability, and zero attractor distortion.

---

### Decision D-03: SDM Episodic Memory Durability Boundary
- **Question:** Does the current volatility of Kanerva SDM memory traces (`AffectiveMemory`) constitute a blocker for F-02 and the Engineering Readiness Audit, or is it formally deferred to a dedicated Memory Persistence Phase (e.g., Phase 25)?
- **Candidate Options:**
  - **Option 1 (Blocker):** Halt F-02 readiness; expand F-02 scope to engineer binary disk serialization, address matrix persistence, and trace indexing for `SDMCore`.
  - **Option 2 (Phase Boundary Deferral - Recommended):** Formally ratify that F-02 governs subcortical limbic and relational continuity ($h, s, R$), while cortical episodic SDM persistence belongs to a dedicated Phase 25 milestone.
- **Agent Recommendation:** **Option 2 (Deferral to Phase 25).**
- **Impact of Ratification:** Prevents scope explosion in F-02; preserves sub-millisecond turn latency; allows focused implementation of limbic-relational coherence.

---

### Decision D-04: Epoch Synchronization Mechanism
- **Question:** How shall cross-store causal consistency be implemented between `data/relationship.json` and `data/dynamical_state.json`?
- **Candidate Options:**
  - **Option 1 (Centralized Manifest):** Introduce a lightweight coordinator file `data/epoch_manifest.json` recording `{"epoch_id": int, "t_commit": float, "last_successful_turn": int}` written atomically after all stores complete.
  - **Option 2 (Header Cross-Validation):** Embed `epoch_id: int` directly in the schemas of both `dynamical_state.json` and `relationship.json`. On cold boot, orchestrator verifies that `dyn.epoch_id == rel.epoch_id`.
- **Agent Recommendation:** **Option 1 (Centralized Manifest).**
- **Impact of Ratification:** Provides a single, unambiguous commit point for multi-store state transactions without altering existing domain JSON schemas.

---

### Decision D-05: Homeostatic Energy / Fatigue Durability
- **Question:** Shall metabolic energy $\mathcal{E}$ and cognitive load $\mathcal{C}$ be persisted in the checkpoint and settled asymptotically across downtime, or remain volatile RAM resetting to $\mathcal{E}=1.0$?
- **Candidate Options:**
  - **Option 1 (Remain Volatile):** Keep `HomeostaticEngine` ephemeral. $\mathcal{E}$ resets to $1.0$ on every restart.
  - **Option 2 (Asymptotically Settled - Recommended):** Store $\mathcal{E}$ and $\mathcal{C}$ in the checkpoint; on restart, settle toward resting levels based on elapsed physical time ($\Delta t$).
- **Agent Recommendation:** **Option 2 (Asymptotically Settled).**
- **Impact of Ratification:** Prevents artificial fatigue wipe on quick application restarts while preserving biological rest realism over long offline downtime.

---

### Decision D-06: Graceful Process Shutdown Hook
- **Question:** Shall Lucia establish a graceful shutdown pathway to capture idle dynamical drift prior to process exit, or rely strictly on Stage 16.5 turn checkpoints?
- **Candidate Options:**
  - **Option 1 (Turn Checkpoints Only):** Accept that unforced idle drift occurring between the last turn and application exit is discarded.
  - **Option 2 (Graceful IPC Hook - Recommended):** Update `electron/main/process-manager.js` to send `SIGINT` / `POST /lifecycle/shutdown` with a 1500ms timeout prior to forceful `taskkill /F`, and register a FastAPI shutdown handler to persist `EmotionCore.checkpoint()`.
- **Agent Recommendation:** **Option 2 (Graceful IPC Hook).**
- **Impact of Ratification:** Eliminates Scenario 3 (Idle Shutdown Trajectory Loss) and guarantees that the persisted state accurately captures the exact shutdown instant.

---

### Decision D-07: Authorization for Implementation Phase
- **Question:** Is implementation of the ratified architecture authorized to proceed?
- **Options:**
  - **YES:** Authorize remediation work under an explicit implementation plan.
  - **NO:** Analysis only; implementation remains blocked pending further design review.
- **Current Status:** **NO (BLOCKED PENDING OWNER REVIEW).**

---

*This document is an architecture decision analysis artifact prepared for Owner Review. Implementation is NOT authorized.*
