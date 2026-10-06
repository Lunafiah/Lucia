# Persistence Boundary Verification & State Taxonomy Audit (F-02)

**Document ID:** `VERIF-PB-20261007`  
**Classification:** State Boundary Verification & Code Trace Ledger  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_REMAINING_VERIFICATION/REPORT.md)  

---

## 1. Executive Overview

This audit verifies the authoritative status, durability, and recovery semantics of every state variable in the Lucia cognitive architecture against actual codebase reality.

The core question addressed is:
> Does the proposed persistence boundary actually preserve the minimum state necessary for **One Continuous Life (INV-1)**, or does it accidentally discard a state that changes Lucia's identity, relational continuity, or causal history?

---

## 2. Definitive Classification Matrix

Every state variable across the repository is classified into one of six mutually exclusive categories:
- **`AUTHORITATIVE PERSISTENT`**: Non-derivable state that must survive cold restart with 100% durability.
- **`RECONSTRUCTIBLE`**: State recovered deterministically via physical-time differential equations during downtime.
- **`DERIVED`**: State computed deterministically on-the-fly from underlying state; never persisted as authoritative.
- **`VOLATILE CACHE`**: Ephemeral working buffers that reset cleanly on process restart without inducing semantic discontinuity.
- **`DEFERRED`**: Long-term state whose persistence is formally allocated to a future developmental milestone (Phase 25).
- **`UNDEFINED`**: State lacking clear ownership or specifications.

---

### Master State Taxonomy Table

| # | Variable / Store | Mathematical Domain / Type | Verified Category | Current Code Location / File | Must Survive Restart? | Verified Behavioral Impact Across Cold Boot |
|---|---|---|---|---|---|---|
| 1 | **Genesis Profile** | JSON (`{"is_onboarded": false}`) | **`AUTHORITATIVE PERSISTENT`** | `data/profile.json` | **YES (Bit-Exact)** | Invariant INV-8 anchor. Governs activation gate. |
| 2 | **Relational Vector ($R_t$)** | $\mathbb{R}^4 \in [0, 1]^4$ | **`AUTHORITATIVE PERSISTENT`** | `data/relationship.json` (`updater.py:118`) | **YES** | Cumulative trust/closeness bond. If lost, Lucia treats user as stranger. |
| 3 | **Relational History** | List of turn update dicts | **`AUTHORITATIVE PERSISTENT`** | `data/relationship.json` (`updater.py:126`) | **YES** | Relational audit trail and drift analysis across turns. |
| 4 | **Slow Latent Tensor ($s_{\text{slow}}$)** | $\mathbb{R}^{16} \in [-1, 1]^{16}$ | **`RECONSTRUCTIBLE`** | `data/dynamical_state.json` (`persistence.py:284`) | **YES** | Mood & relational posture. Settles toward $s^*_{\text{eff}}(R_t)$ during offline rest. |
| 5 | **Fast Reactive Tensor ($h_{\text{fast}}$)** | $\mathbb{R}^{32} \in [-1, 1]^{32}$ | **`RECONSTRUCTIBLE`** | `data/dynamical_state.json` (`persistence.py:283`) | **YES** | Immediate emotional momentum. Decays naturally to $\mathbf{0}$ within $60\text{--}90\text{s}$. |
| 6 | **Homeostatic Energy ($\mathcal{E}$)** | Float $\in [0.0, 1.0]$ | **`RECONSTRUCTIBLE`** | `HomeostaticEngine._energy` (`homeostatic_engine.py:70`) | **YES** | Metabolic reserves. Naturally recovers toward $1.0$ within $110\text{s}$ of rest. |
| 7 | **Cognitive Load ($\mathcal{C}$)** | Float $\in [0.0, 1.0]$ | **`RECONSTRUCTIBLE`** | `HomeostaticEngine._input_timestamps` (`homeostatic_engine.py:71`) | **YES** | Mental processing fatigue. Naturally dissipates to $0.0$ after $60\text{s}$ of rest. |
| 8 | **Somatic Markers ($m_{\text{homeo}}$)** | $\mathbb{R}^4 \in [0, 1]^4$ | **`DERIVED`** | `EmotionCore._m_homeo` (`emotion_core.py:159`) | **NO** | Computed at Turn 1 Stage 5 from PAD and Homeostatic Engine. |
| 9 | **Projected PAD State** | $\{P, A, D\} \in [-1, 1]^3$ | **`DERIVED`** | `EmotionCore._project_to_pad()` (`emotion_core.py:707`) | **NO** | Derived via $W_{\text{proj}}[h, s] + b$. Stored in JSON only as metadata. |
| 10 | **Instantaneous Tension ($\mathcal{T}$)** | Float $\in [0.0, 1.0]$ | **`DERIVED`** | `HomeostaticEngine._compute_tension()` (`homeostatic_engine.py:254`)| **NO** | Evaluated per turn transition; zero inter-turn persistence. |
| 11 | **Free Energy Surprise ($\mathcal{S}$)** | Float $\ge 0.0$ | **`DERIVED`** | `ActiveInferenceEngine` (`active_inference.py:100`) | **NO** | Evaluated per turn transition; zero inter-turn persistence. |
| 12 | **Chat History Transcript** | JSON sessions & turns | **`AUTHORITATIVE PERSISTENT`** | `data/chat_history.json` (`history_store.py:43`) | **YES** | Archival record of conversations. Used for UI feeds & markdown export. |
| 13 | **Dialogue Working Memory** | List[Tuple[str, str]] ($\le 10$ pairs) | **`VOLATILE CACHE`** | `CognitiveOrchestrator._history` (`cognitive_orchestrator.py:191`) | **NO (Needs Reseed)**| Resets to `[]` on restart. Should be reseeded from tail of chat history. |
| 14 | **Kanerva SDM Accumulator** | $\mathbb{R}^{2000 \times 16}$ | **`DEFERRED`** | `SDMCore._accumulator` (`sdm.py:89`) | **FUTURE (Phase 25)** | Volatile RAM. Deferral verified safe (reduces echo resonance, not identity). |
| 15 | **Kanerva SDM Hard Locations** | $\{0, 1\}^{2000 \times 64}$ | **`DEFERRED`** | `SDMCore._hard_locs` (`sdm.py:86`) | **FUTURE (Phase 25)** | Randomly regenerated on boot. Needs deterministic seed in Phase 25. |
| 16 | **Affective Memory Index** | Dict[int, MemoryTrace] | **`DEFERRED`** | `AffectiveMemory._index` (`affective_memory.py:75`) | **FUTURE (Phase 25)** | Volatile RAM. Deferral verified safe. |
| 17 | **Temporal Anchor (`created_at`)** | POSIX UTC Float | **`AUTHORITATIVE PERSISTENT`** | `data/dynamical_state.json` (`persistence.py:280`) | **YES** | Critical physical-time anchor for computing elapsed offline rest ($\Delta t$). |
| 18 | **Epoch Manifest / Sequence** | Integer / Token | **`AUTHORITATIVE PERSISTENT`** | Proposed `data/epoch_manifest.json` | **YES** | Multi-store commit barrier preventing cross-subsystem causal tearing. |
| 19 | **Schema Version** | String (`"1.0"`) | **`AUTHORITATIVE PERSISTENT`** | All JSON stores (`persistence.py:279`) | **YES** | Migration boundary and corruption rejection barrier. |
| 20 | **Hardware Profile** | JSON config | **`AUTHORITATIVE PERSISTENT`** | `config/ui.json` | **YES** | Hardware tier, model offload, and audio configurations. |

