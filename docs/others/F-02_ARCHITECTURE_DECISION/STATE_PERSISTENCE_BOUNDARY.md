# State Persistence Boundary & Classification Specification (F-02)

**Document ID:** `SPEC-SPB-F02-20261007`  
**Classification:** State Boundary & Durability Taxonomy Specification  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`ADR_ANALYSIS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/ADR_ANALYSIS.md)  
**Governing Documents:** [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  

---

## 1. Executive Overview

This specification establishes the authoritative **State Persistence Boundary** for the Lucia companion architecture. It defines the durability, reconstructibility, mutability, and synchronization requirements for every state variable across all cognitive, limbic, physiological, and conversational subsystems.

The boundary enforces the principle that **One Continuous Life (INV-1)** does not require indiscriminate, monolithic serialization of all volatile RAM. Rather, it requires a precise mathematical taxonomy distinguishing:
1. **Authoritative Durable State:** Non-derivable invariants and cumulative history that cannot be reconstructed via physical laws or deterministic replay.
2. **Reconstructible Dynamical State:** Continuous dynamical tensors that evolve predictably across downtime according to physical-time differential equations and resting attractors.
3. **Derived / Observational State:** Epistemic reflections computed deterministically on-the-fly from underlying state.
4. **Volatile In-Session Cache:** Ephemeral operational buffers reset cleanly on restart without inducing semantic discontinuity.

---

## 2. Complete State Persistence Boundary Matrix

| # | State Variable / Store | Mathematical Domain / Type | Authoritative? | Must Persist? | Reconstructible? | Same Logical Epoch Required? | Storage Mechanism / Target Path | Primary Source & Rationale |
|---|---|---|---|---|---|---|---|---|
| 1 | **Genesis Profile** | JSON object (`{"is_onboarded": bool}`) | **YES** | **YES** | **NO** | **YES** (Static Anchor) | `data/profile.json` (Bit-Exact) | `[CANONICAL ARCHITECTURAL REQUIREMENT]` (INV-8). Immutable gate defining activation state. SHA-256 protected. |
| 2 | **Relational Vector ($R_t$)** | $\mathbb{R}^4 \in [0, 1]^4$ (Familiarity, Trust, Closeness, Reciprocity) | **YES** | **YES** | **NO** | **YES** | `data/relationship.json` (Atomic replace) | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Cumulative social bond with user. Non-derivable from limbic tensors. |
| 3 | **Relational History** | List of turn update records | **YES** | **YES** | **NO** | **YES** | `data/relationship.json` | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Audit trail for relational evolution and trend analysis. |
| 4 | **Slow Latent Tensor ($s_{\text{slow}}$)** | $\mathbb{R}^{16} \in [-1.0, 1.0]^{16}$ | **YES** (Limbic) | **YES** | **PARTIALLY** (Decays toward $s^*_{\text{eff}}(R_t)$) | **YES** | `data/dynamical_state.json` (Atomic replace) | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Represents mood, long-term affective posture, and bonded attractor displacement. |
| 5 | **Fast Reactive Tensor ($h_{\text{fast}}$)** | $\mathbb{R}^{32} \in [-1.0, 1.0]^{32}$ | **YES** (Limbic) | **YES** | **YES** (Decays to $0$ if $\Delta t \gg 5\text{s}$) | **YES** | `data/dynamical_state.json` (Atomic replace) | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Represents immediate emotional momentum and reactive arousal. |
| 6 | **Attractor Context ($\_R\_t$) in EmotionCore** | $\mathbb{R}^4 \in [0, 1]^4$ | **NO** (Shadow of $R_t$) | **NO** (Injected) | **YES** (From `RelationshipUpdater`) | **YES** | In-memory RAM (`EmotionCore._R_t`) | `[VERIFIED FROM CODE]`. Currently desynchronized on cold boot (E-01). Must be injected from $R_t$ prior to ODE recovery. |
| 7 | **Homeostatic Somatic Markers ($m_{\text{homeo}}$)** | $\mathbb{R}^4 \in [0, 1]^4$ ($E, C, T, S$) | **NO** (Bridge State) | **OPTIONAL** (Metadata) | **YES** (From Energy & PAD) | **YES** | `data/dynamical_state.json` (`state.m_homeo`) | `[ARCHITECTURAL INFERENCE]`. Somatic bridge between body and limbic ODE. Recomputed on Turn 1 Stage 5. |
| 8 | **Homeostatic Energy ($\mathcal{E}$)** | Float $\in [0.0, 1.0]$ | **YES** (Metabolic) | **YES** (Recommended) | **PARTIALLY** (Settles asymptotically to $1.0$) | **YES** | Proposed in Checkpoint / `data/dynamical_state.json` | `[VERIFIED FROM CODE]`. Currently volatile RAM resetting to $1.0$ (E-05). Must settle asymptotically based on $\Delta t$. |
| 9 | **Cognitive Load ($\mathcal{C}$)** | Float $\in [0.0, 1.0]$ | **YES** (Physiological) | **YES** (Recommended) | **YES** (Decays to $0.0$) | **YES** | Proposed in Checkpoint / `data/dynamical_state.json` | `[ARCHITECTURAL INFERENCE]`. Represents mental fatigue from rapid turns. Decays quickly during rest. |
| 10 | **Instantaneous Tension ($\mathcal{T}$)** | Float $\in [0.0, 1.0]$ | **NO** (Per-Turn) | **NO** | **YES** (Evaluated per transition) | **NO** | RAM only | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Instantaneous derived affect; cleared each turn; triggers $k=2$ deliberative depth. |
| 11 | **Free Energy Surprise ($\mathcal{S}$)** | Float $\ge 0.0$ | **NO** (Per-Turn) | **NO** | **YES** (Evaluated per transition) | **NO** | RAM only | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Active inference surprise metric; evaluated strictly on current turn transition. |
| 12 | **Projected PAD Coordinates** | $\{P, A, D\} \in [-1, 1]^3$ | **NO** (Derived) | **NO** (Stored as metadata only) | **YES** (Exact: $W_{\text{proj}}[h, s] + b$) | **NO** | `data/dynamical_state.json` (`state.pad`) | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Derived projection. Never an authoritative source of truth. |
| 13 | **Kanerva SDM Trace Accumulator** | $\mathbb{R}^{K \times M}$ ($2000 \times 16$) | **YES** (Episodic) | **FUTURE** (Phase 25) | **NO** | **FUTURE** | In-memory RAM (`SDMCore._accumulator`) | `[VERIFIED FROM CODE]`. Currently 100% volatile RAM (E-06). Defer to dedicated Memory Persistence Phase. |
| 14 | **Kanerva SDM Hard Locations** | $\{0, 1\}^{K \times D}$ ($2000 \times 64$) | **YES** (Structural) | **FUTURE** (Phase 25) | **YES** (If deterministic seed used) | **FUTURE** | In-memory RAM (`SDMCore._hard_locs`) | `[VERIFIED FROM CODE]`. Randomly regenerated on boot. Needs stable deterministic seed or persistent matrix. |
| 15 | **Affective Memory Index** | Dict[int, MemoryTrace] | **YES** (Semantic) | **FUTURE** (Phase 25) | **NO** | **FUTURE** | In-memory RAM (`AffectiveMemory._index`) | `[VERIFIED FROM CODE]`. Currently volatile RAM. Defer to dedicated Memory Persistence Phase. |
| 16 | **Chat History (User/Companion)** | JSON array of turns | **YES** (Autobiographical)| **YES** | **NO** | **YES** | `data/chat_history.json` (Append-only) | `[VERIFIED FROM CODE]`. Complete conversational transcript. Survives restart, but not injected into working memory. |
| 17 | **Dialogue Working Memory (`_history`)** | List[Dict[str, str]] ($\le 10$ turns) | **NO** (Working Cache) | **NO** | **YES** (Reconstructible from tail of chat history)| **YES** | In-memory RAM (`CognitiveOrchestrator._history`) | `[VERIFIED FROM CODE]`. Currently resets to `[]` on startup. Should be populated with last $N$ turns from `chat_history.json`. |
| 18 | **Checkpoint Timestamp (`created_at`)** | POSIX UTC Float | **YES** (Temporal) | **YES** | **NO** | **YES** | `data/dynamical_state.json` | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Physical anchor for computing elapsed offline downtime $\Delta t$. |
| 19 | **Logical Epoch ID (`epoch_id`)** | Integer / String GUID | **YES** (Causal) | **YES** | **NO** | **MANDATORY** | Proposed in Checkpoint Envelope / Manifest | `[ARCHITECTURAL INFERENCE]`. Solves E-04 causal tearing by binding multi-store commits to identical turn boundary. |
| 20 | **Schema Version (`schema_version`)** | String (`"1.0"`) | **YES** (Governance) | **YES** | **NO** | **YES** | All serialized JSON stores | `[CANONICAL ARCHITECTURAL REQUIREMENT]`. Strict schema migration and corruption rejection gate. |

---

## 3. Detailed Boundary Analysis by Subsystem

### 3.1 Subcortical Limbic Subsystem (`EmotionCore`)
- **Authoritative Variables:** Fast tensor $h_{\text{fast}} \in \mathbb{R}^{32}$, slow tensor $s_{\text{slow}} \in \mathbb{R}^{16}$, and temporal anchor $t_{\text{checkpoint}}$.
- **Reconstructibility Semantics:**
  - $h_{\text{fast}}$: Has a short time constant ($\tau_{\text{fast}} \in [0.5, 1.5]\text{s}$). If offline time $\Delta t > 10\text{s}$, $h_{\text{fast}}$ naturally decays to $\mathbf{0}$.
  - $s_{\text{slow}}$: Has a long time constant ($\tau_{\text{slow\_decay}} \approx 28.0\text{s}$). If offline time is short ($\Delta t \le 60\text{s}$), it decays numerically. If offline time is long ($\Delta t \gg 60\text{s}$), it asymptotically approaches the relationally conditioned attractor $s^*_{\text{eff}}(R_t)$.
- **Strict Invariant:** `EmotionCore` must NEVER be permitted to compute resting relaxation while referencing default baseline $R_0$. $R_t$ must be passed into `EmotionCore` before downtime integration begins.

### 3.2 Relational Subsystem (`RelationshipUpdater`)
- **Authoritative Variables:** Familiarity, Trust, Closeness, Reciprocity ($R_t \in [0, 1]^4$) and update audit log.
- **Durability:** Tier 1 Authoritative Invariant. These parameters represent cumulative interpersonal bonding that took weeks or months to develop. They must survive crash, power failure, and software upgrades with zero loss.
- **Reconstructibility:** Non-reconstructible. If lost, the relationship resets to a stranger.
- **Coordination:** Must be stamped with the same `epoch_id` as the dynamical state snapshot.

### 3.3 Physiological Subsystem (`HomeostaticEngine`)
- **Authoritative Variables:** Metabolic Energy $\mathcal{E} \in [0, 1]$ and Cognitive Load $\mathcal{C} \in [0, 1]$.
- **Classification:** Reconstructible Physiological State.
- **Recovery Rule:**
  - Energy $\mathcal{E}$ naturally replenishes during offline rest at recovery rate $\gamma_E = 0.05/\text{s}$:
    $$\mathcal{E}(t_{\text{boot}}) = 1.0 - (1.0 - \mathcal{E}_{\text{checkpoint}}) e^{-\gamma_E \Delta t}$$
  - Cognitive Load $\mathcal{C}$ naturally dissipates during offline rest at decay rate $\gamma_C = 0.08/\text{s}$:
    $$\mathcal{C}(t_{\text{boot}}) = \mathcal{C}_{\text{checkpoint}} e^{-\gamma_C \Delta t}$$
  - For long downtime ($\Delta t > 1\text{ hour}$), $\mathcal{E} \to 1.0$ and $\mathcal{C} \to 0.0$ smoothly and organically.
  - For near-instantaneous restarts ($\Delta t < 10\text{s}$), fatigue and cognitive load are preserved, preventing metabolic reset exploits.

### 3.4 Associative & Episodic Memory Subsystem (`AffectiveMemory` / SDM)
- **Authoritative Variables:** SDM Trace Accumulator, Hard Location Matrix, Index of Traces.
- **Current Reality:** 100% Volatile RAM (E-06).
- **Persistence Boundary Decision:** **DEFERRED TO DEDICATED MEMORY PHASE.**
  - SDM represents cortical associative recall, not core subcortical individuality.
  - One Continuous Life is structurally maintained across restarts by Tier 1 Relational Continuity and Tier 2 Limbic Attractor Continuity.
  - Attempting to serialize large high-dimensional SDM arrays in F-02 introduces excessive risk and I/O latency. SDM persistence must be addressed in Phase 25 with a dedicated memory compaction/indexing specification.

### 3.5 Conversational & Working Memory Subsystem
- **Authoritative Store:** `data/chat_history.json` (Append-Only Log).
- **Working Cache:** `CognitiveOrchestrator._history` (In-Memory Ring Buffer).
- **Boundary Rule:** `chat_history.json` is durable. On cold boot, `CognitiveOrchestrator` should populate its in-memory `_history` with the trailing $K=10$ turns from `chat_history.json`, restoring immediate conversational coherence without requiring full memory persistence.

---

## 4. Evidence Classification

- **[VERIFIED FROM CODE]**: Rows 1, 2, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 20.
- **[CANONICAL ARCHITECTURAL REQUIREMENT]**: Rows 1, 2, 4, 5, 10, 11, 12, 18, 20.
- **[ARCHITECTURAL INFERENCE]**: Rows 7, 9, 19, and the Asymptotic Energy settling rule.
- **[RESEARCH HYPOTHESIS]**: SDM deterministic pseudo-random seed generation vs. disk matrix serialization.
- **[OWNER DECISION REQUIRED]**: Formal adoption of Energy/Fatigue asymptotic settling and SDM persistence deferral.

---

*This document is an architecture decision analysis artifact prepared for Owner Review. Implementation is NOT authorized.*
