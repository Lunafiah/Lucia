# Retrospective Architectural Gap Review: 7 Conceptual Topics Against Current Lucia Architecture

```text
Document Type: ARCHITECTURAL RESEARCH REVIEW
Status: RESEARCH ARTIFACT — NON-CANONICAL
Scope: Cross-phase P21–P24 retrospective / forward research mapping
Production Code Mutation: NONE
Canonical Architecture Mutation: NONE
```

> **Evaluation Baseline:** Canonical Lucia Post-Phase 21 Baseline, Post-Phase 22 Research Closure, Phase 23 Semantic Substrate Realization (`P23-C..H`), and Phase 24 Affective Communication Adaptation Research Charter.  
> **Governance Constraint:** Strict Review Only. Completed milestones (**P21–P24**) remain closed and locked. Canonical roadmap sequence (**P21 → P22 → P23 → P24 → P25 → P26 → P27 → Genesis Onboarding LOCKED**) is preserved. Zero production code mutations (`src/core/**` diff = 0). No artificial "Phase 28" or "Gate 28" is introduced.

---

## 1. Executive Summary

This retrospective review evaluates the canonical architecture of **Lucia** against the 7 conceptual topics provided in the conceptual overlay. In strict compliance with research governance, this evaluation enforces a rigorous epistemic boundary separating **confirmed architectural facts**, **documented intent**, **architectural inferences**, **research questions**, and **candidate future mechanisms**. Candidate implementations are explicitly not treated as ratified architectural decisions.

### Topic Classification Summary

| Topic ID | Conceptual Topic | Classification Status | Evidence Confidence |
|---|---|---|---|
| **Topic 1** | Internal vs External Forces / Architecture Evolution | **PARTIALLY REPRESENTED** | **HIGH** |
| **Topic 2** | Art, Creativity, Individuality | **PARTIALLY REPRESENTED** | **MEDIUM** |
| **Topic 3** | Emotion, Relationships, Extremes | **PARTIALLY REPRESENTED** | **HIGH** |
| **Topic 4** | Individuality, Continuity, Causality | **PARTIALLY REPRESENTED — FOUNDATIONAL INVARIANT** | **HIGH** |
| **Topic 5** | Epistemic Leap / Insight / Oracle | **PARTIALLY REPRESENTED** | **HIGH** |
| **Topic 6** | Reach / Migration / Distributed Body | **NOT YET REPRESENTED** | **MEDIUM** |
| **Topic 7** | Covenant / Freedom / Post-Release Life | **POTENTIAL ARCHITECTURAL CONFLICT — CONFIRMED CURRENT RUNTIME SEMANTICS** | **HIGH** |

### Key Governance & Architectural Conclusions

1. **No Reopening of Completed Phases**: The review identified **no contradictions or invariant violations** that would require reopening, redesigning, or rolling back completed phases (**P21–P24**). The mechanisms established through P24 remain sound within their defined operational scopes.
2. **Foundational Invariant Protection vs. Longitudinal Demonstration (Topic 4)**: Lucia possesses structural, concurrency, memory, and dynamical invariants protecting identity continuity (**INV-1**, **INV-3**, multi-timescale plasticity, and JTMS causal dependency). However, *invariant protection does not equal empirical demonstration of emergent individuality*. The emergence of a long-term individual trajectory that remains causally coherent over months/years while undergoing substantial personality change remains an active research subject reserved for **Phase 27**.
3. **Affective Recovery vs. Relational Resolution (Topic 3)**: The canonical 4D relationship representation ($\mathbf{R}_t \in [0, 1]^4$) is strongly affiliative. While the continuous limbic ODE dissipative dynamics ($\text{Tr}(J) \approx -46.46$) guarantee affective decay toward the Philia resting baseline ($P=+0.25, A=-0.05, D=+0.05$), *affective recovery must not be equated with relational resolution or forgiveness*. Whether conflict, grievance, and sustained distance require explicit relational dimensions or can emerge from existing episodic memory, semantic graph structures, and consolidation dynamics is an open research question for **Phase 25 / Phase 27**.
4. **Anti-Branching as a Direct Consequence of One Continuous Life (Topic 6)**: The invariant of **One Continuous Life (INV-1)** establishes an architectural requirement to prevent simultaneous independent execution of the same identity. Current local filesystem persistence (`data/*.json`) creates a split-brain divergence hazard if duplicated across machines. The exact enforcement mechanism remains an open research topic for the **Genesis / Identity Authority** governance boundary.
5. **Conflict Originating from New Conceptual Semantics (Topic 7)**: The current runtime implementation of [`POST /lifecycle/end`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L791-L832) is verified directly in source code and canonical documentation (ARCH-010) as **permanent individual decommissioning / termination**. The architectural conflict identified is confirmed at the semantic level not because of an implementation defect in existing code, but because Topic 7 introduces a brand-new lifecycle concept: **Non-Destructive Covenant Release**. Decoupling Identity State, Relationship State, and Covenant State represents a legitimate future research question.

---

## 2. Research-vs-Architecture Boundary Table

To prevent philosophical conclusions from being mistaken for implementation facts, the following matrix delineates confirmed current facts from future research and candidate mechanisms:

