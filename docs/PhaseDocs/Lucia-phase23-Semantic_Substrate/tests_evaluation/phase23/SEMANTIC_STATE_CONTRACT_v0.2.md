# P23 Semantic State Contract v0.2 — P22-Inherited

> **Authoritative Phase 23 Research Specification & Semantic Contract**  
> **Status:** `[RESEARCH CONTRACT / PRE-IMPLEMENTATION]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`  
> **Predecessor Baseline:** Phase 22 Relational Research Branch (Phases 22-AL through 22-SC)  
> **Target Subsystem:** Post-Phase 22 Semantic State Formation & Continuous Communication  
> **Production Safety Invariant:** 100% Isolated. Zero modifications to `src/core/**`, `electron/**`, runtime lifecycle, or `data/profile.json` (`{"is_onboarded": false}`).

---

## 1. Executive Summary & Purpose

This contract establishes the formal baseline, research requirements, and falsification targets for **Phase 23 — Semantic Formation & Continuous Communication**. 

Phase 23 directly inherits the finalized empirical findings of the **Phase 22 research branch** (specifically Phase 22-SC, Phase 22-SSF, Phase 22-REL, Phase 22-ANCHOR, and Phase 22-RI). Rather than restarting semantic representation design from scratch or reviving disproven modeling assumptions, this document locks down established Phase 22 truths, integrates critical negative results from Phase 22-SSF, reframes the central research boundary, and preregisters explicit falsification targets for the transition from relational conditioning to rich, compositional, continuous communication.

---

## 2. Central Research Problem & Architectural Pipeline

### 2.1 The Phase 23 Research Question

> **How can Lucia transform continuous multimodal cognitive and relational states into a persistent, grounded, compositional, language-independent semantic state that supports continuous communication without making an LLM or natural-language token sequence a necessary cognitive substrate?**

### 2.2 Conceptual Progression: Phase 22 Baseline to Phase 23 Realization

```text
Phase 22 (Validated Baseline)
  Multimodal / Relational Evidence
               │
               ▼
     Relevance Gating (G4)
               │
               ▼
   RelationalConditioningState (C1/C4)
               │
═══════════════╪════════════════════════════════════════════════════════════════
Phase 23 (Active Research Horizon)
               │
               ▼
   Communicative Intention (What needs to be expressed & why)
               │
               ▼  ◄── [PRIMARY P23 RESEARCH GAP]
               │      How continuous cognitive & relational state transforms
               │      into a grounded, variable-size semantic structure.
               ▼
    Semantic Formation Layer
               │
               ▼
Persistent Grounded Compositional Semantic State
  - Grounded entity & event referents (Episodic/Semantic memory binding)
  - Variable-size compositional structures (Role/filler bindings)
  - Recursion, nested propositions, modality, temporal relations
  - Incremental delta updates without re-instantiation from scratch
               │
               ▼
Downstream Realization (Substrate-Neutral Consumers)
  ├── Symbolic Action / Policy Engine (D0)
  ├── Somatic & Physical Embodiment Controller (D2: Live2D/VRM, Gaze, Latency)
  ├── Vocal Prosody & Acoustic Parameter Synthesizer (RVC / Direct F0/Energy)
  └── Surface Linguistic Renderer (Optional SLM/LLM for multi-language text)
```

### 2.3 The Primary Research Gap

The central bridge under investigation in Phase 23 is:

```text
Continuous Cognitive State (Limbic PAD + Somatic + Relational)
                  │
                  ▼
       Communicative Intention
                  │
                  ▼
                 ???   ◄── [PHASE 23 CORE INVESTIGATION]
                  │
                  ▼
Grounded Variable-Size Semantic Structure
```

---

## 3. Epistemological Classification Ledger

In accordance with `AGENTS.md` §0 and §6, the elements of this contract are strictly classified into three mutually exclusive categories:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Category A: INHERITED / LOCKED FROM PHASE 22 (Empirical Facts)              │
│ Category B: P23 RESEARCH REQUIREMENTS (Hypotheses & Target Capabilities)   │
│ Category C: P23 UNKNOWN / FALSIFICATION TARGETS (Open Preregistered Risks)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Category A: INHERITED / LOCKED FROM PHASE 22

