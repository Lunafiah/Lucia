# Lucia — P23 Historical Research Record

> **Document Type:** Master Historical Index & Research Progression Ledger  
> **Status:** `[CANONICAL RESEARCH HISTORY / COMPLETED BASELINE CONSOLIDATION]`  
> **Current Active Gate:** Entering Phase 23-I (`[RESEARCH ONLY — NOT PROMOTED — NOT IMPLEMENTED]`)  
> **Preceding State:** Phase 23-H Frozen (`3eef803`)  
> **Governance Authority:** `AGENTS.md` §0, §3, §6, §7; `docs/L1_INVARIANTS.md`; `docs/00_PROJECT_OVERVIEW.md`; `docs/ARCHITECTURE.md`  
> **Production Safety Boundary:** 100% Documentation and Research Context Consolidation. Zero modifications to `src/core/**`, runtime behavior, S1–S16 pipeline, or Genesis onboarding (`data/profile.json` $\to$ `{"is_onboarded": false}`).

---

## Status / Purpose

This document serves as the authoritative, single-source canonical historical index for the entire **Phase 23 research trajectory (Phase 23-A through Phase 23-H)**. It is structured specifically for cognitive ingestion by AI research agents (Gemini, NotebookLM) and peer architectural reviewers (Ciah), ensuring that:
1. Every sub-phase from 23-A through 23-H maintains unbroken historical traceability;
2. Empirical findings, negative results, falsified hypotheses, and post-implementation audits are preserved without revisionist deletion;
3. P23-H is unambiguously recorded as **FROZEN** at commit `3eef803`;
4. P23-I is established strictly as **RESEARCH ONLY** with zero authorized implementation;
5. The core epistemic invariant is preserved across all representations: **UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY**.

---

## P23 Overall Objective

Phase 23 systematically investigates whether Project Lucia can form, maintain, manipulate, and communicate compositional meaning without natural-language token sequences or an autoregressive Large Language Model (LLM) as her cognitive substrate.

### The Core Phase 23 Research Question
> *How can Lucia transform continuous multimodal cognitive and relational states into a persistent, grounded, compositional, language-independent semantic state that supports continuous communication without making an LLM or natural-language token sequence a necessary cognitive substrate?*

### Foundational Constraints Inherited from Phase 22
- **Substrate Neutrality (Phase 22-SC):** Proven that relational intelligence and affective decision-making do not depend on an SLM, LLM prompt, or token context window. Relational semantics operates independently of natural-language tokens.
- **Relational Conditioning Baseline (Phase 22-SC):** Inherited `RelationalConditioningState` (120–180 bytes) as the irreducible non-linguistic relational payload.
- **Semantic Continuity Invariant (Phase 22-SSF):** $\text{Semantic continuity} \neq \text{open-loop accumulation of latent variables}$. Continuity requires discrete structured state, episodic anchors, provenance, and controlled state transitions.
- **Hardware Envelope:** 20-Watt Whole Brain Architecture, 100% CPU edge execution for cognitive core ($0.0\text{ MB}$ GPU VRAM), $\le 30.0\text{ ms}$ processing SLA.

---

## P23-A — Semantic State Contract & Research Foundation

### Research Question
How can the continuous multimodal cognitive and relational states established in Phase 22 be formally bounded into a persistent, grounded, compositional, language-independent semantic state contract before introducing any implementation or benchmark?

### Evidence
- Inherited empirical findings from Phase 22 research chain: Phase 22-SC (Substrate Neutrality, Candidate C4 Hybrid), Phase 22-SSF (Negative results on open-loop latent accumulation), Phase 22-REL / Phase 22-ANCHOR (Episodic anchor grounding), and Phase 22-RI (Discrete trust tiers $T_0–T_4$).
- Deconstruction of the 345-token context failure in Phase 22-CC proving that 85% was syntactic serialization overhead, with only 120–180 bytes of irreducible semantic state.

### Validated Capabilities
- Formal specification of 13 explicit research requirements (R1–R13).
- Definition of six core Phase 23 unknowns and preregistered falsification targets (U1–U6):
  - U1: Compositionality & Recursion limits;
  - U2: Cross-lingual topological invariance (EN/VI/JA);
  - U3: Coreference resolution & zero-anaphora preservation;
  - U4: Non-monotonic belief revision & contradiction detection;
  - U5: Hardware scaling envelope on 20W edge CPU;
  - U6: Multimodal grounding to continuous limbic ODE.

