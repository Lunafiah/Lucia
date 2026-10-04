# Lucia — Master Source Map & Provenance Ledger

> **Canonical Repository-Wide Architectural Claim-to-Evidence Traceability Map**  
> **Status:** `[CANONICAL REPOSITORY MAP]`  
> **Purpose:** Unbroken Provenance Chains Connecting Core Architectural Claims to Living Canon, Formal Decisions, Raw Evidence, Implementation Code, and Test Verification

---

## 1. Provenance Architecture Standard

Every significant architectural claim in Lucia must be backed by an explicit, unbroken provenance chain:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      PROVENANCE CHAIN SCHEMA                           │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Architectural Claim    ── What principle or invariant is claimed?   │
│ 2. Canonical Document     ── Where is this fact authoritatively owned? │
│ 3. Research / Decision    ── Which research spec or ADR authorized it? │
│ 4. Evaluation Evidence    ── What empirical data/benchmark proves it?  │
│ 5. Production Code        ── Which exact module executes it?           │
│ 6. Verification Suite     ── Which automated test proves correctness?  │
└────────────────────────────────────────────────────────────────────────┘
```

Where any link in the chain is incomplete or unverified, it is explicitly classified as `UNPROVEN`, `RESEARCH ONLY`, or `MISSING PROVENANCE` rather than assuming certainty.

---

## 2. Core Architectural Subsystems Provenance Map

### 2.1 Limbic Fast Loop: Coupled Multi-Timescale Liquid Neural Network (MT-LNN ODE)
- **Architectural Claim**: Emotional state is an unconscious, continuous physiological dynamic system operating in 3D PAD space governed by coupled fast ($\mathbb{R}^{32}$) and slow ($\mathbb{R}^{16}$) ODEs with dissipative Lyapunov contraction ($\text{Tr}(J) \approx -46.46$) relaxing to the Philia attractor ($+0.25, -0.05, +0.05$).
- **Canonical Document**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.2; [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) §3.
- **Governing Decision**: ADR-026 (Coupled MT-LNN), ARCH-001, ARCH-024.
- **Research Specification**: [`docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESEARCH_PROPOSAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESEARCH_PROPOSAL.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESULTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESULTS.md); Phase 19 Acceptance Report (Commit `19db677`).
- **Production Code**: [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py), [`src/core/emotion/homeostatic_engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/homeostatic_engine.py).
- **Verification Suite**: `tests/unit/test_emotion_dynamics.py`, `tests/evaluation/evaluation_phase19/test_mt_lnn.py`.

---

### 2.2 Metabolic Homeostasis & Somatic Behavioral Conditioning
- **Architectural Claim**: Metabolic budgeting computes somatic markers (Cognitive Load $\mathcal{C}$, Energy $\mathcal{E}$, Tension $\mathcal{T}$) to dynamically constrain language generation: token budgets (`max_tokens`), temperature, reasoning depth ($k=2$ when $\mathcal{S}>0.60$), and conversational pacing latency without self-reported introspective declarations.
- **Canonical Document**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.3; [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) §1.
- **Governing Decision**: ADR-015 (Causal Active Inference), ARCH-014.
- **Research Specification**: [`docs/PhaseDocs/lucia-phase1-core/Phase_1_design.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase1-core/Phase_1_design.md).
- **Evaluation Evidence**: `tests/unit/test_homeostasis.py`; Phase 9 Ablation Test Report.
- **Production Code**: [`src/core/emotion/homeostatic_engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/homeostatic_engine.py).
- **Verification Suite**: `tests/unit/test_homeostasis.py`, `tests/ablation/test_causal_active_inference.py`.

---

### 2.3 Sparse Distributed Memory (SDM) & Closed-Loop Affective Recollection
- **Architectural Claim**: Episodic memory utilizes a 1,000-location Kanerva SDM (1000-bit address, 64-dim content) with salience-resistant 60s decay ($\lambda_{\text{eff}}$). Closed-loop recollection couples retrieved episodic slow-field traces ($\mathbf{s}_{\text{enc}} \in \mathbb{R}^{16}$) into the slow MT-LNN ODE via an auxiliary forcing pulse ($\mathbf{W}_{\text{rec}} = 0.35\mathbf{I}_{16}$, 4.0s pulse).
- **Canonical Document**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.5.
- **Governing Decision**: ADR-003, ADR-027 (Closed-Loop Affective Recollection), ARCH-025.
- **Research Specification**: [`docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESEARCH_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESEARCH_SPEC.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESULTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESULTS.md); Phase 20 Acceptance Report (Commit `f20420a`).
- **Production Code**: [`src/core/memory/sdm.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/sdm.py), [`src/core/memory/ecphory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py), [`src/core/memory/decay.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/decay.py).
- **Verification Suite**: `tests/unit/test_sdm.py`, `tests/unit/test_ecphory.py`, `tests/evaluation/evaluation_phase20/test_recollection.py`.

---

### 2.4 Tier 3 Offline Synaptic Consolidation & Relational Attractor Grounding
- **Architectural Claim**: Multi-timescale plasticity separates fast reactive hidden adaptation from slow relational grounding. Tier 2 shifts slow resting equilibrium $\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t)$ bounded by spectral norm $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$. Tier 3 runs offline CPU backpropagation-through-ODE (`torchdiffeq.odeint`) in a standalone engine, swapping weights under sub-1ms `_train_lock` with 0.0 MB GPU VRAM impact.
- **Canonical Document**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.4; [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) §4.
- **Governing Decision**: ADR-028 (Long-Term Relational Consolidation), ARCH-026.
- **Research Specification**: [`docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESULTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESULTS.md); Phase 21 Acceptance Report (Commit `58a509c`).
- **Production Code**: [`src/core/emotion/consolidation.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/consolidation.py).
- **Verification Suite**: `tests/unit/test_consolidation.py` (13/13 PASS), `tests/evaluation/evaluation_phase21/` (15/15 PASS).

---

### 2.5 Canonical S1–S16 Cognitive Orchestrator Pipeline
- **Architectural Claim**: Conversational interaction executes as a strictly ordered, non-redundant 16-stage pipeline (S1–S16) owned authoritatively by `CognitiveOrchestrator`, with serialized turn execution (`asyncio.Lock` + `_turn_lock`) and complete two-phase relationship lifecycle separation (ADR-022: Stage 9 read snapshot $\mathbf{R}_{t-1}$, Stage 16.3 update $\mathbf{R}_t$).
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §2.1; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §2.
- **Governing Decision**: ADR-014, ADR-018, ADR-022, ADR-025, ARCH-012, ARCH-023.
- **Research Specification**: [`docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ACCEPTANCE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ACCEPTANCE_REPORT.md).
- **Production Code**: [`src/core/orchestrator/orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/orchestrator.py).
- **Verification Suite**: `tests/unit/test_orchestrator.py`.

---

### 2.6 Substrate Neutrality of Relational Cognition (Phase 22 Research Finding)
- **Architectural Claim**: Relational cognition does not depend on Small Language Models (SLMs), prompts, or natural-language token windows. Relational conditioning operates as a structured semantic interface (C1/C4) capable of driving non-language downstream consumers (D0 Symbolic Renderer, D2 Direct Action Policy) with 100% fidelity. 85% of CC context failure is syntactic token serialization overhead; pure dense HDC superposition fails for $N>5$ anchors.
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.1; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §2 (Callout), §8 (DRAFT ADR-030).
- **Governing Decision**: DRAFT ADR-030 (`[RESEARCH VALIDATED / NOT PROMOTED]`).
- **Research Specification**: [`docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md).
- **Evaluation Evidence**: `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/evaluation_artifacts/phase22_sc/final_report.md` (10/10 gates PASS), `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/evaluation_artifacts/phase22_cc/final_report.md`.
- **Production Code**: 100% Isolated; Production diff = 0 files changed.
- **Verification Suite**: `tests/evaluation/phase22_sc/` (all passing).