The following findings were empirically established in Phase 22 within their tested scope. Phase 23 treats them as **authoritative constraints** and **MUST NOT reopen or re-research them**:

1. **Substrate-Neutral Relational Semantics (`G-SC1`–`G-SC10`):**
   - Relational semantic conditioning operates completely independently of natural-language prompts, LLM tokens, or context windows.
   - Non-language consumers—specifically **D0 (Symbolic Renderer)** and **D2 (Direct Embodiment Policy)**—achieve identical $100\%$ relational fidelity with $0.00\%$ over-inference operating directly on structured evidence frames.
   - The tested consumer divergence was strictly $|D0 - D2| = 0.0$.
   - **Locked Invariant:** P23 shall NOT reopen the question: *"Does relational cognition fundamentally require an SLM/LLM or natural-language prompt?"* That question is closed within the Phase 22 tested scope.

2. **The `RelationalConditioningState` Interface Baseline:**
   - Phase 22 explicitly hands forward the **Substrate-Neutral Semantic Conditioning Interface** as a frozen contract:
     ```python
     @dataclass(frozen=True)
     class RelationalConditioningState:
         trust_tier: str            # T0_STRANGER | T1_ACQUAINTANCE | T2_COLLABORATOR | T3_COMPANION | T4_CONFIDANT
         is_guarded: bool           # True if an unhealed breach/rupture exists
         relational_stance: str     # DEFENSIVE_HOLD | RECEPTIVE_REPAIR | OPEN_ENGAGEMENT
         active_anchors: List[Dict[str, Any]]  # Milestone and repair episodic anchor references
         epistemic_confidence: float # Calibrated confidence in relational stance [0.0, 1.0]
         has_rupture: bool          # Presence of active unacknowledged rupture
         has_repair: bool           # Presence of active bilateral repair
     ```
   - Compact payload: $\sim 120–180\text{ bytes}$ in structured form (vs. $345\text{ tokens}$ in raw text). Requires zero token parsing.

3. **Renderer Independence (`semantic state → independent consumer / renderer`):**
   - The local SLM is an optional downstream surface renderer, **NOT** the owner or creator of semantic or relational state.
   - Passing relational evidence through an SLM adds zero relational cognition and slightly increases hallucination/over-inference risk ($1.5\%$ in D1 vs $0.0\%$ in D0/D2).
   - In P23, all semantic state generation must happen upstream of any text or voice rendering.

4. **Tested Cross-Language Relational Equivalence:**
   - Phase 22-SC established exact semantic equivalence across English, Vietnamese, and Japanese within its tested relational scope ($\Delta R^2 = 0.0000$, Language Gap $= 0.0$).
   - P23 shall NOT treat basic cross-language relational semantic independence as an unsolved problem. Instead, P23 tests whether this property scales to richer compositional semantic structures.

5. **C4 Hybrid Graph + HDC Inherited Baseline:**
   - Standalone dense Hyperdimensional Computing (HDC, Candidate C3) was **falsified** due to superposition crosstalk and retrieval degradation when active items $N > 5$ ($68.2\%$ recovery).
   - Candidate C4 (Hybrid Typed Graph + HDC hypervector binding) achieved optimal performance ($0.9620$ fidelity, monotonic uncertainty calibration).
   - **Baseline Rule:** C4 MUST be treated as an inherited baseline and initial candidate family, not an unexplored clean slate.
   - **Boundary Restriction:** Do NOT declare C4 universally optimal for all open-domain semantic cognition. P23 must systematically test whether C4 scales to recursive composition, negation, and variable-size structures.

6. **Preservation of Phase 22-SSF Negative Result (Rejection of Open-Loop Latent Accumulation):**
   - Phase 22-SSF demonstrated that open-loop forward accumulation of slow latent variables without observation feedback failed catastrophically ($R^2_{\text{slow}} = -0.9446$), fast states missed target ($R^2_{\text{fast}} = 0.5716 < 0.70$), and downstream flapping reached $68.8\%$.
   - **Core Research Invariant:**
     $$\text{Semantic continuity} \neq \text{open-loop accumulation of continuous latent variables}$$
   - Semantic continuity CANNOT be achieved by simply integrating continuous float vectors across time. It requires:
     $$\text{Persistent Structured State} + \text{Episodic Anchors} + \text{Evidence / Provenance} + \text{Controlled State Updates}$$

