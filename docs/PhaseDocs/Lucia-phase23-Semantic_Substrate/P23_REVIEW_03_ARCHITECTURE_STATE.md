# P23 Review Pack — File 3: Architecture State & Epistemic Boundaries

> **Document 3 of 5 in the P23 Reviewer Pack**  
> **Target Audience:** Reviewer with strict reading budget / NotebookLM / Gemini Ingestion  
> **Status:** `[CANONICAL ARCHITECTURAL BOUNDARY AUDIT]`  
> **Preceding Baseline:** Phase 23-H Frozen (`3eef803`)

---

## 1. Epistemological Classification Taxonomy

To ensure absolute rigor, every architectural mechanism, boundary, and capability in Project Lucia is strictly classified into one of seven tiers:

| Tier Label | Definition & Evidentiary Standard |
|---|---|
| **`IMPLEMENTED`** | Merged into production codebase (`src/core/`), covered by unit and regression test suites, verified at runtime. |
| **`RESEARCH-VALIDATED`** | Empirically verified in isolated testbeds (`tests/evaluation/`) passing 100% of pre-registered criteria; not yet promoted to production. |
| **`SUPPORTED`** | Mathematically and structurally defensible deduction directly constrained by empirical data. |
| **`PLAUSIBLE`** | Biologically or computationally sound hypothesis consistent with current evidence but lacking formal benchmark isolation. |
| **`SPECULATIVE`** | Theoretical conjecture without empirical isolation or mathematical bounding in this repository. |
| **`UNRESOLVED`** | An active open gap where current subsystems do not yet interface seamlessly. |
| **`REJECTED`** | Explicitly falsified by benchmark measurements or prohibited by architectural invariants. |

---

## 2. Complete Architectural Boundary Audit

| Subsystem / Mechanism | Epistemic Tier | Architectural Scope & Measured Evidence |
|---|:---:|---|
| **Limbic FastLoop ODE (Coupled MT-LNN)** | **`IMPLEMENTED`** | Continuous PAD state integration every 200 ms under `_step_lock` ($\le 1\text{ms}$). |
| **SDM Episodic Memory & Decay** | **`IMPLEMENTED`** | 100,000-location Kanerva SDM, slow decay worker (60s), ecphory resonance. |
| **Language Adapter Firewall (P23-F)** | **`IMPLEMENTED`** | Perimeter ingress/egress gating ({en, vi, ja}); substrate purity auditing. |
| **Semantic Fortification Layer (P23-E)** | **`IMPLEMENTED`** | Session-boundary persistence, zero novel entity insertion, SHA-256 checksums. |
| **Cognitive Core Term Substrate (P23-G)** | **`IMPLEMENTED`** | 64-bit integer IDs, Strong Kleene conjunction, preallocated static `TermArena`. |
| **Goal Reasoning Kernel & JTMS (P23-H)** | **`IMPLEMENTED`** | Backward goal chaining, static Horn rules, non-monotonic cascade retraction. **FROZEN at `3eef803`**. |
| **Dual-Stream Sensory Front-End (P23-C)** | **`RESEARCH-VALIDATED`** | eGeMAPS prosody (88D) + UD syntactic dependency parsing ($5.1\text{ ms}$ CPU). |
| **UMR-TPG Semantic Substrate (P23-D)** | **`RESEARCH-VALIDATED`** | Temporal-Predicate Graph verified across 6 tracks (EXP-01–06); $189\text{ MB}$ @ 100k facts. |
| **Downstream SLM Surface Realization (ADR-035 / P23-D Freeze)** | **`IMPLEMENTED`** | Language generation strictly downstream of formed semantic graphs. P23-D Output Language Freeze establishes canonical production outputs: English text (`CANONICAL_TEXT_OUTPUT_LANGUAGE = 'en'`) and Japanese voice (`CANONICAL_VOICE_OUTPUT_LANGUAGE = 'ja'`) realizing in parallel via `RealizationOutput`. Dyadic companion perspective enforced. PASS WITH NOTES (89/89 PASS, 0 regression, No Category-C coupling). |
| **Direct Token-Free Embodiment Driving** | **`SUPPORTED`** | Somatic blendshapes (`Smile_W`), pitch, and latency driven without LLM ($r=1.000$). |
| **Dynamic Open-Domain Concept Induction** | **`PLAUSIBLE`** | Continuous clustering of sensory features into novel concept nodes. |
| **Human-Level General Sentience / AGI** | **`SPECULATIVE`** | **NOT CLAIMED**. Lucia is strictly a bounded operational companion system. |
| **The P23-C $\longleftrightarrow$ P23-H Dynamic Interface** | **`UNRESOLVED`** | The missing bridge between dynamic concept formation and static Horn reasoning. |
| **Dense HDC as Recursive Semantic Store (C3)** | **`REJECTED`** | Falsified in P23-B and P23-D (superposition crosstalk noise; $\text{SPRR}=0.0$). |
| **Sentence Embeddings as Cognitive Substrate** | **`REJECTED`** | Falsified in P23-C (thematic role swap collapse on adversarial minimal pairs). |
| **Vectorized UMR (V-UMR) Memory Envelope** | **`REJECTED`** | Falsified in P23-D EXP-05 ($660.3\text{ MB}$ working set exceeding $350\text{ MB}$ gate). |
| **Denying Antecedent to False in Reasoning** | **`REJECTED`** | Formally eliminated by `FIX-23H-01`; unproven goals evaluate strictly to `UNKNOWN`. |