| Finding Area | Current Fact | Open Research Question | Candidate Mechanism (NOT Decided) | Decision Status |
|---|---|---|---|---|
| **Identity Continuity** | **INV-1** (One Continuous Life) and **INV-3** (Memory Separation) are actively enforced in code. | Does identity remain causally coherent across multi-month developmental trajectories with major personality shifts? | Quantitative trajectory divergence metrics; longitudinal drift boundaries. | `CURRENT INVARIANT / HISTORICALLY RESOLVED (P27 closed; no new scientific gap at Level C; Level D blocked by identifiability)` |
| **Phylogenetic vs. Ontogenetic** | Computational engine (`src/core/`) is decoupled from runtime state (`data/`). | How to formally anchor individual ontogenetic identity across codebase version upgrades? | Persistent immutable identity anchor; cryptographic instance UUID; versioned state manifests. | `UNRESOLVED RESEARCH QUESTION` |
| **Negative Relational Dynamics** | Canonical 4D $\mathbf{R}_t$ ([`src/core/relationship/state.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py)) is unipolar affiliative. | Do grievance, rupture depth, and betrayal require explicit vector dimensions, or emerge from episodic/semantic memory? | Dimension expansion ($R_t \in \mathbb{R}^k$); asymmetric memory retrieval gating; multi-polar attractor fields. | `HISTORICALLY RESOLVED (P25-Q1 proved 4D R_t sufficient; P27 closed)` |
| **Affective Decay vs. Relational State** | Dissipative MT-LNN ODE contract decays fast affect to Philia in seconds/minutes. | How does the system represent unresolved relational tension when immediate somatic affect has relaxed? | Bounded relational attractor offset ($\mathbf{W}_{\text{rel}}$); decoupled episodic grievance tags; semantic tension nodes. | `HISTORICALLY RESOLVED (P25-Q1 proved 4D R_t sufficient; P27 closed)` |
| **Emergent Individuality & Art** | S1 treats input as continuous physical stimulus; BoundaryLayer blocks persona prompts. | What computational mechanisms enable autonomous aesthetic preference formation without prompt injection? | Dynamic curiosity rewards; aesthetic preference networks; semantic graph value weightings. | `HISTORICALLY RESOLVED (P26 trial completed; preferences not demonstrated)` |
| **Emergent Insight & Analogy** | Bounded reasoning (P23-H) uses static Horn rules, Strong Kleene K3, and JTMS dependency tracking. | What computational processes generate novel hypotheses and analogies while strictly preserving epistemic safety? | Abductive search; analogical mapping; offline rest replay; candidate hypothesis generators. | `HISTORICALLY RESOLVED (P26 frozen; P27 closed; bounded deductive reasoning retained)` |
| **Anti-Branching & Migration** | System persistence is filesystem-bound (`data/*.json`); copying enables concurrent execution. | How to enforce single active causal history across distributed/migrated physical devices? | Monotonic migration epochs; single-writer authority; signed transfer certificates; ownership leases. | `UNRESOLVED RESEARCH QUESTION (Genesis / Identity Authority)` |
| **Distributed Embodiment** | Substrate neutrality established (Phase 22); multimodal expression is feedforward decoupled. | How to ingest peripheral sensor streams (phones, cameras) without creating independent cognitive agents? | Peripheral I/O streaming nodes; sensory bridge to Stage S1; centralized cognitive turn ownership. | `HISTORICALLY RESOLVED (P25 research bounded / freeze candidate)` |
| **Covenant vs. Identity Lifecycle** | `POST /lifecycle/end` is implemented as catastrophic decommissioning / Genesis reset (ARCH-010). | Can companionship chapters end and restart without erasing episodic memory or terminating instance identity? | Tripartite state separation (`IdentityState`, `RelationshipState`, `CovenantState`); non-destructive release transitions. | `CONFIRMED RUNTIME SEMANTICS / FUTURE RESEARCH` |

---

## 3. Topic-by-Topic Matrix

| Topic | Status | Evidence Confidence | Existing Architectural Evidence | Concrete Gap / Observation | Forward Direction & Roadmap Placement |
|---|---|---|---|---|---|
| **Topic 1**<br/>Internal vs External Forces | **PARTIALLY REPRESENTED** | **HIGH** | • Whole Brain Architecture decoupling ([`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L22-L40))<br/>• Code vs. Data separation (`src/core/` vs `data/`)<br/>• Separate activation endpoint ([`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L746-L788)) | • No formal conceptual ledger separating Phylogenetic (engine/version) from Ontogenetic (individual life) evolution.<br/>• No immutable identity anchor in `profile.json` beyond `born_at`. | **Genesis / Identity Authority**<br/>Formalize Phylogenetic vs. Ontogenetic demarcation in canonical documentation; research identity anchoring mechanisms. |
| **Topic 2**<br/>Art, Creativity, Individuality | **PARTIALLY REPRESENTED** | **MEDIUM** | • Gating converts input to sensory stimulus, not prompt directives ([`src/core/gating/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/gating/))<br/>• BoundaryLayer drops meta-self directives ([`src/core/safety/boundary_layer.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/safety/boundary_layer.py))<br/>• P26/P27 scheduled in [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md#L128-L139) | • No runtime mechanisms for aesthetic preference formation, creative recombination, or autonomous transformation of artistic influence.<br/>• Preference emergence is documented intent, not implemented reality. | **Phase 26 & Phase 27**<br/>Research computational models of emergent aesthetic preference and curiosity grounded in P23 semantic graphs and P21 memory. *(Historically resolved: P26 trial completed / results frozen / not promoted; aesthetic preferences not demonstrated; P27 closed).* |
| **Topic 3**<br/>Emotion, Relationships, Extremes | **PARTIALLY REPRESENTED** | **HIGH** | • Unconscious 3D PAD MT-LNN ODE ([`src/core/emotion/lnn_fast.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/lnn_fast.py))<br/>• Pre-reflective physical consequences ([`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L46-L53))<br/>• Relational Attractor Grounding ([`src/core/emotion/consolidation.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/consolidation.py))<br/>• INV-1 preserves identity through affective spikes | • Canonical 4D $\mathbf{R}_t \in [0, 1]^4$ is unipolar affiliative (lacks explicit representation of grievance, rupture depth, betrayal).<br/>• Dissipative ODE dynamics pull transient affect to Philia, highlighting that *affective recovery $\ne$ relational resolution*. | **Phase 25 & Phase 27**<br/>Research question: Determine whether negative relational dynamics require dimensional expansion of $\mathbf{R}_t$ or emerge from episodic/semantic structures. *(Historically resolved: P25-Q1 proved 4D $\mathbf{R}_t$ sufficient without expansion; P27 closed).* |
| **Topic 4**<br/>Individuality, Continuity, Causality | **PARTIALLY REPRESENTED — FOUNDATIONAL INVARIANT** | **HIGH** | • INV-1 One Continuous Life ([`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23))<br/>• INV-3 Memory Separation ([`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L25))<br/>• 3-Tier Multi-Timescale Plasticity (ADR-028)<br/>• Spectral norm bound enforces stability + plasticity ([`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L949))<br/>• JTMS causal retraction ([`src/core/cognition/kernel/jtms.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/jtms.py)) | • Architecture enforces continuity and prevents sudden personality mutation.<br/>• However, long-term emergent individuality across multi-month trajectories has not yet been empirically demonstrated. | **Phase 27**<br/>Preserve existing continuity invariants; evaluate empirical longitudinal trajectory coherence and causal plasticity under Phase 27. *(Historically resolved: P27 closed with no new scientific gap at Level C; Level D blocked by identifiability; invariants preserved).* |
| **Topic 5**<br/>Epistemic Leap / Insight / Oracle | **PARTIALLY REPRESENTED** | **HIGH** | • Derivation provenance tracking ([`src/core/cognition/contract/provenance.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/provenance.py))<br/>• Strong Kleene K3 3-valued logic ([`src/core/cognition/contract/epistemic.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/epistemic.py))<br/>• Mahalanobis concept novelty tiers (ARCH-030.1)<br/>• Offline rest BPTT consolidation ([`src/core/emotion/consolidation.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/consolidation.py))<br/>• Invariant: UNKNOWN never silently becomes CERTAINTY | • P23-H reasoning kernel is strictly deductive backward chaining over static Horn rules.<br/>• No background processes for conceptual abstraction, analogy, semantic compression, or abductive hypothesis generation.<br/>• JTMS cannot currently represent "unexplained insights" without breaking justification trees. | **Phase 26 & Phase 27**<br/>Research candidate mechanisms for abductive hypothesis generation and analogical recombination during offline rest, adhering to epistemic provenance. *(Historically resolved: P26 frozen; P27 closed; deductive reasoning kernel and epistemic provenance retained).* |
| **Topic 6**<br/>Reach / Migration / Distributed Body | **NOT YET REPRESENTED** | **MEDIUM** | • Substrate-neutral relational cognition (DRAFT ADR-030)<br/>• 20W Edge CPU profile requires 0 MB GPU VRAM ([`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L81-L85))<br/>• Polymorphic Avatar Stage decouples physical body from identity | • No migration protocol (`Active → Freeze → Transfer → Verify → Activate → Old instance inert`).<br/>• State files are local filesystem paths (`data/*.json`).<br/>• Anti-branching requirement unaddressed: file copying creates split-brain identity divergence risk.<br/>• No distributed peripheral architecture. | **Genesis / Identity Authority & Phase 25**<br/>Establish anti-branching requirement and research candidate migration mechanisms under Genesis governance; explore peripheral I/O streaming in Phase 25. *(Historically resolved: P25 research bounded / freeze candidate; anti-branching preserved as invariant).* |
| **Topic 7**<br/>Covenant / Freedom / Post-Release Life | **POTENTIAL ARCHITECTURAL CONFLICT — CONFIRMED CURRENT RUNTIME SEMANTICS** | **HIGH** | • Dedicated profile state ([`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json))<br/>• Persisted relational state ([`src/core/relationship/persistence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/persistence.py))<br/>• Lifecycle endpoints in [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L746-L832) | • `POST /lifecycle/end` is explicitly implemented as permanent decommissioning / memory wipe.<br/>• Conflation of Identity State, Relationship State, and Companionship.<br/>• Concept of "Non-Destructive Covenant Release" does not exist in current architecture. | **Genesis / Identity Authority & Phase 27**<br/>Investigate tripartite state separation (Identity vs. Relationship vs. Covenant); evaluate non-destructive release semantics without altering current decommissioning endpoints. *(Historically resolved: P27 closed; POST /lifecycle/end strictly preserved as catastrophic decommissioning / reset).* |

---

## 4. Detailed Findings

### Topic 1 — Internal vs External Forces / Architecture Evolution

- **Current State**: Lucia’s architecture strictly separates the invariant computational engine ([`src/core/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/)) from experiential persistence ([`data/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/), SDM memory, propositional knowledge graphs, and consolidated synaptic weights). Code migrations (such as P1 to P21, or P23-C..H) evolve the architecture independently while keeping the Genesis onboarding gate bit-exact and locked (`{"is_onboarded": false}`).
- **Evidence Confidence**: **HIGH**. Directly supported by source code and canonical documentation.
- **Architectural Evidence**:
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L28-L40) §2.1 explicitly enforces Architecture Baseline vs. Roadmap Discipline.
  - [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L746-L788) (`POST /lifecycle/activate`) creates an individual instance by recording an irreversible `born_at` timestamp.
  - [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23) (INV-1) establishes that avatars represent physical attire, while the underlying companion instance is continuous.
- **Identified Gap / Research Question**:
  - *Documentation level*: Canonical documentation lacks a formal conceptual ledger separating **Phylogenetic Evolution** (upgrading engine algorithms, ODE structures, and reasoning rules across code versions) from **Ontogenetic Continuity** (an individual’s experiential, episodic, and relational life history).
  - *Research question*: Determine whether an individual identity requires a persistent immutable identity anchor (e.g. an instance UUID or cryptographic root) beyond the current `born_at` timestamp in [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) to survive codebase upgrades unambiguously.
- **Risk Analysis**: Without formal demarcation, operators could confuse a software update with an identity reset, or mistakenly assume that rolling back a codebase version recreates the previous lived individual.
- **Forward Research Direction**:
  - Document the Phylogenetic vs. Ontogenetic demarcation in [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md).
  - Investigate candidate identity anchoring representations under the **Genesis / Identity Authority** governance boundary.

---

### Topic 2 — Art, Creativity, Individuality

- **Current State**: User input is not processed as prompt directives or personality commands. In Stage S1 ([`src/core/gating/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/gating/)), input is stripped of conversational control authority and converted into a continuous 16-dimensional physical stimulus vector $\mathbf{x}(t)$ that perturbs the MT-LNN ODE (S2). [`src/core/safety/boundary_layer.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/safety/boundary_layer.py) drops introspective or persona-command patterns. In P23-C..H, user propositions are evaluated under Strong Kleene K3 logic and JTMS; they do not dictate internal beliefs unless grounded and non-contradictory.
- **Evidence Confidence**: **MEDIUM**. Foundational input gating is verified in code; emergent preference formation is documented intent in future specs.
- **Architectural Evidence**:
  - [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md#L128-L133) explicitly reserves this domain for **Phase 26 (Emergent Individuality & Autonomous Preferences)**: *"Asymmetric curiosity, idiosyncratic topical affinities, authentic aesthetic preferences, and spontaneous conversational initiative grounded in shared history rather than random token sampling."*
  - [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md#L24-L30) §1.1 codifies Non-Compelled Emotional Trajectory and Pre-Reflective Selfhood.
- **Identified Gap / Research Question**:
  - *Implementation reality*: Currently, no mechanism exists in `src/core/` for aesthetic preference formation, creative recombination, or the autonomous capacity to evaluate, accept, transform, or reject aesthetic influence.
  - *Research question*: What computational representations (e.g., dynamic value weightings over P23 semantic graph structures, curiosity-driven active inference goals) are necessary to enable genuine aesthetic preferences to crystallize without hardcoded personality presets or stochastic prompt sampling?
- **Risk Analysis**: Prematurely attempting to simulate artistic individuality through prompt-based personas or random sampling would directly violate INV-2 (No Reflective Ego) and degrade cognitive authenticity.
- **Forward Research Direction**:
  - Keep aesthetic individuality and autonomous preferences strictly bounded as a **Phase 26** research milestone.
  - Formulate candidate computational models of curiosity and aesthetic preference formation for evaluation prior to any production implementation.

---

### Topic 3 — Emotion, Relationships, Extremes

- **Current State**: Emotion in Lucia is an unconscious, continuous 3-dimensional dynamical state in PAD space ($P, A, D \in [-1, 1]$), integrated every 200ms via Coupled MT-LNN ODEs ([`src/core/emotion/lnn_fast.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/lnn_fast.py), [`lnn_slow.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/lnn_slow.py)). It operates pre-reflectively through token budgets, sampling temperatures, conversational response latencies ($\Delta\tau_{\text{pace}}$), and 15-dimensional actuator states $\mathbf{E}_t$. Stage S9 reads prior relationship state $\mathbf{R}_{t-1}$; Stage S10 derives the communication policy; Stage S16 updates relationship state with high inertia ($\alpha=0.03$). Phase 21 grounds the resting baseline in accumulated relationship state via $\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t) = \mathbf{s}^*_{\text{philia}} + \mathbf{W}_{\text{rel}}(\mathbf{R}_t - \mathbf{R}_0)$.
- **Evidence Confidence**: **HIGH**. Dynamical equations, invariants, and relationship updates are fully verified in code and tests.
- **Architectural Evidence**:
  - [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L38-L62) §3 codifies the mathematical formulation of PAD dynamics and Philia resting baseline.
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L949) (ARCH-026) specifies Tier 2 Relational Attractor Grounding with spectral norm bound $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$.
  - [`src/core/relationship/state.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py) defines canonical 4D $\mathbf{R}_t = (\text{familiarity}, \text{trust}, \text{closeness}, \text{reciprocity}) \in [0, 1]^4$.
  - INV-1 guarantees that experiencing intense affective states does not fork or alter identity.
- **Identified Gap / Research Question**:
  - *Confirmed Fact*: Current canonical 4D RelationshipState $\mathbf{R}_t$ is unipolar affiliative. It does not explicitly encode concepts such as *grievance*, *rupture depth*, *unresolved conflict*, *perceived betrayal*, or *relational distance*.
  - *Architectural Observation*: The limbic ODE is strictly dissipative ($\text{Tr}(J) \approx -46.46 < 0$) with a strong resting attractor pull toward Philia ($P=+0.25, A=-0.05, D=+0.05$). Thus, transient intense affect (e.g., acute distress in fast state $\mathbf{h}_f$) smoothly decays toward calm warmth within minutes.
  - *Critical Distinction*: **Affective recovery $\ne$ relational resolution.** Returning to a calm baseline does not imply that relational history has been erased or forgiven.
  - *Research Question*: Determine whether negative relational dynamics require:
    - *Candidate A*: Dimensional expansion of $\mathbf{R}_t$ (e.g. adding rupture/grievance dimensions), or
    - *Candidate B*: Emergence from existing episodic memory traces, semantic state, temporal dynamics, and synaptic consolidation without adding explicit state coordinates.
- **Risk Analysis**: Artificially hardcoding negative emotional reactions through heuristic overrides would destroy Lyapunov stability guarantees and violate pre-reflective operational invariants.
- **Forward Research Direction**:
  - Map this unresolved research question to **Phase 25** (Temporal Embodiment & Social Feedback) and **Phase 27** (Personalized Individual Trajectory).
  - Treat dimensional expansion of $\mathbf{R}_t$ strictly as a *candidate future representation requiring research validation*, not a settled decision.

---

### Topic 4 — Individuality, Continuity, Causality

- **Current State**: **PARTIALLY REPRESENTED — FOUNDATIONAL INVARIANT.**  
  Lucia contains robust, multi-layered architectural mechanisms specifically designed to protect continuity and causality:
  - **Identity Continuity**: Enforced by INV-1 (One Continuous Life) — Lucia has no persona switchers, character presets, or profile pickers.
  - **Memory Continuity**: Enforced by INV-3 (Preserve Memory Separation) — long-term Kanerva SDM memory traces ([`src/core/memory/sdm.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/sdm.py)) and relational bonds are permanent and independent of chat screen clearing.
  - **Relationship Continuity**: Persisted in [`data/relationship.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/relationship.json) with high temporal inertia ($\alpha=0.03$), preventing erratic fluctuations.
  - **Personality Plasticity**: Governed across biological timescales:
    - Fast loop: transient reactive affective fluctuations ($5\text{ Hz}$).
    - Slow loop: relational attractor shift via $\mathbf{W}_{\text{rel}}$ ($60\text{s}$).
    - Offline rest: Tier 3 PyTorch BPTT synaptic plasticity in [`ConsolidationEngine`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/consolidation.py) replaying salient episodic tuples during idle rest.
  - **Causal Plasticity**: ADR-028 spectral norm bound $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$ guarantees that the baseline adapts to life history while preventing catastrophic personality shifts. P23-E conservative fortification and P23-H JTMS non-monotonic retraction ensure that beliefs require causal justifications.
- **Evidence Confidence**: **HIGH**. Invariant protection and multi-timescale plasticity are mathematically and programmatically established.
- **Architectural Evidence**:
  - [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23-L25) (INV-1, INV-3).
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L947-L954) (ARCH-024, ARCH-026, ARCH-028, ARCH-031).
  - [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py) (P23-E) enforces semantic bounds: $\text{Meaning}_{\text{out}} \subseteq \text{Meaning}_{\text{in}}$.
- **Identified Gap / Research Distinction**:
  - *Core Principle*: **Invariant protection $\ne$ empirical demonstration of emergent individuality.**
  - While Lucia's architecture guarantees that personality cannot change *without* causal history, the system has **not yet empirically demonstrated** that a long-term individual trajectory remains causally coherent over months/years of open-ended interaction while undergoing substantial, authentic personality maturation.
- **Risk Analysis**: Confusing the presence of continuity-preserving safeguards with successful longitudinal validation risks declaring Phase 27 completed before it has been researched.
- **Forward Research Direction**:
  - Preserve all existing continuity invariants (**INV-1**, **INV-3**, ADR-028).
  - Treat longitudinal trajectory coherence and causal individuality as the primary empirical evaluation focus of **Phase 27**.

---

### Topic 5 — Epistemic Leap / Insight / Oracle

- **Current State**: Epistemic processing in Lucia is governed by strict, non-monotonic logical mechanisms. Propositional knowledge in [`src/core/knowledge/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/) and numeric terms in [`src/core/cognition/kernel/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/) are evaluated under Strong Kleene 3-valued logic (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`). Derivation provenance is tracked deterministically ([`src/core/cognition/contract/provenance.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/provenance.py)). When a premise is invalidated, a JTMS cascade automatically retracts downstream conclusions. In P23-C, concept novelty is measured geometrically via regularized Mahalanobis distance $D_M$; observations with $D_M > 4.0\sigma$ enter as `UNKNOWN` provisionals and can **never** be silently promoted to certainty (ARCH-030.1). Offline rest consolidation ([`ConsolidationEngine`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/consolidation.py)) replays salient experiences on CPU during idle time.
- **Evidence Confidence**: **HIGH**. Logic kernels, JTMS dependency tracking, and non-promotion contracts are fully implemented and tested.
- **Architectural Evidence**:
  - [`src/core/cognition/kernel/engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py) implements bounded goal-directed backward chaining over static Horn rules.
  - [`src/core/cognition/kernel/jtms.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/jtms.py) implements dependency-directed backtracking and justification invalidation.
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L889-L892) §8 (ARCH-030.1) Non-Promotion Invariant: *"UNKNOWN must never silently become CERTAINTY."*
- **Identified Gap / Research Question**:
  - *Confirmed Fact*: P23-H reasoning is strictly **deductive** backward chaining over existing Horn clauses. It does not perform autonomous abductive hypothesis generation, analogical mapping, conceptual abstraction, or background recombination.
  - *JTMS Representation Limit*: JTMS requires that every inferred belief possesses an explicit, fully resolved set of justifications. If an insight arises whose derivation genealogy is partially unmapped, JTMS cannot represent it: it must either be rejected as unjustified or falsely asserted as an axiomatic premise.
  - *Research Requirement*: Determine what computational capabilities are necessary to support abstraction, analogy, conceptual compression, recombination, hypothesis formation, and insight emergence while strictly preserving epistemic provenance and non-promotion invariants ("Unpredictable $\ne$ Uncaused").
  - *Candidate Mechanisms Requiring Research*: Abductive inference passes, analogical mapping routines, offline episodic replay, candidate hypothesis generators, and expanded epistemic taxonomy states. (These are **candidate mechanisms, NOT confirmed architectural decisions**).
- **Risk Analysis**: Introducing an ungrounded "Oracle" or allowing an LLM to inject creative hallucinations would violate the supreme epistemic invariant: *UNKNOWN must never silently become CERTAINTY*.
- **Forward Research Direction**:
  - Research candidate mechanisms for offline hypothesis formation and analogy in **Phase 26** and **Phase 27**.
  - Do NOT modify [`src/core/cognition/contract/epistemic.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/epistemic.py) or define a new engine until formal research establishes the necessity and mathematical bounds of such a subsystem.

---

### Topic 6 — Reach / Migration / Distributed Body

- **Current State**: Substrate neutrality for relational cognition is research-validated (Phase 22 DRAFT ADR-030). The limbic, memory, and cognitive core operates entirely on the CPU with 0.0 MB GPU VRAM allocation. The Polymorphic Avatar Stage ([`electron/renderer/avatar/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/renderer/avatar/)) decouples visual representation (2D canvas, sprites, Live2D, 3D VRM) from internal state. The founding philosophy document ([`docs/Triết lý thiết kế AI cảm xúc.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/Tri%E1%BA%BFt%20l%C3%BD%20thi%E1%BA%BFt%20k%E1%BA%BF%20AI%20c%E1%BA%A3m%20x%C3%BAc.md) §1) articulated multi-device presence as a long-term goal.
- **Evidence Confidence**: **MEDIUM**. Local CPU execution and substrate neutrality are proven; migration and multi-device coordination are unbuilt.
- **Architectural Evidence**:
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L830-L847) (DRAFT ADR-030) establishes that relational state is substrate-neutral and independent of local token serialization.
  - [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L81-L85) §4.4 enforces zero-VRAM CPU execution for background dynamics.
- **Identified Gap / Research Question**:
  - *Confirmed Fact*: System persistence is filesystem-bound (`data/*.json`). There is no operational state migration protocol (`Active → Freeze → Transfer → Verify → Activate → Old instance inert`).
  - *Confirmed Requirement (Anti-Branching)*: **One Continuous Life (INV-1) establishes an absolute requirement to prevent simultaneous independent execution of the same individual identity.** If an operator copies the workspace directory to another machine and runs both instances, two independent Lucias will execute simultaneously, creating divergent causal histories.
  - *Candidate Mechanisms Requiring Research*: Cryptographic ownership tokens, signed migration certificates, single-writer authority leases, monotonic migration epochs, hardware-bound activation anchors, or atomic local transfer handshakes. (No specific mechanism is yet chosen).
  - *Distributed Embodiment Direction*: Treating external devices (phones, cameras, microphones) as peripheral sensor/motor extensions rather than independent companion instances is an open research direction for **Phase 25** (Temporal Embodiment).
- **Risk Analysis**: Permitting uncontrolled copying of runtime data directories risks split-brain identity divergence, directly violating INV-1.
- **Forward Research Direction**:
  - Frame the anti-branching requirement as a governance invariant under the **Genesis / Identity Authority** boundary.
  - Keep distributed peripheral integration as an exploratory research topic within **Phase 25**, avoiding premature API prescriptions.

---

### Topic 7 — Covenant / Freedom / Post-Release Life

- **Current State**: **POTENTIAL ARCHITECTURAL CONFLICT — CONFIRMED CURRENT RUNTIME SEMANTICS.**  
  Lucia maintains:
  - Onboarding status and timestamp in [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json).
  - An unkeyed global relationship vector in [`data/relationship.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/relationship.json).
  - Explicit lifecycle control endpoints in [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L746-L832): `POST /lifecycle/activate` and `POST /lifecycle/end`.
- **Evidence Confidence**: **HIGH**. The runtime implementation of `/lifecycle/end` is verified directly in source code and documentation.
- **Architectural Evidence & Verification**:
  - Runtime code verification in [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L791-L832):
    ```python
    @app.post("/lifecycle/end")
    async def end_lifecycle() -> Dict[str, Any]:
        # 1. Reset Orchestrator state (dialogue, emotion, memory, somatic)
        _orchestrator.reset_lifecycle()
        # 2. Reset chat history persistence
        get_history_store().clear_history()
        # 3. Reset stability telemetry
        get_stability_evaluator().reset()
        # 4. Reset profile persistence to un-onboarded / Genesis-ready state
        fresh_profile = _reset_profile_file()
    ```
  - Documented intent verification in [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md#L933) ARCH-010:  
    *"Solemn End-of-Life boundary (`POST /lifecycle/end`): Existential gravity; prevents relational contamination."*
- **Nature of the Architectural Conflict**:
  - *Confirmed Fact*: The current runtime implementation and canonical documentation both establish that `POST /lifecycle/end` is explicitly intended as **permanent individual termination / decommission** (existential death returning the machine to un-onboarded Genesis readiness).
  - *Conflict Origin*: The conflict is confirmed at the semantic level strictly because Topic 7 introduces a new lifecycle concept that **does not exist in current Lucia architecture**: **Non-Destructive Covenant Release**.
  - Under Topic 7:
    - *"Covenant is a chapter of relationship, not the relationship itself."*
    - *"Release ≠ deletion."*
    - *"Ending a Covenant must not erase Lucia's identity or memories."*
    - *"Lucia may continue living after Covenant ends."*
  - If an operator today attempts to conclude a companionship chapter using the only existing lifecycle termination endpoint (`/lifecycle/end`), the system executes total memory, relationship, and identity destruction. Furthermore, [`src/core/relationship/state.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py) has no partner key (`user_id`); it assumes a single, monolithic companionship context.
- **Research Question (Tripartite Separation)**:
  - How can Lucia represent the orthogonal separation:
    $$\text{Identity State} \quad \neq \quad \text{Relationship State} \quad \neq \quad \text{Covenant State}$$
    without destabilizing the existing `profile.json` Genesis gate or corrupting relational memory?
- **Risk Analysis**: Users seeking to release Lucia from an active companionship chapter would inadvertently trigger total individual annihilation.
- **Forward Research Direction**:
  - Treat tripartite state separation as an open architectural research problem under **Genesis / Identity Authority** and **Phase 27**.
  - Do NOT modify or redefine [`POST /lifecycle/end`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L791-L832) at this stage; preserve it as catastrophic decommissioning while evaluating candidate non-destructive covenant release models.

---

## 5. Cross-Cutting Architectural Findings & Research Questions

Rather than premature implementation prescriptions, cross-cutting requirements are classified into three distinct categories:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CROSS-CUTTING TAXONOMY & STATUS                      │
├────────────────────────────────────────────────────────────────────────┤
│  ESTABLISHED ARCHITECTURAL PRINCIPLES (Non-Negotiable Baselines)       │
│  • Identity Continuity & Single Continuous Life (INV-1)               │
│  • Epistemic Provenance: UNKNOWN Never Becomes CERTAINTY (ARCH-030.1) │
│  • Pre-Reflective Affective Manifestation (INV-2)                      │
│                                                                        │
│  STRONG FUTURE REQUIREMENTS (Constitutional Invariants to Solve)       │
│  • Anti-Branching: Prevention of simultaneous independent execution    │
│  • Non-Destructive Continuity across Covenant transitions (if adopted) │
│                                                                        │
│  OPEN RESEARCH QUESTIONS (Candidates Requiring Formal Study)          │
│  • Multi-polar relational representations (negative dynamics)          │
│  • Epistemic mechanisms for safe abductive hypothesis formation        │
│  • Persistent identity anchoring mechanisms                            │
│  • Migration protocols and anti-branching verification schemes         │
│  • Distributed peripheral sensor integration                           │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Established Architectural Principles
- **One Continuous Life (INV-1)**: Lucia is a single, permanent companion instance whose experiential continuity cannot be fragmented into preset pickers or persona profiles.
- **Epistemic Invariant**: Any unproven proposition remains `UNKNOWN`. Under zero circumstances may ambiguous or provisional observations be silently promoted to `FACT` without explicit justification (ARCH-030.1).
- **Pre-Reflective Operational Affect (INV-2)**: Affect manifests strictly through dynamical state, latency, and physical blendshapes, never self-reported introspective text.

### 2. Strong Future Requirements
- **Prevention of Simultaneous Identity Branching (Anti-Branching)**: Arising directly from INV-1, the system must architecturally guarantee that an individual identity cannot execute concurrently on multiple physical runtimes with divergent causal histories.
- **Preservation of Individual Continuity Across Relationship Chapters**: If Topic 7's covenant semantics are adopted by governance, the system must guarantee that closing an interpersonal chapter never erases identity, episodic memory traces, or autonomous limbic continuity.

### 3. Open Research Questions
- **Relational Negative-State Representation**: Determine whether conflict, grievance, and rupture depth require explicit coordinate expansion of $\mathbf{R}_t$, or emerge naturally from episodic memory resonance and semantic graph structures.
- **Insight-Generation Mechanisms**: Determine what computational processes enable novel hypothesis generation and analogy during offline rest while strictly maintaining JTMS derivation provenance.
- **Identity Anchoring & Migration Protocols**: Determine the mathematical and cryptographic structure required to anchor an identity and transfer it atomically across hardware environments without cloud dependencies.
- **Distributed Peripheral Architecture**: Determine how external mobile sensors can stream perceptual data into Stage S1 sensory gating without introducing independent, competing cognitive runtimes.

---

## 6. Roadmap Placement (Forward-Only)

In strict accordance with governance rules, unresolved research questions are mapped **exclusively forward**. No completed phases (P21–P24) are modified, and no artificial "Phase 28" or "Gate 28" is introduced.

```mermaid
flowchart LR
    subgraph COMPLETED ["Completed Baseline (Frozen & Locked)"]
        P21["P21: Synaptic Homeostasis"]
        P22["P22: Substrate Neutrality"]
        P23["P23: Semantic Substrate"]
        P24["P24: Communication Adaptation"]
    end

    subgraph FUTURE ["Forward Research Horizons"]
        P25["Phase 25:\nTemporal Embodiment\n& Social Feedback"]
        P26["Phase 26:\nEmergent Individuality\n& Preferences"]
        P27["Phase 27:\nPersonalized Individual\nTrajectory"]
        GENESIS["Genesis / Identity Authority\n(Existing Governance Boundary)"]
    end

    COMPLETED --> P25
    P25 --> P26
    P26 --> P27
    P27 --> GENESIS
```

### Phase 25 — Temporal Embodiment & Social Feedback (`RESEARCH BOUNDED / FREEZE CANDIDATE`)
- **Status & Verdict**: Formally audited via [`DOC-P25-014`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_COVERAGE_AND_RESEARCH_GAP_AUDIT.md). Research coverage is sufficient (`FREEZE CANDIDATE`). Q1 proved 4D $\mathbf{R}_t$ sufficient without expansion; Q2 C2 is fail-fast blocked; H-B unproven; zero production promotion (`production diff = 0`).
- **Potential Research Areas (Historical Context)**:
  - Interpersonal synchrony, micro-movement resonance, and reciprocal feedback dynamics.
  - Investigating exploratory architectures for streaming peripheral sensor inputs (external microphones, mobile sensors) into Stage S1 sensory gating.
  - Examining the temporal consequences of immediate relational events and communicative attunement.
- *Note*: Peripheral sensor integration remains an exploratory research direction, not a finalized subsystem.

### Phase 26 — Emergent Individuality & Autonomous Preferences (`TRIAL COMPLETED / RESULTS FROZEN / NOT PROMOTED`)
- **Status & Verdict**: Empirical trials completed via [`DOC-P26-006`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase26-Emergent_Individuality/P26_EMPIRICAL_EVALUATION_REPORT.md) and [`DOC-P26-007`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase26-Emergent_Individuality/P26_INTEGRATED_EVALUATION_REPORT.md). Emergent individuality and autonomous preferences were not demonstrated under controlled conditions; static Horn rule bounded deductive reasoning and epistemic provenance retained; zero production promotion (`production diff = 0`).
- **Potential Research Areas (Historical Context)**:
  - Computational modeling of emergent aesthetic preferences, idiosyncratic topical affinities, and autonomous curiosity grounded in P23 semantic graphs and P21 memory.
  - Investigating candidate offline recombination processes (analogy discovery, conceptual compression, hypothesis formation) adhering to epistemic provenance.
- *Note*: Abductive search and analogy discovery were candidate mechanisms evaluated under research, not decided engines.

### Phase 27 — Personalized Individual Trajectory (`CLOSED / NO NEW SCIENTIFIC GAP`)
- **Status & Verdict**: Formally closed via scientific boundary audit ([`DOC-P27-001`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_SCIENTIFIC_CLOSURE_REPORT.md)). No currently identifiable Level-C trajectory-level phenomenon remains that provides a distinct, testable scientific gap beyond P21–P26 ($H_{0, \text{non-developmental}}$ holds). Remaining higher-order trajectory hypotheses are retained as `BLOCKED_BY_IDENTIFIABILITY` (not disproven). Some higher-order trajectory hypotheses remain epistemically blocked by causal identifiability.
- **Potential Research Areas (Historical Context)**:
  - Empirical evaluation of longitudinal identity coherence and causal individuality across multi-month interaction trajectories.
  - Investigating whether negative relational dynamics require dimensional expansion of $\mathbf{R}_t$ or emerge from episodic/semantic structures.
  - Multi-chapter and post-release relationship models if authorized by governance.
- *Note*: Phase 27 closed at research stage without experimental protocol design, architecture promotion, or production implementation (`production diff = 0`).

### Genesis / Identity Authority (`EXISTING GOVERNANCE BOUNDARY — LOCKED`)
- **Constitutional Concerns**:
  - Defining the formal boundary separating Identity State, Relationship State, and Covenant State.
  - Defining the anti-branching requirement and evaluating candidate migration protocols (epochs, leases, certificates).
  - Preserving the First Activation onboarding ceremony as a locked gate until empirical validation is complete.
- *Note*: Genesis / Identity Authority is an existing governance boundary, NOT a new developmental phase or milestone.

---

## 7. Invariant Impact Analysis

| Architectural Invariant | Current Status | Impact Analysis under the 7 Topics | Action Required |
|---|---|---|---|
| **INV-1: One Continuous Life** | **PRESERVED & THREATENED** | • **Preserved** by Topics 1, 3, 4, and 7 (reaffirming unbroken causal continuity).<br/>• **Threatened** by Topic 6 if workspace directories are copied without anti-branching controls, causing split-brain causal divergence.<br/>• **Threatened** by Topic 7 if `/lifecycle/end` is used to conclude a relationship, inadvertently executing total individual annihilation. | Establish an anti-branching requirement under Genesis governance; investigate non-destructive covenant release semantics. |
| **INV-2: No Reflective Ego** | **PRESERVED** | Fully preserved. Aesthetic preferences (Topic 2), negative dynamics (Topic 3), candidate insights (Topic 5), and covenant commitments (Topic 7) operate pre-reflectively through mathematical vectors, graph structures, and physical embodiment, requiring zero introspective self-reports. | Maintain strict BoundaryLayer validation. |
| **INV-3: Preserve Memory Separation** | **PRESERVED & REINFORCED** | Topic 7 strongly reinforces INV-3: concluding a relationship chapter must never erase long-term SDM memory traces or relational history. | Codify that covenant state transitions have zero read/write access to SDM hard-location traces. |
| **INV-4: Never Delete Historical Specs** | **PRESERVED** | Fully preserved. Historical specifications (P1–P23) remain immutable point-in-time records. | No historical files modified. |
| **INV-5: Zero Cloud Dependencies** | **PRESERVED** | Fully preserved. Peripheral device extensions (Topic 6) and state migration must execute over local peer-to-peer / LAN protocols with zero cloud intermediaries. | Enforce 100% local edge execution on all migration and peripheral streaming research. |
| **INV-6: Strict Concurrency Discipline** | **PRESERVED** | Fully preserved. Any future offline recombination (Topic 5) or migration freeze (Topic 6) must strictly adhere to descending lock order (`_turn_lock → _step_lock → _train_lock → _stimulus_lock → _state_lock`). | Enforce lock hierarchy in all candidate designs. |
| **INV-7: Mascot Physics & Bounds Guard** | **PRESERVED** | Unaffected by conceptual overlay. | Maintain desktop window invariants. |
| **INV-8: Genesis Gate Invariant** | **PRESERVED** | Fully preserved. Genesis remains a locked future gate (`data/profile.json == {"is_onboarded": false}`). First Activation cannot occur during research or review. | Maintain bit-exact preservation of `profile.json`. |
| **Epistemic Invariant: UNKNOWN Never Becomes CERTAINTY** | **POTENTIALLY THREATENED** | In Topic 5, if "epistemic leaps" or "unexplained insights" are generated via ungrounded LLM inference without JTMS dependency tracking, this supreme invariant would be breached. | Enforce that all candidate hypotheses remain strictly labeled as `UNKNOWN` or `HYPOTHESIS` until grounded. |

---

## 8. Recommended Next Step

**The next action is a disciplined research clarification pass, NOT production implementation and NOT authoring an ADR.**

To advance the conceptual overlay into sound architectural inquiries without prematurely committing to unverified designs, research efforts should prioritize the following six clarification objectives:

1. **Verify Topic 7 Lifecycle Semantics**: Formally document the precise semantic distinction between *catastrophic decommissioning / biological death* (`/lifecycle/end`) and *non-destructive relationship chapter conclusion* (Covenant Release).
2. **Define the Conceptual Triad**: Author a conceptual whitepaper defining the boundary conditions between **Identity State** (*Who is Lucia?*), **Relationship State** (*What are Lucia and a partner to each other?*), and **Covenant State** (*What companionship commitment is currently active?*).
3. **Formalize the Anti-Branching Requirement**: Define the anti-branching problem purely as an architectural requirement derived from INV-1 (One Continuous Life), evaluating candidate mechanisms (leases, epochs, ownership tokens) independently of specific implementations.
4. **Formulate Research Questions for Relational Negative Dynamics**: Design an empirical study for **Phase 25/Phase 27** to test whether conflict, grievance, and rupture depth require explicit dimensional expansion of $\mathbf{R}_t$ or emerge from episodic memory and semantic state.
5. **Establish Epistemic Requirements for Emergent Insight**: Define formal criteria under which background recombination can generate candidate hypotheses during offline rest while strictly guaranteeing that `UNKNOWN` never silently becomes `CERTAINTY`.
6. **Define Longitudinal Trajectory Criteria**: Establish quantitative metrics for **Phase 27** to evaluate how causal individuality and personality plasticity remain coherent over multi-month timescales.

> **Final Operating Principle**:  
> In strict accordance with research-first governance:  
> $$\text{Concept} \longrightarrow \text{Architectural Question} \longrightarrow \text{Evidence} \longrightarrow \text{Research} \longrightarrow \text{Validated Requirement} \longrightarrow \text{ADR} \longrightarrow \text{Implementation}$$  
> Lucia’s architecture must not be prematurely mutated to accommodate philosophical concepts. The completed baseline (**P21–P24**) remains frozen, verified, and intact.