7. **Episodic Anchoring Constraint (from Phase 22-REL / Phase 22-ANCHOR):**
   - Relational continuity requires grounding in discrete episodic memory anchors (milestones, ruptures, repairs) to eliminate drift ($0.00000$ drift). Continuous scalar integration inevitably drifts unbounded over multi-session horizons.

---

### Category B: P23 RESEARCH REQUIREMENTS

Phase 23 expands the representational capacity from relational conditioning frames into general communicative semantics. P23 must design, implement in research isolation, and empirically benchmark mechanisms for:

1. **Continuous Cognitive State $\to$ Communicative Intention:**
   - Formal transformation mapping internal Coupled MT-LNN dynamics (PAD, somatic markers, homeostatic drive), active inference goals, and relational stance into an explicit communicative intention (e.g., inform, clarify, acknowledge, repair, probe, set-boundary).

2. **Communicative Intention $\to$ Variable-Size Semantic Structure:**
   - Generating discrete or semi-structured semantic representations whose topology and size scale with informational complexity, without relying on prompt generation.

3. **Grounding Semantic Entities & Events to Persistent Referents:**
   - Explicitly binding semantic tokens/nodes to persistent entities in the user's episodic memory (SDM), conceptual knowledge store, or perceptual environment.

4. **Role/Filler Binding at Rich Semantic Complexity:**
   - Robust binding of semantic arguments (Agent, Patient, Instrument, Theme, Beneficiary, Location) that avoids catastrophic binding cross-talk or vector collapse.

5. **Recursion and Nested Propositions:**
   - Representing beliefs about beliefs, conditional statements, and recursive communicative goals (e.g., *"Lucia notes that the user believes X because of event Y"*).

6. **Negation Representation:**
   - Formal, non-destructive encoding of explicit negation, denial, and absence without vector phase cancellation or retrieval blindness.

7. **Modality and Epistemic Uncertainty:**
   - Native integration of uncertainty markers (epistemic confidence, possibility, necessity, doubt) within semantic constituents rather than as post-hoc string annotations.

8. **Temporal Structure & Event Ordering:**
   - Explicit representation of past, present, ongoing, and prospective events, aspectual distinctions (completed vs progressive), and duration intervals.

9. **Coreference Across Time:**
   - Tracking entity identity and resolving anaphoric references across multi-turn conversational horizons without losing referential grounding.

10. **Incremental Semantic State Updates (Delta Updates):**
    - Modifying, enriching, or correcting an existing semantic state via localized delta updates without reconstructing the entire semantic graph from scratch on every turn.

11. **Unified Episodic and Conceptual Semantic Memory Integration:**
    - Seamlessly querying and updating both autobiographical episodic traces and generalized conceptual knowledge through a common semantic query format.

12. **Language-Independent Realization Across Modalities:**
    - Validating that the formed semantic state can be realized deterministically into multiple target languages (EN, VI, JA) and non-verbal somatic channels (facial blendshapes, prosody parameters, reaction timing) without changing the upstream state.

13. **Open-Domain Concept Acquisition Without an LLM Authority:**
    - Incorporating new, unseen concepts and vocabulary into the semantic graph while preserving non-LLM cognitive ownership and structural stability.

---

### Category C: P23 UNKNOWN / FALSIFICATION TARGETS

Phase 23 explicitly registers the following open hypotheses and preregistered failure conditions:

* **U1 — Non-LLM Intention Expansion:**
  - *Question:* Can communicative intention be expanded into a grounded, variable-size semantic structure without an SLM/LLM mediating the expansion?
  - *Falsification Condition:* If non-LLM intention expanders fail to produce syntactically valid semantic graphs with structural accuracy $\ge 80\%$ on held-out evaluation dialogues, U1 is falsified.

* **U2 — Persistent Entity Grounding Stability:**
  - *Question:* Can semantic entities remain persistent and grounded across long-lived, multi-session interaction without referential drift?
  - *Falsification Condition:* If entity referent lookup error exceeds $5.0\%$ after $N \ge 50$ conversational turns or across session boundaries, U2 is falsified.