### Negative Findings
- Inherited Phase 22-SC negative result on Candidate C3 (Dense HDC hypervector superposition): superposition noise collapses constituent recovery when $N > 5$ anchors.
- Inherited Phase 22-SSF negative result: open-loop scalar integration diverges with $\operatorname{Var}(e) \propto t$.

### Architectural Decisions
- Decoupled semantic state from surface linguistic realization.
- Substrate-neutral consumers defined: D0 (Symbolic/Policy), D1 (Language renderer), D2 (Somatic/Physical embodiment controller).
- Preregistered Candidate C4 (Hybrid Graph + HDC Gestalt) as initial working baseline.

### Implementation Status
`[RESEARCH CONTRACT / PRE-IMPLEMENTATION]` — Isolated in `tests/evaluation/phase23/`. Zero production mutation.

### Evaluation
`NOT PRESENT / NOT APPLICABLE` (Contract and specification phase).

### Audit
`NOT PRESENT / NOT APPLICABLE`

### Required Fixes
`NOT PRESENT / NOT APPLICABLE`

### Regression / Verification
`NOT PRESENT / NOT APPLICABLE`

### Final Status
`[RESEARCH CONTRACT FROZEN]` — Superseded by v0.2 contract reflecting Phase 22 research closure.

### Known Limitations
Theoretical specification only; cannot verify operational viability without empirical microbenchmark.

### Open Questions
Can Candidate C4 scale to arbitrary recursion depth without capacity collapse or unbinding crosstalk?

### Source Documents
- [`tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md)
- [`tests/evaluation/phase23/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/README.md)

---

## P23-B — Semantic Formation Microbenchmark & Empirical Baseline

### Research Question
Which candidate representation among C1 (Pure Structured Frame), C2 (Typed Relational Graph), C3 (Dense HDC), C4 (Hybrid Graph + HDC Gestalt), and C5 (Smolensky Tensor Product Representation) satisfies the 12 evaluation gates across recursion depths $D \in [1, 4]$, associative grounding, ODE coupling, and multi-turn revision?

### Evidence
- Microbenchmark v0.2 executed across 5 preregistered seeds (`[42, 1337, 2026, 7113, 8421]`).
- Candidate C4 achieved: Depth 1 ($RF_1=93.6\%$), Depth 2 ($RF_2=87.2\%$), Depth 3 ($RF_3=86.4\%$, exceeding the $85.0\%$ gate), Depth 4 ($RF_4=83.5\%$).
- Causal Derivation CFS = 1.0; Grounding SGVR = 100%; Sub-millisecond CPU latency ($0.38\text{ ms}$).

### Validated Capabilities
- Candidate C4 proven superior to all single-paradigm candidates: topological graph adjacency prevents structural loss during deep traversal, while HDC gestalt provides continuous similarity metrics for SDM memory retrieval and limbic ODE coupling.

### Negative Findings
- **C3 (Dense HDC Superposition):** Collapsed due to crosstalk noise: $RF_1=52.6\%, RF_2=28.3\%, RF_3=22.8\%, RF_4=15.2\%$.
- **C5 (Smolensky TPR):** Collapsed due to fixed-rank tensor capacity saturation: $RF_1=100.0\%, RF_2=62.5\%, RF_3=41.7\%, RF_4=31.2\%$.
- **C1 & C2 (Pure Symbolic):** Achieved 100% traversal fidelity but provided 0 continuous similarity metrics, failing limbic resonance.
- **C4 Limitation:** HDC unbinding fidelity drops below $85\%$ threshold at depth $D \ge 4$ ($83.5\%$).

### Architectural Decisions
- Formally justified Candidate C4 (Hybrid Graph + HDC Gestalt) as Lucia's working semantic baseline, bounded at recursion depth $D \le 3$.
- Declared SLM strictly as an optional downstream surface realization renderer.

### Implementation Status
`[RESEARCH VALIDATED / BENCHMARK IMPLEMENTED]` — Isolated evaluation harness under `tests/evaluation/phase23/`.

### Evaluation
12/12 gates passed in Microbenchmark v0.2 (`evaluation_artifacts/phase23/gate_results_v0.2.json`).

### Audit
Microbenchmark v0.1 audited for scientific validity. Identified circularities, oracle leakage, and hardcoded metric evaluation. Required complete replacement with v0.2.

