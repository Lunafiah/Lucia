# State Persistence Boundary Specification (F-02 Final)

**Document ID:** `SPEC-SPB-FINAL-20261007`  
**Classification:** Canonical State Taxonomy Specification (Pending Ratification)  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`FINAL_RATIFICATION_PACKAGE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_FINAL_RATIFICATION/FINAL_RATIFICATION_PACKAGE.md)  

---

## 1. Executive Summary

This specification establishes the authoritative state persistence boundary under the Option D/F architecture. It categorizes every state variable into explicit durability classes and defines the exact synchronization requirements across process boundaries.

---

## 2. Definitive State Taxonomy Matrix

| State Entity | Exact Type / Domain | Durability Category | Storage Target / Mechanism | Code Provenance & Rationale |
|---|---|---|---|---|
| **Genesis Profile** | JSON (`{"is_onboarded": false}`) | **`AUTHORITATIVE PERSISTENT`** | `data/profile.json` (Bit-Exact) | `[CANONICAL REQUIREMENT]` (INV-8). Immutable activation anchor. SHA-256 guarded. |
| **Relational Vector ($R_t$)** | $\mathbb{R}^4 \in [0, 1]^4$ | **`AUTHORITATIVE PERSISTENT`** | `data/relationship.json` (Atomic replace) | `[CANONICAL REQUIREMENT]`. Cumulative familiarity, trust, closeness, reciprocity. |
| **Relational Update History** | List of turn records | **`AUTHORITATIVE PERSISTENT`** | `data/relationship.json` | `[CANONICAL REQUIREMENT]`. Relational drift history. |
| **Slow Latent Tensor ($s_{\text{slow}}$)** | $\mathbb{R}^{16} \in [-1, 1]^{16}$ | **`RECONSTRUCTIBLE`** | `data/dynamical_state.json` | `[CANONICAL REQUIREMENT]`. Limbic mood & attractor displacement. Relaxes toward $s^*_{\text{eff}}(R_t)$. |
| **Fast Reactive Tensor ($h_{\text{fast}}$)** | $\mathbb{R}^{32} \in [-1, 1]^{32}$ | **`RECONSTRUCTIBLE`** | `data/dynamical_state.json` | `[CANONICAL REQUIREMENT]`. Emotional momentum. Decays naturally toward $\mathbf{0}$. |
| **Homeostatic Energy ($\mathcal{E}$)** | Float $\in [0.0, 1.0]$ | **`RECONSTRUCTIBLE`** | Checkpoint snapshot metadata | `[VERIFIED FROM CODE]`. Recovers toward $1.0$ within $110\text{s}$ of rest (`homeostatic_engine.py:46`). |
| **Cognitive Load ($\mathcal{C}$)** | Float $\in [0.0, 1.0]$ | **`RECONSTRUCTIBLE`** | Checkpoint snapshot metadata | `[VERIFIED FROM CODE]`. Dissipates toward $0.0$ after $60\text{s}$ of rest (`homeostatic_engine.py:284`). |
| **Projected PAD Coordinates** | $\{P, A, D\} \in [-1, 1]^3$ | **`DERIVED`** | Recomputed on boot via $W_{\text{proj}}[h, s]$ | `[CANONICAL REQUIREMENT]`. Expressive projection. Serialized in JSON only as non-authoritative metadata. |
| **Somatic Markers ($m_{\text{homeo}}$)** | $\mathbb{R}^4 \in [0, 1]^4$ | **`DERIVED`** | Recomputed Turn 1 Stage 5 | `[VERIFIED FROM CODE]`. Bridge state between body and limbic ODE. |
| **Instantaneous Tension ($\mathcal{T}$)** | Float $\in [0.0, 1.0]$ | **`DERIVED`** | Ephemeral RAM | `[CANONICAL REQUIREMENT]`. Turn-transition metric; zero inter-turn persistence. |
| **Free Energy Surprise ($\mathcal{S}$)** | Float $\ge 0.0$ | **`DERIVED`** | Ephemeral RAM | `[CANONICAL REQUIREMENT]`. Active inference prediction error; zero inter-turn persistence. |
| **Autobiographical Transcript** | JSON sessions & turns | **`AUTHORITATIVE PERSISTENT`** | `data/chat_history.json` (Append-only) | `[VERIFIED FROM CODE]`. Permanent chat history log for UI feeds and Markdown export. |
| **Dialogue Working Memory** | List[Tuple[str, str]] | **`VOLATILE CACHE`** | In-RAM `CognitiveOrchestrator._history` | `[VERIFIED FROM CODE]`. Reseeded on startup from tail ($K$) of `chat_history.json`. |
| **Kanerva SDM Accumulator** | $\mathbb{R}^{2000 \times 16}$ | **`DEFERRED`** | Volatile RAM (`sdm.py:89`) | `[STRONG ARCHITECTURAL RECOMMENDATION]`. Cortical recall substrate; persistence deferred to Phase 25. |
| **Kanerva SDM Hard Locations** | $\{0, 1\}^{2000 \times 64}$ | **`DEFERRED`** | Volatile RAM (`sdm.py:86`) | `[STRONG ARCHITECTURAL RECOMMENDATION]`. Regenerated on boot; deterministic seed deferred to Phase 25. |
| **Checkpoint Temporal Anchor** | POSIX UTC Float | **`AUTHORITATIVE PERSISTENT`** | `data/dynamical_state.json` (`created_at`) | `[CANONICAL REQUIREMENT]`. Physical-time reference for downtime integration ($\Delta t$). |
| **Logical Epoch Manifest** | Integer counter & token | **`AUTHORITATIVE PERSISTENT`** | `data/epoch_manifest.json` | `[STRONG ARCHITECTURAL RECOMMENDATION]`. Commit barrier guaranteeing cross-store causal coherence. |
| **Schema Version** | String (`"1.0"`) | **`AUTHORITATIVE PERSISTENT`** | All domain JSON files | `[CANONICAL REQUIREMENT]`. Structural integrity barrier. |

---

## 3. Detailed Boundary Decisions

### 3.1 Episodic Memory: The SDM Deferral Recommendation
- **Classification:** `STRONG ARCHITECTURAL RECOMMENDATION / OWNER DECISION`.
- **Reasoning:**
  - Relational identity and interpersonal trust are preserved with 100% durability in `data/relationship.json`.
  - Limbic affective identity and mood posture are preserved in `data/dynamical_state.json`.
  - Kanerva SDM traces provide associative ecphoric resonance (echo vectors and pacing nudges). An empty SDM on boot attenuates immediate associative flashbacks on Turn 1, but does **not** alter Lucia's core identity or relational bond.
  - Deferring high-dimensional binary array serialization to Phase 25 avoids I/O latency bottlenecks and risk of corruption in F-02.
  - Final ratification belongs to the Owner.

### 3.2 Conversational History: Archive vs. Working Memory
- **Classification:**
  - `data/chat_history.json` = Persistent autobiographical archive.
  - `CognitiveOrchestrator._history` = Reconstructible working memory context.
- **Reseeding Policy:**
  - Startup initializes `_history` by reading the last $K$ turn pairs from `chat_history.json`.
  - $K$ is designated as an **implementation configuration parameter** (defaulting to 10), **NOT** an immutable architectural invariant.