* **U3 — C4 Representation Scalability Boundary:**
  - *Question:* Can the inherited C4 hybrid representation (Typed Graph + HDC Hypervector) scale to variable-depth recursion, nested propositions, and negation without superposition collapse?
  - *Falsification Condition:* If retrieval fidelity on nested proposition structures drops below $85\%$ or binding crosstalk exceeds $10\%$ for depth $D \ge 3$, C4 is rejected for general semantics and must be superseded.

* **U4 — Continuous Affective / Structured Semantic Coupling:**
  - *Question:* How should continuous affective (PAD), epistemic, and attentional variables modulate the discrete topology of the semantic graph without destabilizing ODE dynamics or creating boundary discontinuities?
  - *Falsification Condition:* If continuous state modulation causes state flapping $> 5.0\%$ or introduces Lyapunov instability ($\lambda_{\max} > 0$) into the MT-LNN limbic ODE, the coupling mechanism is falsified.

* **U5 — Continual State Update Drift & Graph Bloat:**
  - *Question:* Can the semantic state remain stable under continuous, incremental delta updates over extended sessions without semantic drift or uncontrolled structural growth?
  - *Falsification Condition:* If memory footprint grows unbounded ($\mathcal{O}(T)$ without sub-linear compaction) or if semantic drift exceeds $\Delta_{\text{drift}} > 0.15$ on unchanged historical facts, U5 is falsified.

* **U6 — Open-Domain Concept Grounding Autonomy:**
  - *Question:* Can open-domain concepts be acquired and grounded without an LLM acting as the cognitive authority?
  - *Falsification Condition:* If concept insertion requires LLM arbitration for structural validity or violates local 20W edge CPU budget ($\le 30\text{ ms}$), autonomous concept acquisition is falsified.

---

## 4. Representation Progression & Architecture Policy

### 4.1 Principled Representation Evolution

Phase 23 does NOT reset representation research to zero. It progresses systematically along the following lineage:

```text
Phase 22 Validated Baseline
  ├── C1: Structured Relational Frame (Tested ~120-180 bytes)
  └── C4: Hybrid Typed Graph + HDC Hypervector (Optimal in P22-SC)
               │
               ▼
Phase 23 Extension Tests
  ├── Test 1: Recursive Propositional Nesting (Depth D = 1..4)
  ├── Test 2: Role/Filler Binding Capacity & Disambiguation
  ├── Test 3: Negation, Modality & Epistemic Uncertainty Operators
  ├── Test 4: Temporal Indexing & Aspect Binding
  └── Test 5: Incremental Delta Graph Transformation
               │
               ▼
General Grounded Compositional Semantic State
  (Only promoted if C4 passes all extension tests; otherwise superseded based on empirical evidence)
```

### 4.2 Architectural Neutrality & Non-Premature Locking

To prevent locking architectural choices ahead of empirical evidence, the following paradigms remain **open research candidates** and are **STRICTLY NOT PREMATURELY LOCKED**:

- **Semantic Formalisms:** Abstract Meaning Representation (AMR), Universal Meaning Representation (UMR), Discourse Representation Theory (DRT), Vector Symbolic Architectures (VSA), Tensor Product Representations (TPR), or Category-Theoretic Graph Grammars.
- **Underlying Memory Implementations:** Specific graph databases, hypervector dimensions, or sparse distributed memory schemas.
- **Neural Frameworks:** Explicit encoder-decoder architectures, recursive neural networks, graph neural networks, or energy-based models.
- **Downstream Realization Engines:** Specific acoustic synthesis architectures, phoneme generators, or neural decoders.

Choice among these candidates must be guided strictly by empirical benchmark results against the P23 acceptance gates.

---

## 5. Phase 23 Scope Boundaries & Non-Goals

To prevent scope creep and maintain strict research discipline, Phase 23 defines explicit non-responsibilities:

