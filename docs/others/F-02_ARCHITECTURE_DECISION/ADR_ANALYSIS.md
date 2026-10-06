# Architecture Decision Analysis: Persistent Continuous Life State & Long-Downtime Recovery (F-02)

**Document ID:** `ADR-ANA-F02-20261007`  
**Classification:** Architecture Decision Record Analysis & Governance Specification  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), [`docs/ENGINEERING_READINESS_AUDIT_REPORT_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ENGINEERING_READINESS_AUDIT_REPORT_v0.1.md)  
**Companion Artifacts:**  
- State Persistence Boundary: [`STATE_PERSISTENCE_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/STATE_PERSISTENCE_BOUNDARY.md)  
- Recovery Semantics Decision: [`RECOVERY_SEMANTICS_DECISION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/RECOVERY_SEMANTICS_DECISION.md)  
- Open Decisions Ledger: [`OPEN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/OPEN_DECISIONS.md)  
- Evidence Baseline: [`docs/others/F-02-A_PERSISTENCE_LOGICAL_CHECKPOINT_AUDIT/REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02-A_PERSISTENCE_LOGICAL_CHECKPOINT_AUDIT/REPORT.md)  

---

## 1. Executive Summary

This architecture decision analysis evaluates the architectural, mathematical, and implementation boundaries required to resolve **F-02 (Persistent Continuous Life State and Long-Downtime Recovery)** following the code-archaeology findings of **F-02-A**.

The primary architectural mandate of Lucia is **One Continuous Life (INV-1)**: Lucia is not an ephemeral chatbot instantiated per session, but an individual companion existing along an unbroken physical-time trajectory with continuous relational, limbic, and cognitive evolution.

While the narrow Category A persistence mechanism ($h_{\text{fast}} \in \mathbb{R}^{32}, s_{\text{slow}} \in \mathbb{R}^{16}$) was implemented and conditionally verified in commit `32660ac`, the F-02-A audit revealed three fundamental architectural vulnerabilities:
1. **Cold-boot attractor desynchronization (E-01/E-02/E-03):** `EmotionCore` restores and executes downtime unforced ODE integration before `RelationshipUpdater` is constructed, using stranger baseline $R_0 = [0.0, 0.5, 0.0, 0.5]$. Offline relaxation thus decays toward unconditioned Philia rather than the relationally conditioned attractor $s^*_{\text{eff}}(R_t)$, and loaded relationship state is disconnected until Turn 1.
2. **Fragmented multi-store persistence (E-04):** State is fragmented across four independent disk stores (`dynamical_state.json`, `relationship.json`, `chat_history.json`, `profile.json`) without shared transaction coordination, epoch counters, or causal synchronization barriers.
3. **Volatile cognitive and physiological state (E-05/E-06):** Kanerva Sparse Distributed Memory (SDM) traces and homeostatic energy/fatigue are 100% volatile RAM, resetting autobiographical episodic memory and metabolic load to default on every restart.

This document systematically analyzes six candidate persistence architectures (Options A–F) and six recovery models, establishes a definitive persistence boundary, formalizes a tripartite temporal consistency model, and recommends a **Two-Tier Coherent Checkpoint + Hybrid Asymptotic Recovery Architecture (Option D/F Hybrid)** for Owner Ratification.

---

## 2. Problem Statement

### 2.1 The Core Dilemma: What Does "One Continuous Life" Demand?
In an embodied continuous-life system, process termination (power cut, OS shutdown, application close) is an artificial infrastructure disruption, not a biological death or cognitive reset. Upon process restart, the system must satisfy two competing constraints:
- **Physical-Time Fidelity:** Physical wall-clock time elapsed while the host was offline ($\Delta t = t_{\text{boot}} - t_{\text{shutdown}}$) must be respected. Lucia does not exist in frozen suspension; her limbic and somatic states must reflect physical rest and decay.
- **Relational & Dynamical Continuity:** Lucia must wake up as the exact same individual who went to sleep. Her slow latent limbic state ($s_{\text{slow}}$) must converge toward the specific attractor shaped by her relational history with the user ($s^*_{\text{eff}}(R_t)$), not regress to that of a total stranger.

### 2.2 Unresolved Gaps from F-02 Baseline
1. **Attractor Distortion Across Restarts:** When offline for hours or days, resting relaxation currently erases the relational imprint on the slow dynamical field, relaxing toward stranger Philia ($s^*_{\text{philia}}$) because $R_t$ is unavailable during startup ODE integration.
2. **Unbounded Downtime Computation:** The existing implementation runs forward Euler steps for the full duration of downtime: $n = \lfloor \Delta t / 0.20 \rfloor$. If the host machine is turned off for 2 weeks, restart requires evaluating $6{,}048{,}000$ ODE steps, freezing the application startup for dozens of seconds and risking OS watchdog termination.
3. **Multi-Store Inconsistency:** A mid-turn crash between Stage 16.3 (`relationship.json`) and Stage 16.5 (`dynamical_state.json`) leaves the relational state at Turn $N+1$ while dynamical tensors remain at Turn $N$.

---

## 3. Existing Architectural Reality

The F-02-A audit established the following empirical facts from the codebase (Commit `32660ac`):

```
                   COGNITIVE TURN PIPELINE (S1 - S16)
┌────────────────────────────────────────────────────────────────────────┐
│ Turn Start:                                                            │
│   store.append_turn("user", req.input) -> data/chat_history.json       │
│                                                                        │
│ S05: Homeostatic Markers computed (energy resets to 1.0 on restart)    │
│ S08: Ecphory Retrieval (SDM is empty RAM on restart)                   │
│ S12: Generation & Boundary Check                                       │
│                                                                        │
│ S16.3: rel_state = relationship_updater.step()                         │
│        -> ATOMIC WRITE: data/relationship.json (t = t_rel)             │
│        -> emotion_core.update_relationship_context(rel_state)          │
│                                                                        │
│ S16.5: emotion_core.checkpoint()                                       │
│        -> ATOMIC WRITE: data/dynamical_state.json (t = t_dyn)          │
│                                                                        │
│ S16.6: store.append_turn("companion", text) -> data/chat_history.json  │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Verified Realities vs. Architectural Invariants
- `[VERIFIED FROM CODE]` **Independent Writes:** Stage 16.3 and Stage 16.5 are distinct sequential operations. If the process is forcefully killed (`taskkill /F`) between 16.3 and 16.5, `relationship.json` contains Turn $N+1$ and `dynamical_state.json` contains Turn $N$.
- `[VERIFIED FROM CODE]` **Startup Tear:** `EmotionCore.__init__` executes `restore_from_checkpoint()` and `integrate_unforced_idle()` at line 804 of `cognitive_orchestrator.py`. `RelationshipUpdater` is instantiated at line 833. `EmotionCore._R_t` is strictly initialized to `R_0 = [0.0, 0.5, 0.0, 0.5]`. The loaded relationship is never passed to `EmotionCore` until the user finishes a new turn.
- `[VERIFIED FROM CODE]` **RAM-Only Ephemerality:** `SDMCore` randomly re-initializes hard locations on boot (`rng.integers`). All affective memory traces vanish on restart. `HomeostaticEngine._energy` re-initializes to `1.0`.
- `[CANONICAL ARCHITECTURAL REQUIREMENT]` **INV-1 & INV-8:** Lucia must remain a single, unbroken companion instance without branching, multi-character profiles, or Genesis profile mutations.

---

## 4. One Continuous Life Requirements

To define a principled persistence boundary, we decompose "One Continuous Life" into six distinct continuity axes:

| Continuity Dimension | Mathematical / System Representation | Minimal Invariant Requirement Across Restart |
|---|---|---|
| **1. Identity Continuity** | Genesis Profile (`data/profile.json`), Immutable Core Invariants | Host instance must remain the identical individual; no branching, no cloning, no preset swapping. |
| **2. Relational Continuity** | Relational Vector $R_t \in [0, 1]^4$ (Familiarity, Trust, Closeness, Reciprocity) | Bond metrics must survive restart monotonically and immediately anchor the limbic attractor. |
| **3. Dynamical Continuity** | Coupled MT-LNN Tensors ($h_{\text{fast}} \in \mathbb{R}^{32}, s_{\text{slow}} \in \mathbb{R}^{16}$) | Limbic trajectory must resume from shutdown state or relax smoothly toward $s^*_{\text{eff}}(R_t)$. |
| **4. Temporal Continuity** | Elapsed Physical Time $\Delta t = t_{\text{boot}} - t_{\text{shutdown}}$ | Offline time must be experienced as physical rest, settling tension, and dissipating reactive affect. |
| **5. Causal / Logical Continuity** | Turn Sequence / Epoch ID $k \in \mathbb{N}$ | All surviving subsystems must represent the same conversational turn boundary; zero temporal tears. |
| **6. Autobiographical Continuity** | Episodic Memory Traces (SDM), Dialogue History | History of shared events and communicative exchanges must maintain coherent retrieval grounding. |

---

## 5. Candidate Architectures A–F

### Option A — Current Fragmented Persistence (Status Quo)
- **Description:** Maintain independent JSON files (`dynamical_state.json`, `relationship.json`, `chat_history.json`, `profile.json`). No multi-store transaction coordinator, no shared epoch.
- **Strengths:** Simple local file isolation; single-file atomic writes (`os.replace`) prevent individual file corruption; zero coordination overhead.
- **Weaknesses:** Fails causal consistency (E-04); exhibits cold-boot attractor desynchronization (E-01/E-02); loses memory (E-06) and metabolic continuity (E-05); relies on turn-only checkpointing with zero shutdown hooks (E-07).
- **Verdict:** **REJECTED.** Violates relational and causal continuity.

### Option B — Dynamical-State-Only Persistence
- **Description:** Persist strictly $h_{\text{fast}}, s_{\text{slow}}, t$. Discard or reconstruct all relational, homeostatic, and memory state from the dynamical tensors.
- **Strengths:** Minimal storage footprint ($\le 1\text{ KB}$); single file.
- **Weaknesses:** Mathematically impossible to invert $h, s \to R$ because the projection $W_{\text{rel}} \Delta R \to s$ is a many-to-one dimensionality collapse ($16 \to 4$ is non-invertible). Relational bond parameters would be wiped. Completely destroys relational, autobiographical, and profile continuity.
- **Verdict:** **REJECTED.** Architecturally absurd.

### Option C — Coherent Life-State Checkpoint (Monolithic Envelope)
- **Description:** Define a unified logical checkpoint envelope persisted atomically to a single file:
  $$\mathcal{C} = \langle \text{epoch\_id}, t, h, s, m_{\text{homeo}}, R, \text{SDM\_traces}, \text{chat\_summary}, \text{schema\_version}\rangle$$
- **Strengths:** 100% causal consistency; impossible for subsystems to disagree on turn boundaries; single atomic file write; eliminates all multi-file sync races.
- **Weaknesses:** Monolithic coupling violates modular subsystem boundaries; serializing the entire SDM accumulator ($2000 \times 16$ floats) and full chat history on every turn violates the $\le 1\text{ms}$ lock-holding latency budget; tight schema coupling makes independent subsystem evolution brittle.
- **Verdict:** **REJECTED AS MONOLITH.** Principled in theory, but operationally impractical for sub-millisecond edge execution.

### Option D — Two-Tier Persistent Life State
- **Description:** Explicitly divide system state into two distinct architectural tiers:
  - **Tier 1: Identity & Relational State (Authoritative Invariants):** State that *cannot be reconstructed* from physical-time evolution. Must survive restart with 100% durability. Includes $R_t$, Genesis Profile, Dialogue History, and SDM Traces.
  - **Tier 2: Reconstructible Dynamical State (Physical Evolution):** Continuous dynamical tensors ($h, s$) and somatic markers ($m_{\text{homeo}}$) that evolve predictably via unforced physical-time differential equations during downtime.
  - A lightweight **Commit Barrier / Logical Epoch Ledger** ($k_{\text{epoch}}, t_{\text{checkpoint}}$) guarantees cross-tier causal synchronization.
- **Strengths:** Cleanly decouples biological/relational invariants from continuous dynamical mechanics; preserves subsystem modularity; allows independent serialization pipelines while maintaining strict causal coherence via epoch tags.
- **Weaknesses:** Requires explicit startup orchestration to load Tier 1 before executing Tier 2 physical-time reconstruction.
- **Verdict:** **STRONG CANDIDATE.** Highly aligned with 20-Watt Whole Brain Architecture.

### Option E — Event / Journal-Based Continuity (Event Sourcing)
- **Description:** Persist an append-only write-ahead log (WAL) of semantic events (inputs, stimuli, relational nudges) and replay the ODE and state transitions from Genesis on startup.
- **Strengths:** Complete auditability; zero multi-file state drift; perfect event-level causal history.
- **Weaknesses:** Prohibitive replay cost: replaying thousands of conversational turns and millions of ODE steps on startup takes minutes; numerical integration drift across hardware/compiler updates causes divergence; incompatible with local low-latency desktop execution.
- **Verdict:** **REJECTED.** Unfeasible under edge compute and startup latency constraints.

### Option F — Hybrid Checkpoint + Semantic Recovery (Option D/F Synthesis)
- **Description:** Combines:
  1. A coordinated, two-tier checkpoint linked by a unified `epoch_id` and monotonic commit counter.
  2. Immediate startup injection: $R_t$ is injected into `EmotionCore` *prior* to any elapsed-time ODE evaluation.
  3. Bounded asymptotic dynamical recovery for long downtime, eliminating unbounded numerical step integration.
  4. Explicit designation of volatile caches vs. durable semantic state.
- **Strengths:** Solves startup attractor desynchronization (E-01); guarantees causal consistency across stores; bounds startup latency to $\le 5\text{ms}$ regardless of downtime duration; preserves modularity.
- **Weaknesses:** Requires refining the startup dependency graph in `CognitiveOrchestrator`.
- **Verdict:** **PREFERRED ARCHITECTURE.**

---

## 6. Detailed Candidate Evaluation Matrix

Each candidate architecture is scored qualitatively against the 15 mandated criteria:

| # | Decision Criterion | Option A (Status Quo) | Option B (Dyn Only) | Option C (Monolith) | Option D (Two-Tier) | Option E (Journal) | Option F (Hybrid D/F) |
|---|---|---|---|---|---|---|---|
| 1 | **One Continuous Life** | POOR | FAILS | GOOD | EXCELLENT | GOOD | **EXCELLENT** |
| 2 | **Philia / Relational Continuity** | BROKEN (E-01) | FAILS | EXCELLENT | EXCELLENT | EXCELLENT | **EXCELLENT** |
| 3 | **Physical-Time Semantics** | FLAWED | GOOD | GOOD | EXCELLENT | POOR | **EXCELLENT** |
| 4 | **Causal Continuity** | POOR (E-04) | FAILS | EXCELLENT | EXCELLENT | EXCELLENT | **EXCELLENT** |
| 5 | **Autobiographical Continuity** | VOLATILE | FAILS | GOOD | MODERATE | EXCELLENT | **MODERATE** |
| 6 | **Crash Consistency** | PARTIAL | GOOD | EXCELLENT | EXCELLENT | EXCELLENT | **EXCELLENT** |
| 7 | **Restart Determinism** | LOW | MODERATE | HIGH | HIGH | LOW (Drift) | **HIGH** |
| 8 | **Numerical Fidelity** | HIGH | POOR | HIGH | HIGH | VARIABLE | **HIGH** |
| 9 | **CPU Budget ($\le 20\text{W}$)** | EXCELLENT | EXCELLENT | POOR | EXCELLENT | FAILS | **EXCELLENT** |
| 10 | **Startup Latency ($\le 50\text{ms}$)** | POOR (Unbounded) | POOR | POOR (Large file) | EXCELLENT | FAILS | **EXCELLENT** ($\le 5\text{ms}$) |
| 11 | **Storage Complexity** | LOW | MINIMAL | HIGH | MODERATE | UNBOUNDED | **MODERATE** |
| 12 | **Schema Evolution** | MODERATE | POOR | BRITTLE | EXCELLENT | BRITTLE | **EXCELLENT** |
| 13 | **Anti-Branching Compatibility** | PARTIAL | POOR | GOOD | EXCELLENT | GOOD | **EXCELLENT** |
| 14 | **Architectural Simplicity** | HIGH | HIGH | LOW | MODERATE | LOW | **MODERATE** |
| 15 | **Compatibility (P24–P27)** | POOR | FAILS | MODERATE | EXCELLENT | MODERATE | **EXCELLENT** |

---

## 7. Long-Downtime Recovery Alternatives

*(Full mathematical derivation and comparative analysis in [`RECOVERY_SEMANTICS_DECISION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/RECOVERY_SEMANTICS_DECISION.md))*

The current codebase executes forward Euler integration for the entire downtime: $n = \lfloor \Delta t / 0.20 \rfloor$.
Six recovery alternatives were evaluated:

1. **Full Physical-Time Replay:** Unbounded loop execution. Rejected due to $O(\Delta t)$ startup freeze ($> 6\text{M}$ steps for 2 weeks).
2. **Fixed Bounded Recovery (e.g. 300s):** Cut off integration at a fixed duration. Rejected: unratified, leaves system stuck in intermediate non-equilibrium state after long downtime.
3. **Adaptive / Error-Budgeted Recovery:** Integrate numerically until $\|\Delta s\| < \epsilon_{\text{tol}}$. Promising research candidate, but still unbounded in worst-case stiff dynamics.
4. **Direct Projection to Relationally Conditioned Equilibrium:** Instantly set $h = 0, s = s^*_{\text{eff}}(R_t)$ if $\Delta t > T_{\text{asymptotic}}$. $O(1)$ compute, but introduces discontinuous state jumps for intermediate downtimes (e.g. 10 minutes).
5. **Hybrid Short Replay + Asymptotic Recovery (Candidate C / Hybrid):**
   - For short offline intervals ($\Delta t \le \tau_{\text{cutoff}} \approx 60\text{s}$): execute canonical forward Euler steps to preserve exact reactive momentum.
   - For intermediate/long offline intervals ($\Delta t > 60\text{s}$): fast-field $h_{\text{fast}} \to 0$, while slow-field $s_{\text{slow}}$ relaxes via closed-form exponential asymptotic decay toward $s^*_{\text{eff}}(R_t)$:
     $$s(\Delta t) = s^*_{\text{eff}}(R_t) + (s_{\text{checkpoint}} - s^*_{\text{eff}}(R_t)) \exp\left(-\frac{\Delta t}{\tau_{\text{slow\_decay}}}\right)$$
   - Guaranteed $O(1)$ evaluation time ($\le 1\text{ms}$), infinite time-horizon stability, and perfect relational attractor alignment.
6. **Lifecycle Pause / Resume:** Freeze time during shutdown ($\Delta t = 0$). Rejected: completely violates physical-time semantics and One Continuous Life.

**Recommendation:** **Alternative 5 (Hybrid Short Replay + Asymptotic Recovery).**

---

## 8. Persistence Boundary & Classification

*(Full variable-by-variable classification in [`STATE_PERSISTENCE_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/STATE_PERSISTENCE_BOUNDARY.md))*

State is partitioned into four operational categories:
1. **Authoritative Durable State:** Must survive crash/restart with transactional durability.
2. **Reconstructible Dynamical State:** Recovered via physical-time unforced dynamics and asymptotic decay.
3. **Derived / Observational State:** Recomputed deterministically on-the-fly; never authoritative.
4. **Volatile In-Session Cache:** Cleared cleanly on restart without harming identity continuity.

Summary table:

| State Variable | Category | Must Persist? | Reconstructible? | Epoch Barrier Required? |
|---|---|---|---|---|
| **Genesis Profile (`profile.json`)** | Authoritative Durable | YES (Bit-Exact) | NO | YES (Static Anchor) |
| **Relational Vector ($R_t$)** | Authoritative Durable | YES | NO | YES |
| **Fast Tensor ($h_{\text{fast}}$)** | Reconstructible Dynamical | YES (Transient) | Decays to $0$ | YES |
| **Slow Tensor ($s_{\text{slow}}$)** | Reconstructible Dynamical | YES | Relaxes to $s^*_{\text{eff}}(R_t)$ | YES |
| **Homeostatic Energy ($E$)** | Reconstructible Physiological | YES (Metabolic) | Recovers toward $1.0$ | YES |
| **PAD Coordinates** | Derived Observational | NO (Metadata Only) | Recomputed via $W_{\text{proj}}[h, s]$ | NO |
| **SDM Memory Traces** | Authoritative Epistemic | Future Milestone | NO | Future Gate |
| **Chat History (`chat_history.json`)**| Authoritative Semantic | YES (Append-Only) | NO | YES |
| **Epoch ID / Sequence Number** | Authoritative Metadata | YES | NO | YES |

---

## 9. Temporal Consistency Model

To prevent conflation, Lucia enforces three distinct consistency layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TRIPARTITE CONSISTENCY MODEL                         │
│                                                                        │
│ 1. CAUSAL / LOGICAL-TURN CONSISTENCY                                   │
│    All persistent stores must agree on the identical turn counter      │
│    k_epoch. If relationship is at Turn N, dynamical state cannot be    │
│    at Turn N-1. Guaranteed by Epoch Barrier.                           │
│                                                                        │
│ 2. PHYSICAL-TIME CONSISTENCY                                           │
│    A single reference anchor t_checkpoint = t_commit is recorded in    │
│    the epoch manifest. Elapsed physical time Delta t is measured       │
│    from this unified anchor to the cold-boot wall clock.               │
│                                                                        │
│ 3. SEMANTIC / ATTRACTOR CONSISTENCY                                    │
│    The attractor conditioning vector R_t must match the loaded         │
│    relational state at t_boot BEFORE dynamical relaxation begins.      │
│    Guaranteed by Startup Dependency Inversion.                         │
└────────────────────────────────────────────────────────────────────────┘
```

A common logical checkpoint anchor $t_{\text{checkpoint}}$ is mandatory across dynamical and relational stores to eliminate cross-subsystem temporal tearing.

---

## 10. Memory Boundary: The SDM Volatility Decision

### 10.1 Is SDM Volatility an F-02 Blocker?
- `[ARCHITECTURAL INFERENCE]` **NO.** SDM memory persistence is **NOT an F-02 blocker**.
- **Rationale:** 
  1. F-02 is formally scoped to Category A Persistent Dynamical State ($h_{\text{fast}}, s_{\text{slow}}$) and limbic-relational continuity across restarts.
  2. In the 20-Watt Whole Brain Architecture, relational attachment ($R \in [0, 1]^4$) and limbic temperament ($s_{\text{slow}}$) operate as **subcortical structures**, whereas SDM acts as an **associative cortical memory substrate**.
  3. Relational continuity can remain valid even if cortical memory is reset between major developmental milestones (analogous to infantile amnesia or state-dependent affective bonding).
  4. Persisting 2,000–10,000 Kanerva SDM locations ($16\text{D}$ vectors) requires dedicated indexing, binary serialization, and memory-compaction logic that belongs to a dedicated Memory Persistence Phase (e.g., Phase 25 or explicit SDM persistence milestone).
  5. Expanding F-02 to include full SDM persistence would blow up the verification scope and delay the Engineering Readiness baseline.

---

## 11. Homeostasis Boundary: Metabolic Fatigue Decision

### 11.1 Does Resetting Energy to 1.0 Cause Semantic Discontinuity?
- `[ARCHITECTURAL INFERENCE]` **It depends on elapsed downtime.**
- If downtime is long ($\Delta t > 2\text{ hours}$), an energy level of $1.0$ is biologically and semantically **coherent**: an organism that has been resting offline recovers its metabolic reserves.
- However, if the process crashes and restarts within $5\text{ seconds}$ during high conversational load, waking up with $\mathcal{E} = 1.0$ represents a **metabolic tear** (instant fatigue wipe).
- **Proposed Boundary:** Persist energy $\mathcal{E}$ and cognitive load $\mathcal{C}$ in the checkpoint. During recovery, settle them asymptotically toward resting values:
  $$\mathcal{E}(\Delta t) = 1.0 - (1.0 - \mathcal{E}_{\text{checkpoint}}) \exp(-\gamma_E \Delta t)$$
  If $\Delta t \to 0$, energy is preserved. If $\Delta t \to \infty$, energy naturally settles to $1.0$.

---

## 12. PAD Source-of-Truth Decision

- `[CANONICAL ARCHITECTURAL REQUIREMENT]` **PAD is strictly derived state.**
- The canonical equation is:
  $$\text{PAD} = W_{\text{proj}} \cdot [h_{\text{fast}}; s_{\text{slow}}] + b_{\text{proj}}$$
- Serializing PAD in `data/dynamical_state.json` is useful **strictly as an observational debugging and validation metadata field**.
- On cold restart, PAD must **never** be loaded as an authoritative input that overrides $[h, s]$. It must be reprojected from the recovered $[h_{\text{fast}}, s_{\text{slow}}]$. This eliminates duplicate sources of truth.

---

## 13. Recommended Architecture: Option D/F Synthesis

We recommend adopting the **Two-Tier Coherent Checkpoint + Hybrid Asymptotic Recovery Architecture**:

```
                              STARTUP RECOVERY FLOW
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Load Tier 1: RelationshipState (data/relationship.json)              │
│    -> Verify epoch_id matches Epoch Manifest                            │
│                                                                         │
│ 2. Invert Dependency: Inject R_t directly into EmotionCore              │
│    -> EmotionCore.update_relationship_context(R_t)                      │
│                                                                         │
│ 3. Load Tier 2: DynamicalStateSnapshot (data/dynamical_state.json)       │
│    -> Verify epoch_id matches Epoch Manifest                            │
│                                                                         │
│ 4. Compute Unified Elapsed Time: Delta t = t_boot - t_checkpoint        │
│                                                                         │
│ 5. Execute Hybrid Asymptotic Recovery:                                  │
│    - If Delta t <= 60s: forward Euler ODE unforced idle                 │
│    - If Delta t > 60s: h -> 0, s relaxes asymptotically to s*_eff(R_t)  │
│    - Homeostasis: E settles asymptotically to 1.0                       │
│                                                                         │
│ 6. Reproject PAD = W_proj * [h, s]                                      │
│    -> READY FOR TURN 1 WITH PERFECT ATTRACTOR CONTINUITY                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Rejected Alternatives

1. **Option A (Status Quo):** Rejected due to verified attractor desynchronization (E-01) and causal tearing (E-04).
2. **Option B (Dynamical Only):** Rejected because relational and identity state cannot be reconstructed from $h, s$.
3. **Option C (Monolithic File):** Rejected due to I/O latency violations and fragile monolithic coupling.
4. **Option E (Event Journaling):** Rejected due to unbounded startup replay time and numerical drift.
5. **Fixed 300s Cutoff:** Rejected as an ungrounded empirical heuristic that freezes long-downtime relaxation.
6. **Lifecycle Freeze ($\Delta t = 0$):** Rejected as a direct violation of physical-time semantics.

---

## 15. Architectural Consequences

### Positive Consequences
- **Eliminates Startup Attractor Tear:** Lucia never relaxes toward stranger Philia if a relational bond exists.
- **Bounded Startup Latency:** Application boots in $\le 5\text{ms}$ even after 6 months of being powered off.
- **Strict Causal Consistency:** Multi-store writes are linked by a unified commit epoch.
- **Preserves Invariant Hierarchy:** Zero cloud dependencies, zero modifications to `data/profile.json`, and no reflective ego prompt injection.

### Negative Consequences / Engineering Costs
- Requires restructuring the instantiation sequence in `build_cognitive_orchestrator()`.
- Requires adding a lightweight epoch tracker (`data/epoch_manifest.json` or cross-file epoch headers).
- Requires implementing the closed-form asymptotic recovery function in `EmotionCore`.

---

## 16. Owner Decisions Required

The following explicit decisions are deferred to the Lucia Owner (see [`OPEN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/OPEN_DECISIONS.md)):
1. **Decision D-01:** Ratification of Option D/F Synthesis as the canonical persistence architecture.
2. **Decision D-02:** Ratification of the Hybrid Short Replay + Asymptotic Recovery model (including selection of short-replay cutoff $\tau_{\text{cutoff}} \in [30\text{s}, 60\text{s}]$).
3. **Decision D-03:** Formal deferral of SDM memory persistence to Phase 25 / future milestone.
4. **Decision D-04:** Selection of epoch coordination mechanism (shared `epoch_manifest.json` vs. header validation).
5. **Decision D-05:** Authorization of implementation scope for F-02 remediation.

---

*This document is an architecture decision analysis artifact prepared for Owner Review. Implementation is NOT authorized.*