---

## 3. Detailed Component Boundaries & Interactions

### 3.1 P23-C Concept Formation Boundary
- **Input:** Raw acoustic audio waveforms or raw text strings.
- **Process:** Stream 1 extracts eGeMAPS prosody (88D) to perturb limbic ODE. Stream 2 parses Universal Dependencies to extract predicate-argument structures.
- **Output:** Concept prototypes and relational edges.
- **Boundary Restriction:** P23-C does not execute logical deduction; it only produces perceptual/syntactic candidate representations.

### 3.2 P23-G Cognitive Core Contract Boundary
- **Input:** Language-independent `SemanticGraph` from P23-F Language Adapter or P23-E Fortifier.
- **Process:** `ProjectGraphToTerms` maps string concept symbols and relation roles to 64-bit integers using `SymbolTable`. Populates `TermArena`.
- **Output:** Queryable numeric `LogicalTerm`, `EntityTerm`, and `ScopeTerm` records.
- **Boundary Restriction:** P23-G is a passive term store; it does not chain inferences or evaluate rules autonomously.

### 3.3 P23-H Bounded Reasoning Kernel Boundary
- **Input:** Goal specification (`Goal`), working facts in `TermArena`, and static indexed rules in `RuleIndex`.
- **Process:** Backward chaining with depth ($\le 8$) and step ($\le 256$) guards. Strong Kleene K3 truth evaluation. Multi-justification JTMS retraction.
- **Output:** `GoalResult` (`TRUE`, `FALSE`, `UNKNOWN`), `InformationSubgoal` (missing premises/unbound variables), or `DisambiguationSubgoal` (competing ambiguous branches).
- **Boundary Restriction:** Operates strictly on pre-compiled static Horn rules. Cannot synthesize dynamic rules or learn new predicates at runtime.

### 3.4 P23-D Output Language Architecture & Realization Boundary
- **Input:** Multilingual user utterance entering perception boundary (EN, JA, VI, etc.). Input language does not dictate output language ($\text{input language} \ne \text{output language}$).
- **Cognitive / Semantic Substrate:** Retains strict language neutrality; zero surface language tokens or grammatical dependencies encoded into knowledge representations or limbic ODE.
- **Output:** Decoupled parallel surface realization branches via `RealizationOutput`:
  - English text (`CANONICAL_TEXT_OUTPUT_LANGUAGE = "en"`) compiled via natural prose directives and guarded fail-closed by Stage S14 `SemanticFidelityGate`.
  - Japanese voice (`CANONICAL_VOICE_OUTPUT_LANGUAGE = "ja"`) realized directly from semantic/pragmatic state via `realize_japanese_voice_text()`. Neither branch acts as a semantic intermediary for the other.
- **Perspective:** First-person dyadic companion perspective. Third-person narrator drift ("two people", "hai người", "二人") is strictly blocked.
- **P23-D Audit Result:** Status `PASS WITH NOTES`, 89/89 relevant communication + realization tests PASS, 0 regression, No Category-C Production Architectural Coupling detected.
- **Preserved Technical Notes:** Note A: helper `translate_to_japanese(safe_response)` is a surface-realization convenience path (direct semantic fallback exists; future multi-head renderer out of current scope); Note B: dead import `detect_active_language` is housekeeping technical debt.