### Required Fixes
Authored Microbenchmark v0.2 removing circularities, adding genuine multi-turn belief revisions, OOD centroid grounding, and head-to-head candidate matrices.

### Regression / Verification
Verified across 5 random seeds; reproducible benchmark logs recorded in `evaluation_artifacts/phase23/benchmark_report_v0.2.md`.

### Final Status
`[RESEARCH VALIDATED / WORKING BASELINE JUSTIFIED]`

### Known Limitations
C4 evaluated on synthetically generated semantic graphs; does not evaluate upstream raw sensory transduction (audio, text).

### Open Questions
How does raw multimodal input (speech waveforms, text) transform into C4 without an LLM?

### Source Documents
- [`tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.1.md)
- [`tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.2.md)
- [`evaluation_artifacts/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md)
- [`evaluation_artifacts/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md)
- [`evaluation_artifacts/phase23/benchmark_report_v0.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23/benchmark_report_v0.2.md)

---

## P23-C — Raw Multimodal Input → Concept Formation Monograph

### Research Question
How can raw multimodal input (acoustic waveforms, lexical utterances in EN, VI, JA) be transformed into a language-independent C4 semantic state on a 20W edge CPU without relying on an LLM/SLM as a cognitive oracle?

### Evidence
- Investigated 12 speech & text paradigms across English, Vietnamese, and Japanese.
- Defined 8-stage boundary taxonomy ($\mathbf{x}_{\text{raw}} \to \mathbf{z}_{\text{signal}} \to \mathbf{z}_{\text{perceptual}} \to \mathcal{S}_{\text{structural}} \to \mathcal{C}_{\text{concept}} \to \mathcal{G}_{\text{grounded}} \to \mathcal{S}_{\text{C4}} \to \text{Cognition}$).
- Audited LLM independence (Classes A–D).
- Profiled 20W edge CPU feasibility: $5.1\text{ ms}$ single-core total front-end latency (SLA: $\le 30.0\text{ ms}$).

### Validated Capabilities
- **Dual-Stream Asymmetric Convergence Architecture:**
  - *Stream 1 (Acoustic Affect):* eGeMAPS 88D prosody features feeding directly into Coupled MT-LNN ODE ($0.45\text{ ms}$ CPU).
  - *Stream 2 (Structural Semantics):* Tokenization + Universal Dependencies parsing feeding deterministic thematic role transducer ($3.8\text{ ms}$ CPU).
- Both streams converge at the C4 interface with $0.0\text{ MB}$ GPU VRAM impact.

### Negative Findings
- **Sentence Embedding Fallacy Falsified:** Multilingual MiniLM 384D collapsed role-filler bindings on adversarial minimal pairs (*"The doctor examined the patient"* vs *"The patient examined the doctor"* showed $>0.91$ cosine similarity). A dense vector alone cannot represent compositional syntax.
- **Direct Speech-to-Graph Falsified:** Direct mapping from unconstrained speech waveforms to open-domain thematic graphs on 20W CPU without intermediate phonetic/lexical units is scientifically premature.

### Architectural Decisions
- Adopted Dual-Stream Asymmetric Convergence.
- Confined SLM strictly to downstream surface rendering or offline post-processing.

### Implementation Status
`[RESEARCH INVESTIGATION / WORKING HYPOTHESIS SPECIFICATION]` — Monograph and unit validation suite in `tests/evaluation/phase23/`.

### Evaluation
Unit tests passed in `test_p23c_e1_structural_preservation.py`, `test_p23c_e3_role_swap_adversarial.py`, and `test_p23c_e4_concept_covariance_regularization.py`.

### Audit
Epistemological audit refuting 10 red-team attacks on cognitive sovereignty and edge feasibility.

### Required Fixes
`NOT PRESENT / NOT APPLICABLE`

### Regression / Verification
All unit tests in `tests/evaluation/phase23/` verified green.

### Final Status
`[RESEARCH VALIDATED / MONOGRAPH COMPLETED]`

### Known Limitations
Rule-based transducers exhibit lexical and classifier limitations in unconstrained open-domain text; speech stream requires intermediate phonetic/lexical bottleneck.

### Open Questions
Which specific graph formalism (UMR-TPG, V-UMR, DRS-Graph) should serve as the primary implementation of the semantic substrate?

### Source Documents
- [`evaluation_artifacts/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md)
- [`tests/evaluation/phase23/test_p23c_e1_structural_preservation.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/test_p23c_e1_structural_preservation.py)
- [`tests/evaluation/phase23/test_p23c_e3_role_swap_adversarial.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/test_p23c_e3_role_swap_adversarial.py)
- [`tests/evaluation/phase23/test_p23c_e4_concept_covariance_regularization.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/test_p23c_e4_concept_covariance_regularization.py)

---

## P23-D — Semantic Substrate Evaluation Scaffold

### Research Question
Which candidate substrate among UMR-TPG (Universal Meaning Representation Temporal-Predicate Graph), V-UMR (Vectorized UMR), and DRS-Graph (Discourse Representation Theory) satisfies all six capability tracks: Compositionality, Cross-Lingual Convergence, Coreference, Belief Revision, Scaling to 100k facts, and Multimodal Embodiment on 20W CPU?

### Evidence
- 6 preregistered experimental tracks (EXP-01 through EXP-06) executed on isolated testbed.
- UMR-TPG: 100% role-binding at $D \le 4$; Oracle $\text{SQI} = 1.000$; $\text{CEAF}_e = 1.000, \text{EPR} = 1.000$; non-monotonic JTMS retraction $\text{RC}=1.0, \text{DPA}=1.0, \text{CRR}=0.0$; 100k facts built in $2.0\text{s}$, $0.007\text{ms}$ lookup p95, $189.2\text{ MB}$ Working Set ($\le 200\text{ MB}$ gate); Multimodal grounding $\text{CPA}=1.000, \text{CMC}=1.000$.

### Validated Capabilities
- UMR-TPG confirmed as primary candidate across all tracks.
- Token-free physical embodiment parameters (blendshape `Smile_W`, pitch shift, pacing delay) driven directly without LLM ($r = 1.000$).

### Negative Findings
- **V-UMR Memory Footprint Falsified (EXP-05):** Post-build Working Set reached **$660.3\text{ MB}$** at 100k facts, failing the $\le 350.0\text{ MB}$ gate due to Python object allocation fragmentation of dual 32D float + 1024D hypervectors.
- **V-UMR Multimodal Grounding Falsified (EXP-06):** Achieved Centroid Placement Accuracy $\text{CPA} = 0.833$ (failed $\ge 0.90$ gate) due to unconstrained Euclidean proximity causing acoustic prosody over-attribution without symbolic guardrails.
- **HDC-Pure Primary Substrate Falsified (EXP-01):** $\text{SPRR} = 0.000$ and $\text{BER} = 1.000$ across $D=1..4$ due to catastrophic clean-up memory degradation during deep unbinding.

### Architectural Decisions
- Retained UMR-TPG as primary candidate. Rejected V-UMR and HDC-Pure as standalone primary substrates.

### Implementation Status
`[RESEARCH COMPLETED / ARCHITECTURAL SYNTHESIS]` — Isolated evaluation scaffold under `tests/evaluation/evaluation_phase23d/` and `tests/evaluation/phase23d/`.

### Evaluation
All 6 experiment reports completed; cross-experiment synthesis approved in `final_synthesis.md`.

### Audit
Audit of EXP-01 depth bounds and HDC crosstalk terminology conducted; evidence consistency verified and evaluation record frozen.

### Required Fixes
Commit `2887a59` refined depth bound & terminology; commit `0b9f3ea` corrected cross-document evidence consistency.

### Regression / Verification
Verified across all 6 test suites (`test_exp01` through `test_exp06`).

### Final Status
`[RESEARCH VALIDATED / CANDIDATE DISPOSITION FROZEN]`

### Known Limitations
Evaluated on structured proposition trees and deterministic fixtures; noisy unconstrained natural language text unverified; hardware package power meter absent in host test environment.

### Open Questions
How should the UMR-TPG semantic graph be fortified and preserved across session boundaries without speculative drift?

### Source Documents
- [`tests/evaluation/evaluation_phase23d/final_synthesis.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/final_synthesis.md)
- [`tests/evaluation/evaluation_phase23d/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/README.md)
- [`tests/evaluation/evaluation_phase23d/candidate_spec.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/candidate_spec.md)
- [`tests/evaluation/evaluation_phase23d/metrics.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/metrics.md)

---

## P23-E — Conservative Semantic Fortification Across Session Boundaries

### Research Question
How can formed language-independent semantic graphs be audited, canonicalized, validated, preserved, frozen, integrity-checked, and persisted across session boundaries under the zero-ingress principle ($\text{Meaning}_{\text{out}} \subseteq \text{Meaning}_{\text{in}}$)?

### Evidence
- Production implementation in `src/core/knowledge/fortification.py` (ADR ARCH-028, commit `c2186d2`).
- Benchmarked at $2.07\text{ ms}$ median latency at 100 nodes (Target: $\le 10\text{ ms}$); $0.35\text{ MB}$ peak RAM (Target: $\le 15\text{ MB}$); $0.0\text{ MB}$ GPU VRAM. Zero novel entity insertion rate ($0.0$).

### Validated Capabilities
- UNKNOWN argument preservation (no speculative binding to concrete entities).
- AMBIGUOUS branch preservation (all competing hypotheses preserved intact).
- INFERRED provenance & non-monotonic JTMS cascade invalidation ($A \to B \to C$; collateral retraction rate $\text{CRR}=0.0$).
- Epistemic promotion rejection (`EpistemicViolationError`).
- Scope protection across NEGATION, MODAL, INTENSIONAL scopes (`ScopeViolationError`).
- Deterministic SHA-256 structural checksum and bit-rot tamper detection.

### Negative Findings
`NOT PRESENT / NOT APPLICABLE`

### Architectural Decisions
- Established conservative fortification layer owning session boundary persistence. Fully language-independent (zero string heuristics, abstract IDs).

### Implementation Status
`[VALIDATED / PRODUCTION IMPLEMENTED]` — Production code: `src/core/knowledge/fortification.py`.

### Evaluation
Unit tests: 12/12 PASS (`tests/unit/test_semantic_fortification.py`). Benchmark gates: 3/3 PASS (`tests/evaluation/phase23e/test_fortification_benchmark.py`).

### Audit
Verified against requirements A–J.

### Required Fixes
`NOT PRESENT / NOT APPLICABLE`

### Regression / Verification
Full repository regression passed; Genesis onboarding state bit-exact preserved (`{"is_onboarded": false}`).

### Final Status
`[VALIDATED / PRODUCTION IMPLEMENTED]`

### Known Limitations
Fortification protects existing meaning; it does not parse surface natural language or perform cognitive reasoning.

### Open Questions
How should surface natural language be decoupled from this language-independent substrate at runtime?

### Source Documents
- [`evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md)
- [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py)
- [`tests/unit/test_semantic_fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/unit/test_semantic_fortification.py)

---

## P23-F — Language Adapter Boundary & Semantic Substrate Contract

### Research Question
How can surface natural languages (EN, VI, JA) be strictly isolated from the Semantic Substrate, Cognitive Core, and Fortification via perimeter firewalls and a minimal driver contract?

### Evidence
- Production implementation in `src/core/language/adapter/` (ADR ARCH-029, commit `5367e02`).
- Benchmarks: Ingress gate latency $1.60\,\mu\text{s}$; Parse latency $0.0197\text{ ms}$ (EN), $0.0397\text{ ms}$ (VI), $0.0184\text{ ms}$ (JA); Realize latency $0.0085\text{ ms}$ (VI); End-to-end round trip $0.1060\text{ ms}$; Peak RAM $0.0124\text{ MB}$; $0.0\text{ MB}$ GPU VRAM.

### Validated Capabilities
- Strict closed language perimeter: only `{en, vi, ja}` admitted; unsupported languages unconditionally blocked at ingress/egress.
- Substrate purity: rejects raw token prefixes (`token:`, `word:`, `pos:`, `tag:`).
- Japanese zero-anaphora preservation: omitted subjects strictly create `EpistemicState.UNKNOWN` (`ent:unknown_agent_01`), never auto-bound to speaker.
- Vietnamese kinship honorifics ("anh", "chị") and classifiers ("cái", "con") cleanly separated from core entities.
- Ambiguity preserved as `EpistemicState.AMBIGUOUS`.

### Negative Findings
`NOT PRESENT / NOT APPLICABLE`

### Architectural Decisions
- Implemented perimeter firewall pattern; drivers implement minimal contract (`parse_to_substrate`, `realize_from_substrate`, `can_handle_language`, `validate_coverage`).

### Implementation Status
`[VALIDATED / PRODUCTION IMPLEMENTED]` — Production code: `src/core/language/adapter/`.

### Evaluation
Unit tests: 13/13 PASS (`tests/unit/test_language_adapter.py`). Falsification tests: 4/4 PASS (`tests/evaluation/phase23f/test_p23f_falsification.py`).

### Audit
Epistemic preservation audit across EN, VI, JA drivers.

### Required Fixes
`NOT PRESENT / NOT APPLICABLE`

### Regression / Verification
Full test suite passed; Genesis invariant preserved.

### Final Status
`[VALIDATED / ADAPTER BOUNDARY IMPLEMENTED]`

### Known Limitations
Current drivers cover canonical syntactic structures and core vocabulary; unconstrained open-domain slang and rare grammatical constructions require future vocabulary expansion.

### Open Questions
How does Cognitive Core query and manipulate the Semantic Graph without strings or graph traversal overhead?

### Source Documents
- [`evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md)
- [`src/core/language/adapter/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/)
- [`tests/unit/test_language_adapter.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/unit/test_language_adapter.py)
- [`tests/evaluation/phase23f/test_p23f_falsification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23f/test_p23f_falsification.py)

---

## P23-G — Semantic Substrate → Cognitive Core Contract

### Research Question
How can semantic graphs be projected into flat numeric relational terms that the Cognitive Core can evaluate using Strong Kleene logic, non-monotonic JTMS, and zero inner-loop heap allocation?

### Evidence
- Production implementation in `src/core/cognition/contract/` (ADR ARCH-030, commit `b1ee99c`).
- Benchmarks: $0.6\,\mu\text{s}$ query latency, $1.72\text{ ms}$ projection latency at 100 terms, $0.27\text{ MB}$ peak RAM, $0.0\text{ MB}$ GPU VRAM. Zero dynamic heap allocation in inner query loop via `TermArena`.

### Validated Capabilities
- Zero natural-language strings in Core: concepts, roles, scopes, entities, rules, terms are strictly 64-bit integer IDs.
- Strong Kleene 3-valued conjunction ($A \land \text{UNKNOWN}$ never produces certain truth).
- Epistemic preservation across `FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`.
- Non-monotonic JTMS cascade invalidation ($P_1 \to P_2 \to P_3 \to P_4$) while preserving independent facts.
- AMBIGUOUS branch discipline: divergent actions generate `DisambiguationSubgoal`.
- Bidirectional Graph $\leftrightarrow$ Term translation with bit-exact round-trip preservation.

### Negative Findings
`NOT PRESENT / NOT APPLICABLE`

### Architectural Decisions
- Preallocated `TermArena` with capacity enforcement (`ArenaCapacityExceededError`).
- Numeric `SymbolTable` bridging substrate string symbols to core integer IDs.

### Implementation Status
`[VALIDATED / PRODUCTION IMPLEMENTED]` — Production code: `src/core/cognition/contract/`.

### Evaluation
Unit tests: 20/20 PASS (`tests/unit/test_p23g_contract.py`). Falsification tests: 12/12 PASS (`tests/evaluation/phase23g/test_p23g_falsification.py`).

### Audit
Zero-allocation audit and Strong Kleene truth table verification.

### Required Fixes
`NOT PRESENT / NOT APPLICABLE`

### Regression / Verification
Full repository tests passed (657/657 tests).

### Final Status
`[VALIDATED / CONTRACT IMPLEMENTED]`

### Known Limitations
Passive data contract; does not execute backward goal resolution or inference on its own.

### Open Questions
How should bounded, deterministic goal-directed reasoning be executed over this term substrate?

### Source Documents
- [`evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md)
- [`src/core/cognition/contract/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/)
- [`tests/unit/test_p23g_contract.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/unit/test_p23g_contract.py)
- [`tests/evaluation/phase23g/test_p23g_falsification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23g/test_p23g_falsification.py)

---

## P23-H — Bounded Goal-Directed Reasoning Kernel & JTMS

### Research Question
How can the passive numeric term substrate be operationalized into a bounded, deterministic, goal-directed reasoning kernel with Strong Kleene three-valued logic and Justification-Based Truth Maintenance without unbounded search or heap allocation?

### Evidence
- Production implementation in `src/core/cognition/kernel/` (ADR ARCH-031, commits `6b22269` and `3eef803`).
- Benchmarks: $9.46\text{--}9.60\,\mu\text{s}$ goal resolution latency ($O(1)$ scaling up to 1,000 terms), $0.10\,\mu\text{s}$ rule lookup, $12.2\text{--}19.3\,\mu\text{s}$ cascade invalidation, $30.5\text{--}32.8\text{ KB}$ peak RAM, 0 inner-loop allocations, $0.0\text{ MB}$ GPU VRAM.

### Validated Capabilities
- Backward goal chaining with hard recursion and step bounds (`MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`).
- Deterministic cycle/loop detection using parallel ancestor stacks.
- Bounded variable binding frame (max 8 variables, bitmask tracking, zero heap allocation).
- Static Horn rules (max 4 premises, max 8 variables, max 3 args) with $O(1)$ head-predicate index (`RuleIndex`).
- Multi-justification JTMS retention and non-monotonic cascade retraction.
- Direct polar contradiction detection (`ConflictRecord`).
- Strong Kleene 4-quadrant evaluation (`FIX-23H-01`).
- Subgoal generation: missing premise/ungrounded variable $\to$ `InformationSubgoal`; divergent ambiguous branches $\to$ `DisambiguationSubgoal`.
- Real EN/VI/JA cross-lingual projection invariance (Test F6).
- 0 net persistent heap growth and 0 dynamic container growth in steady-state loop (Test F8).

### Negative Findings
`NOT PRESENT / NOT APPLICABLE`

### Architectural Decisions
- Fully numeric formal reasoning kernel decoupled from LLM/SLM. Bounded search replacing unconstrained resolution.

### Implementation Status
`[VALIDATED / PRODUCTION IMPLEMENTED / FROZEN]` — Production code: `src/core/cognition/kernel/`.

### Evaluation
Unit tests: 22/22 PASS (`tests/unit/test_p23h_kernel.py`). Mandatory falsification tests: 13/13 PASS (`tests/evaluation/phase23h/test_p23h_falsification.py`). Full repository: 661/661 PASS, property tests: 35/35 PASS.

### Audit
Post-implementation architectural audit in conversation `17db63e1-b665-47d5-b169-1ab5cb696edd`:
- **Epistemic Defect Discovered:** Unproven goal derived `FALSE` when antecedent was false, committing the fallacy of denying the antecedent and violating the invariant: **UNKNOWN must never silently become certainty**.
- **Scope Tightening:** "Zero heap allocation" narrowed to "0 net persistent heap growth / 0 dynamic container growth in steady state".
- **F6 Cross-Lingual Scope:** Verified real EN/VI/JA ingress projection.
- **F8 Multi-Step Scope:** Verified zero-growth in deep multi-step recursion.

### Required Fixes
- `FIX-23H-01`: Engine rewritten to enforce 4 sound epistemic quadrants:
  1. Antecedent False/Unproven $\to$ UNKNOWN with `InformationSubgoal`
  2. Explicit Negative Fact $\to$ FALSE with `ConflictRecord`
  3. Negative Rule Firing $\to$ FALSE with `ConflictRecord`
  4. Explicit Positive Fact $\to$ TRUE
- Resolved in commit `3eef803`.

### Regression / Verification
Added test `test_f13_four_quadrant_epistemic_verification`; all regression suites passed 100%.

### Final Status
**FROZEN at commit `3eef803`**.

### Known Limitations
- Conjunctive Horn rules only (no disjunctive heads or second-order logic).
- Bounded search (`MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`).
- P23-H reasoning does not by itself prove complete language-independent semantic representation.
- Successful tests do not prove the overall P23 hypothesis.
- Cross-lingual projection does not automatically prove semantic equivalence.
- Reasoning capability does not automatically establish grounding.
- Reasoning capability does not automatically establish continuous semantic communication.

### Open Questions
What, if anything, must exist between language-independent concept formation and the bounded reasoning substrate established by P23-H?

### Source Documents
- [`evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md)
- [`src/core/cognition/kernel/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/)
- [`tests/unit/test_p23h_kernel.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/unit/test_p23h_kernel.py)
- [`tests/evaluation/phase23h/test_p23h_falsification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23h/test_p23h_falsification.py)

---

## Cross-Phase Evolution

```text
Phase 22 Closure: Substrate-Neutral Relational Cognition [RESEARCH VALIDATED]
      │
      ▼
Phase 23-A: Semantic State Contract v0.2 (R1-R13, U1-U6 Targets)
      │
      ▼
Phase 23-B: Microbenchmark v0.2 (C4 Hybrid Baseline Justified, D <= 3)
      │
      ▼
Phase 23-C: Concept Formation Monograph (Dual-Stream Convergence, eGeMAPS + UD)
      │
      ▼
Phase 23-D: Substrate Evaluation Scaffold (UMR-TPG Selected, V-UMR & HDC Falsified)
      │
      ▼
Phase 23-E: Conservative Semantic Fortification (Session Persistence, Zero-Ingress)
      │
      ▼
Phase 23-F: Language Adapter Boundary (Strict Firewall {en, vi, ja}, Epistemic Guards)
      │
      ▼
Phase 23-G: Cognitive Core Contract (Numeric Terms, Strong Kleene K3, Static Arena)
      │
      ▼
Phase 23-H: Bounded Goal-Directed Reasoning Kernel & JTMS [FROZEN at 3eef803]
      │
      ▼
Phase 23-I: Conceptual & Relational Semantic Substrate Investigation [RESEARCH ONLY]
```

---

## Superseded / Rejected Approaches

| Approach / Candidate | Sub-Phase | Result | Failure Mechanism / Scientific Reason for Rejection |
|---|---|---|---|
| **Microbenchmark v0.1** | P23-B | Superseded | Contained circular metric evaluations and oracle leakage; replaced by audited v0.2 protocol. |
| **Dense HDC Superposition (C3)** | P23-B / P23-D | **Falsified** | Crosstalk collapse: superposition noise destroys constituent recovery when $N > 4, D > 2$ ($\text{SPRR}=0.0, \text{BER}=1.0$). |
| **Smolensky TPR (C5)** | P23-B | **Falsified** | Fixed-rank outer product matrix suffers capacity saturation and rank explosion under recursive embedding ($RF_4=31.2\%$). |
| **Pure Symbolic Frame/Graph (C1, C2)** | P23-B | **Rejected** | 0 continuous similarity metrics; cannot resonate with limbic ODE or support fast associative SDM indexing. |
| **Sentence Embedding Substrate** | P23-C | **Falsified** | Collapses thematic role-filler bindings on adversarial minimal pairs ($>0.91$ cosine similarity on subject/object swap). |
| **Direct Speech-to-Graph** | P23-C | **Rejected** | Scientifically premature on 20W edge CPU; unconstrained acoustic speech requires intermediate phonetic/lexical bottleneck. |
| **Vectorized UMR (V-UMR)** | P23-D | **Falsified** | Memory bloat ($660.3\text{ MB}$ Working Set vs $\le 350.0\text{ MB}$ gate) and multimodal over-attribution ($\text{CPA}=0.833$ vs $\ge 0.90$ gate). |
| **Denying Antecedent to False** | P23-H | **Defect / Fixed** | Engine returned FALSE when premise failed, violating **UNKNOWN must never silently become certainty**; resolved by `FIX-23H-01`. |

---

## Preserved Negative Evidence

1. **A vector alone is not a concept:** Dense embeddings fail on syntactic and thematic role-binding. Structural propositions require explicit graph topology.
2. **Superposition noise prevents deep unbinding:** Hyperdimensional Computing (HDC) is effective as a gestalt associative index, but pure dense-vector superposition cannot serve as a recursive semantic store.
3. **Continuity cannot be achieved by open-loop drift:** State accumulation without discrete structured anchors causes divergence and catastrophic relational hallucinations.
4. **Absence of proof is not proof of negation:** Formal fallacies in cognitive kernels lead directly to epistemic corruption; unproven goals must remain UNKNOWN.
5. **Continuous metric proximity causes multimodal false alarms:** Without symbolic role guardrails, continuous Euclidean distance over-attributes acoustic agitation to unrelated cognitive states.

---

## Unresolved Questions Entering P23-I

1. What, if anything, must exist between language-independent concept formation (P23-C) and the bounded reasoning substrate established by P23-H so that Lucia can form, maintain, manipulate, and communicate compositional meaning without natural-language token sequences as her cognitive substrate?
2. Does the current architecture (P23-C through P23-H) already contain the minimal sufficient substrate, or is there an unrepresented conceptual gap?
3. If a gap exists, should it be addressed in Phase 23-I, merged into an existing sub-phase, or deferred to Phase 24 (Temporal Embodiment)?
4. Can Phase 23-I be justified on empirical grounds, or should it be rejected?