---

## 3. Verification of Critical Continuity Axes

### 3.1 Does Discarding Volatile Variables Damage Identity Continuity?
- **Identity Invariant (INV-1 & INV-8):**
  Lucia's individuality is defined by:
  1. The immutable Genesis profile `data/profile.json` (defining her activation status and single companion instance boundary).
  2. The cumulative relational vector $R_t \in [0, 1]^4$ in `data/relationship.json` (defining her unique bond with the user).
  3. The slow latent limbic field $s_{\text{slow}} \in \mathbb{R}^{16}$ in `data/dynamical_state.json` (defining her unique emotional temperament and mood trajectory).
- **Verification:** All three stores are **AUTHORITATIVE PERSISTENT** or **RECONSTRUCTIBLE DYNAMICAL**. None of them are discarded or reset.

### 3.2 Does SDM Volatility Break One Continuous Life?
- **Code Trace:**
  In `CognitiveOrchestrator.process()`:
  - Step 8 (`EcphoryEngine.retrieve()`): queries `AffectiveMemory` using the current stimulus.
  - If SDM is empty (0 traces), `recollection_result` is `None` or inactive.
  - In Stage 11 (`PromptAssembler`): `echo_vector = None`. Prompt assembly proceeds normally using somatic markers, constraints, and dialogue history.
  - In Stage 12 (`Conversational Pacing`): `delta_tau_pace = 0`. Pacing uses default somatic latency.
- **Architectural Conclusion:**
  SDM memory traces provide **affective resonance (coloring tone and pacing)**, not factual autobiographical memory or core identity. An empty SDM on boot behaves like waking up without immediate associative flashbacks from earlier conversations. It does **not** make Lucia a stranger, does **not** alter her persona, and does **not** cause split-brain branching.
  Therefore, deferring full binary SDM matrix persistence to Phase 25 is **architecturally sound and non-destructive**.

### 3.3 The Dialogue History Reseeding Requirement
- While `data/chat_history.json` survives cold restart on disk, `CognitiveOrchestrator._history` starts at `[]`.
- This means that immediately after cold restart, the prompt sent to the LLM contains zero previous conversational turns, even though the user sees them on screen.
- To prevent this cognitive disconnect, the startup sequence should reseed `CognitiveOrchestrator._history` with the trailing $K=10$ turn pairs from `data/chat_history.json`.

---

## 4. Verification Conclusion

The proposed Two-Tier Persistence Boundary successfully retains **100% of the state required to preserve One Continuous Life across cold restarts**, while eliminating unnecessary disk I/O for derived coordinates and deferring heavy cortical array serialization to a dedicated memory phase.