---

## 4. Current Unresolved Interface (The P23-I Horizon)

The repository exhibits a distinct architectural discontinuity between **upstream concept formation** and **downstream formal reasoning**:

```text
┌────────────────────────────────────────────────────────┐
│ STREAM 1 & 2: PERCEPTUAL / SYNTACTIC FRONT-END (P23-C) │
│ • Raw Speech / Text → eGeMAPS / UD Dependency Trees    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
               [ UNRESOLVED INTERFACE GAP ]
               1. How do dynamic concept prototypes bind into
                  novel compositional propositions at runtime?
               2. How are situational multi-turn discourse
                  entities tracked without natural-language tokens?
               3. How does ongoing conversation modify the rule
                  space without corrupting static Horn indexing?
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ STATIC HORN REASONING KERNEL & JTMS (P23-H FROZEN)     │
│ • Static Integer Predicates & Horn Rules               │
│ • Backward Chaining & Cascade Invalidation             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ DOWNSTREAM REALIZATION & FORTIFICATION (P23-E / P23-F) │
│ • Session-boundary persistence (P23-E)                 │
│ • Strict language egress firewalls (P23-F)             │
│ • D0 Symbolic Policy, D1 SLM, D2 Somatic Embodiment    │
└────────────────────────────────────────────────────────┘
```

> **Note on Phase 23-I Research & Evidence Closure:** Gemini completed preliminary research ([`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md)), proposing transition under `FREEZE WITH PARAMETER`. That preliminary recommendation was audited and superseded by the formal evidence closure report ([`docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md)). The current architectural disposition establishes:
> - **E1 (Architecture):** Autonomous P23-I subsystem is NOT justified; full absorption is rejected; candidate disposition is a Stateless Semantic Interface Adapter / Contract Boundary (SSIS-Adapter), pending Gate 23-I-EVAL.
> - **E2 (Parameters):** $N=16$ referents is an unverified engineering heuristic; relational depth $\le 3$ is a theoretical safety envelope, not empirically verified at the boundary.
> - **E3 (Epistemic Grounding):** Confidence $\to$ assertion boundary is an unresolved blocker (continuous confidence must not silently become UNKNOWN $\to$ TRUE; defeasible GVT $\to$ JTMS ingress policy not yet specified).
> - **E4 (Runtime):** $\le 5\text{ ms}$ binding latency is unverified under active $200\text{ ms}$ MT-LNN ODE contention; $0.0\text{ MB}$ GPU VRAM preserved.
> - **Status:** `RESEARCH COMPLETED — EVIDENCE CLOSURE COMPLETED — EVIDENCE STILL INSUFFICIENT — CONTRACT NOT FROZEN — IMPLEMENTATION NOT AUTHORIZED`. Next milestone is `GATE 23-I-EVAL`. Zero production code in `src/core/` or `electron/`.

---

## 5. Interaction with Canonical Cognitive Pipeline (S1–S16)

The canonical S1–S16 Cognitive Pipeline in `CognitiveOrchestrator` (`src/core/orchestrator/`) executes sequentially under `_turn_lock`. The Phase 23 subsystems interface with this pipeline as follows:
- **Stages S1–S3 (Sensory Ingress & Lexical Analysis):** P23-F `LanguageIngressGate` verifies language admission ({en, vi, ja}) before lexical density encoding.
- **Stages S4–S6 (Limbic State & Active Inference):** P23-C Stream 1 feeds continuous prosodic affect directly into MT-LNN ODE without tokenization.
- **Stages S7–S9 (Memory Retrieval & Semantic Binding):** P23-G `TermArena` provides grounded numeric terms for SDM ecphory associative recall.
- **Stages S10–S12 (Deliberation & Reasoning):** P23-H `ReasoningKernel` executes backward goal chaining and emits `InformationSubgoal` / `DisambiguationSubgoal` to guide intention synthesis.
- **Stages S13–S15 (Realization & Safety Gate):** P23-F `LanguageEgressGate` converts intent graphs to surface realization; `BoundaryLayer` regex audits output.
- **Stage S16 (Consolidation & Session Rest):** P23-E `ConservativeSemanticFortification` validates, checks SHA-256 integrity, and freezes long-term semantic graphs.