| Domain | Phase 23 Responsibility? | Justification / Current Authority |
|---|---|---|
| **Re-proving basic substrate neutrality** | **NO (OUT OF SCOPE)** | Fully validated by Phase 22-SC (`G-SC1` through `G-SC10`, 10/10 passed). |
| **Re-proving that an SLM is unnecessary for relational cognition** | **NO (OUT OF SCOPE)** | Definitively resolved by Phase 22-SC ($|D0 - D2| = 0.0$). |
| **Replacing `RelationalConditioningState` without evidence** | **NO (FORBIDDEN)** | P23 inherits this contract as its relational baseline. |
| **Selecting a final production renderer** | **NO (OUT OF SCOPE)** | Renderer selection is downstream realization, not semantic state formation. |
| **Production code integration (`src/core/**`)** | **NO (STRICTLY PROHIBITED)** | Phase 23 is an isolated research milestone (`tests/evaluation/phase23/`). |
| **Genesis Onboarding Activation** | **NO (LOCKED FUTURE GATE)** | Preservation of `data/profile.json == {"is_onboarded": false}` is absolute. |
| **Solving general open-domain human-level language generation** | **NO (OUT OF SCOPE)** | Lucia focuses on grounded, relational, continuous companion communication within local 20W constraints. |

---

## 6. Pre-Registered Phase 23 Research Acceptance Gates

All Phase 23 experimental candidates will be evaluated in isolated harnesses under `tests/evaluation/phase23/` against the following pre-registered criteria:

| Gate ID | Criterion | Requirement / Metric | Target Threshold | Baseline Reference |
|---|---|---|---|---|
| **G-P23-1** | Semantic Compositionality | Accuracy of semantic role/filler binding on complex propositions | $\ge 90.0\%$ | P22-SC C1/C4 |
| **G-P23-2** | Substrate Independence | Consumer divergence between symbolic (D0) and embodied (D2) | $\le 0.02$ | P22-SC `G-SC8` ($0.0$) |
| **G-P23-3** | Cross-Language Parity | Semantic graph equivalence across English, Vietnamese, Japanese | $\Delta \text{Sim} \le 0.03$ | P22-SC `G-SC6` ($0.0$) |
| **G-P23-4** | Negation & Modality Fidelity | Correct realization of negated & uncertain propositions | $\ge 95.0\%$ | New P23 requirement |
| **G-P23-5** | Incremental Update Stability | Preservation of unchanged facts after localized graph delta | $\ge 98.0\%$ | P22-SSF negative finding |
| **G-P23-6** | Anti-Flapping Invariant | Decision/state flapping rate under continuous input stream | $\le 5.0\%$ | P22-SSF ($68.8\%$ FAIL) |
| **G-P23-7** | Referential Grounding | Accuracy of entity resolution to persistent SDM episodic anchors | $\ge 90.0\%$ | P22-ANCHOR ($76.6\%$) |
| **G-P23-8** | Edge CPU Latency SLA | P50 CPU execution time for semantic state formation | $\le 5.0\text{ ms}$ | P22-SC ($0.767\text{ ms}$) |
| **G-P23-9** | Zero GPU VRAM Invariant | Dedicated GPU memory allocation for state formation | $== 0.0\text{ MB}$ | Architectural Invariant |

---

## 7. Governance, Provenance & Production Safety Audit

- **Specification Version:** `v0.2 — P22-Inherited`
- **Supersedes:** Any informal or preliminary notes regarding continuous 12D scalar vector accumulation ($\psi_{\text{user}} \in \mathbb{R}^{12}$) from early Phase 22 exploratory studies.
- **Traceability:**
  - Inherits relational evidence, discrete trust tiers, and C1/C4 formats from [`evaluation_artifacts/phase22_sc/final_report.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase22_sc/final_report.md).
  - Inherits rejection of open-loop accumulation from [`evaluation_artifacts/phase22_ssf/final_report.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase22_ssf/final_report.md).
  - Inherits episodic anchor grounding requirements from [`evaluation_artifacts/phase22_anchor/final_report.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase22_anchor/final_report.md).
  - Consolidated in [`docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md).
- **Production Safety Verification:**
  - Files in `src/core/**`: **0 modified**
  - Files in `electron/**`: **0 modified**
  - Files in `config/**`: **0 modified**
  - Canonical state `data/profile.json`: **Bit-exact preserved** (`{"is_onboarded": false}`)