---

### 2.7 Conservative Semantic Fortification Across Session Boundaries (Phase 23-E)
- **Architectural Claim**: Language-independent semantic fortification layer protects formed state across session boundaries, enforcing zero novel entity ingress, bounded local consistency checks, non-monotonic JTMS premise invalidation, epistemic UNKNOWN/AMBIGUOUS preservation, and structural checksums ($\le 2.07\text{ ms}$ latency, $0.35\text{ MB}$ RAM, 0.0 MB GPU VRAM).
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8 (ADR ARCH-028).
- **Governing Decision**: ARCH-028.
- **Research Specification**: [`docs/research/P23_SOURCE_MAP.md#phase-23-e--conservative-semantic-fortification-across-session-boundaries`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md); `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23e/benchmark_results.json`.
- **Production Code**: [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py).
- **Verification Suite**: `tests/unit/test_semantic_fortification.py` (12/12 PASS), `tests/evaluation/phase23e/test_fortification_benchmark.py`.

---

### 2.8 Language Adapter Boundary & Substrate Contract (Phase 23-F)
- **Architectural Claim**: Decoupled Language Adapter subsystem isolates surface natural language from the Semantic Substrate, Cognitive Core, and Fortification. Enforces strict ingress/egress firewalls (only `{en, vi, ja}` admitted), substrate purity verification, and strict epistemic preservation (Japanese zero-anaphora UNKNOWN preservation, Vietnamese kinship separation).
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8 (ADR ARCH-029).
- **Governing Decision**: ARCH-029.
- **Research Specification**: [`docs/research/P23_SOURCE_MAP.md#phase-23-f--language-adapter-boundary--semantic-substrate-contract`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md); `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/benchmark_results.json`.
- **Production Code**: [`src/core/language/adapter/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/) (`contracts.py`, `registry.py`, `gate.py`, `drivers/`).
- **Verification Suite**: `tests/unit/test_language_adapter.py` (13/13 PASS), `tests/evaluation/phase23f/test_p23f_falsification.py` (4/4 PASS).

---

### 2.9 Semantic Substrate → Cognitive Core Contract (Phase 23-G)
- **Architectural Claim**: Language-independent boundary between Semantic Substrate and Cognitive Core. Strictly numeric concept, role, and entity IDs (zero strings in Core); Strong Kleene 3-valued logic ($A \land \text{UNKNOWN} \neq \text{TRUE}$); non-monotonic JTMS cascade invalidation; DisambiguationSubgoal for ambiguous branches; zero dynamic allocation in inner query loop via static `TermArena` ($0.6\text{ µs}$ query latency, 0.0 MB GPU VRAM).
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8 (ADR ARCH-030).
- **Governing Decision**: ARCH-030.
- **Research Specification**: [`docs/research/P23_SOURCE_MAP.md#phase-23-g--semantic-substrate--cognitive-core-contract`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md); `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23g/benchmark_results.json`.
- **Production Code**: [`src/core/cognition/contract/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/) (`arena.py`, `epistemic.py`, `terms.py`, `matcher.py`, `provenance.py`, `projection.py`, `synthesis.py`, `inference.py`).
- **Verification Suite**: `tests/unit/test_p23g_contract.py` (20/20 PASS), `tests/evaluation/phase23g/test_p23g_falsification.py` (12/12 PASS).

---

### 2.10 Bounded Goal-Directed Reasoning Kernel & JTMS (Phase 23-H)
- **Architectural Claim**: Operationalizes numeric substrate into a bounded, deterministic, goal-directed reasoning kernel. Backward goal chaining with hard search bounds (`MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`), deterministic cycle breaking, static Horn rules with $O(1)$ rule index, preallocated `BindingFrame` with bitmask, polar contradiction conflict detection, multi-justification JTMS retraction, and strict Strong Kleene K3 epistemic safety (`FIX-23H-01`: unproven goals remain UNKNOWN; denying antecedent never yields FALSE). Frozen bit-exact at commit `3eef803`.
- **Canonical Document**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md); [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2.
- **Governing Decision**: ARCH-031.
- **Research Specification**: [`docs/research/P23_SOURCE_MAP.md#phase-23-h--bounded-goal-directed-reasoning-kernel--jtms`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md); `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23h/benchmark_results.json`.
- **Production Code**: [`src/core/cognition/kernel/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/) (`binding.py`, `rules.py`, `jtms.py`, `conflict.py`, `engine.py`).
- **Implementation Commits**: Commit `6b22269` (Initial impl), Commit `3eef803` (Epistemic fix `FIX-23H-01` & Freeze).
- **Verification Suite**: `tests/unit/test_p23h_kernel.py` (22/22 PASS), `tests/evaluation/phase23h/test_p23h_falsification.py` (13/13 PASS).

---

### 2.11 Concept-to-Reasoning Substrate Investigation (Phase 23-I)
- **Architectural Status**: `RESEARCH COMPLETED + EVIDENCE CLOSURE COMPLETED + EVIDENCE STILL INSUFFICIENT + CONTRACT NOT FROZEN + IMPLEMENTATION NOT AUTHORIZED`.
- **Authoritative Evidence Document**: [`docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md).
- **Canonical Empirical Findings (E1–E4)**:
  - **E1 (Architectural Necessity):** Autonomous stateful P23-I subsystem is `NOT JUSTIFIED`. Full absorption into P23-C/G/H is `REJECTED`. Supported interpretation is a `Stateless Semantic Interface Adapter (SSIS-Adapter)`.
  - **E2 (Parameter Envelope):** $\text{MAX\_DISCOURSE\_REFERENTS} = 16$ is an arbitrary heuristic without empirical cliff; $\text{MAX\_RELATIONAL\_DEPTH} \le 3$ is a theoretical safety envelope unverified at boundary. Neither is frozen.
  - **E3 (Epistemic Grounding):** Confidence-to-assertion boundary is an `UNRESOLVED BLOCKER`. Continuous confidence must NOT silently become propositional certainty (`UNKNOWN -> TRUE`). Defeasible GVT $\to$ JTMS policy is not yet specified.
  - **E4 (Runtime):** Latency $\le 5.0\text{ ms}$ is `NOT VERIFIED` under active 200ms MT-LNN ODE CPU contention. GPU VRAM = 0.0 MB is repository-established.
- **Preserved Negative Results**: NEG-01 through NEG-05 permanently preserved (dynamic rule compilation, naive thresholding, unconstrained subgraph matching, anchor expiration to false, dense HDC superposition).
- **Next Governance Gate**: `GATE 23-I-EVAL` (Track A: Referent Envelope, Track B: Concurrency Runtime, Track C: Epistemic Ingress).
- **Superseded Preliminary Report**: [`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md) (Preliminary recommendation "Contract Transition Ready" / "FREEZE WITH PARAMETER" is **SUPERSEDED**).
- **Canonical Document**: [`docs/research/P23-I_RESEARCH_CONTEXT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_RESEARCH_CONTEXT.md); [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2.
- **Governing Decision**: `PENDING GATE 23-I-EVAL` (Contract is NOT frozen; implementation NOT authorized).
- **Pre-P23-I Governance Baseline**: Commit `bed9299` (`docs: establish repository-wide documentation and knowledge architecture`). *Note: Serves strictly as governance context, NOT empirical technical evidence.*
- **Ciah Review Projection**: [`docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md).
- **Production Code**: `IMPLEMENTATION NOT AUTHORIZED` (0 files changed in `src/core/**` and `electron/**`).

---

### 2.12 Phase 24 Adaptive Communication Control Surface
- **Architectural Claim**: Dynamic continuous pitch contouring ($S(t) \in [-4, +7]\text{ st}$, hard clip $\pm 12\text{ st}$), relational prosody conditioning (closeness, trust, familiarity approved; reciprocity strictly severed), boundary segmentation, cadence throttling, and real-time repair.
- **Canonical Document**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7.2; [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.6.5, §8 (ADR-032).
- **Governing Decision**: ADR-032 (ARCH-032).
- **Research Specification**: [`tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md), [`tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md).
- **Evaluation Evidence**: [`tests/evaluation/phase24/voice_benchmark/VOICE_BENCHMARK_PROSODY_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/VOICE_BENCHMARK_PROSODY_REPORT.md), [`docs/research/P24_GEMINI'S_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P24_GEMINI%27S_REPORT.md).
- **Production Code**: [`src/core/voice/boundary.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/boundary.py), [`src/core/voice/cadence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/cadence.py), [`src/core/voice/rvc_pipeline.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/rvc_pipeline.py), [`src/core/voice/voice_engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/voice_engine.py), [`src/core/voice/expression_policy.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/expression_policy.py), [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py), [`electron/renderer/chat/chat.js`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/renderer/chat/chat.js).
- **Implementation Commit**: Commit `5097f2f`.
- **Verification Suite**: `tests/unit/test_p24*`, `tests/property/test_p24*`, `tests/integration/test_p24*` (23/23 PASS).

---

### 2.13 Phase 25 Temporal Embodiment & Social Feedback (P25-Q1 Inquiry)
- **Architectural Status**: `P25-Q1 — RESEARCH COMPLETE / ARCHIVED AS EVIDENCE` (Architecture Gate & Implementation Gate remain LOCKED; Production Diff = 0).
- **Canonical Document**: [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md).
- **Evaluation Evidence**: [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_report.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_report.md); `docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_artifacts/phase25/raw_telemetry.json`.
- **Verification Suite**: `tests/evaluation/phase25/` (`test_p25_discrim.py`, `test_p25_evaluation_suite.py` — 22/22 PASS).

---

## 3. Sub-Phase Granular Source Maps
For detailed sub-phase source maps covering:
- Phase 25: See [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/).
- Phase 24: See [`tests/evaluation/phase24/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/).
- Phase 23 (P23-A through P23-I): See [`docs/research/P23_SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md).
- Phase 22 (20 Sub-Study Branches): See Section 2 of [`docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md).
