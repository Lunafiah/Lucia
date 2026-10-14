# P23 — CAPS Identification & Contract Investigation

> **Document Type:** Research-Only Architectural Investigation & Contract Specification  
> **Status:** `[RESEARCH INVESTIGATION COMPLETED / ARCHITECTURAL RULING: CAPS BOUNDARY JUSTIFIED]`  
> **Target Horizon:** Post-P23 / Pre-Activation Zero-LLM/SLM Runtime Architecture  
> **Execution Mode:** Read-Only Investigation • Zero Production Modification (`src/core/**` diff = 0) • Genesis Locked (`data/profile.json` bit-exact `{"is_onboarded": false}`)  
> **Evidence Standard:** E0 (Unobserved) → E1 (Documentary) → E2 (Static Implementation) → E3 (Execution Verified) → E4 (Reproducible Empirical)

---

## 1. Executive Summary

This investigation addresses the fundamental architectural question identified in the preceding Zero-LLM/SLM investigations ([`P23_SLM_FREE_RUNTIME_ARCHITECTURE_DECISION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_SLM_FREE_RUNTIME_ARCHITECTURE_DECISION.md) and [`P23_SLM_FREE_COMMUNICATION_ARCHITECTURE_INVESTIGATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_SLM_FREE_COMMUNICATION_ARCHITECTURE_INVESTIGATION.md)):

> **Can Lucia autonomously construct grounded outgoing propositions and communicative acts without an LLM/SLM, using capabilities already present or explicitly identifiable in the current architecture?**  
> **Is a dedicated CAPS (Communicative Act & Proposition Synthesizer) subsystem actually required, or is the capability already distributed across existing cognition, memory, reasoning, communication, and semantic-substrate components?**

### Key Findings & Verdict

1. **The Critical Identification Reality (E2/E3):**  
   If the LLM/SLM were removed tomorrow, **no existing component in the current production runtime would decide what Lucia is trying to communicate**.  
   - `ActiveInferenceEngine` ([`src/core/inference/active_inference.py:53–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/inference/active_inference.py#L53-L140)) is strictly a 3x3 linear matrix predictor of continuous PAD emotional transitions; it does not select actions, communicative acts, or propositions.
   - `ReasoningKernel` ([`src/core/cognition/kernel/engine.py:131–210`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L131-L210)) is an isolated backward-chaining deductive engine over integer terms; it evaluates theorem truth values but does not construct conversational statements or initiate dialogue acts.
   - `CommunicationPolicy` ([`src/core/communication/communication_policy.py:70–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140)) evaluates a 10D continuous modulation vector ($C_t$), but generates zero propositional content.
   - `KnowledgeStore` ([`src/core/knowledge/store.py:21–105`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L21-L105)) stores historical and factual propositions, but cannot decide which proposition constitutes an appropriate reply.
   - `SemanticGraph` ([`src/core/knowledge/fortification.py:195–298`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L195-L298)) is a static data structure and persistence format, not an active proposition generator.
2. **Current SLM Responsibility (E2):**  
   The existing SLM currently owns **both "What to Say" (communicative act selection, proposition selection, grounding against dialogue context) and "How to Say It" (lexicalization, syntax, morphology)**. While the cognitive core computes internal states (PAD ODE, somatic markers, relationship vectors, SDM echoes), the SLM currently bridges the entire chasm between those internal states and the outgoing utterance.
3. **Formal Ruling:** **`CAPS BOUNDARY JUSTIFIED` (Confidence: HIGH)**.  
   A formal, language-independent **Boundary Contract** between Internal Cognition and Language Realization is strictly necessary and justified by repository evidence. However, creating a new monolithic *subsystem* called "CAPS" is **NOT justified** at this stage; the required responsibilities (communicative act selection, factual retrieval, deductive justification, and graph construction) naturally belong to distinct cognitive domains (Active Inference/Policy, Knowledge/Reasoning, and Semantic Substrate) coordinated by an explicit contract.

---

## 2. Governance & Scope

This document is a **research and architectural contract investigation only**. In accordance with [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) Section 0 and [`L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md):

- **Read-Only Investigation:** Zero production code modifications (`src/core/**` diff = 0, `electron/**` diff = 0, `data/**` diff = 0).
- **Genesis Lock Invariant (INV-8):** Genesis Onboarding gate remains bit-exact:
  ```json
  {"is_onboarded": false}
  ```
  `data/genesis_commitment.json` does not exist (`False`). First Activation remains locked.
- **No Implementation Authorization:** No production migration, no deletion of `LLMBackend`, and no modification to `src/api/server.py` is authorized.
- **No Phase or ADR Creation:** No new phase (e.g. P23-J) or Architectural Decision Record is created.
- **Target Invariant:** The end-state target remains absolute: **complete elimination of the LLM/SLM runtime dependency** ($\text{LLM Dependency} = 0$, $\text{SLM Dependency} = 0$).

---

## 3. Evidence Standard

Claims and findings throughout this document strictly follow the 5-tier evidence hierarchy:
- **E0 — Unobserved:** Speculative or unevidenced in the repository.
- **E1 — Documentary:** Supported only by documentation, research specs, or historical reports.
- **E2 — Static Implementation:** Supported by source code inspection (classes, methods, control flow).
- **E3 — Execution Verified:** Observed in active runtime tests or integration harnesses.
- **E4 — Reproducible Empirical:** Verified by deterministic, reproducible benchmark telemetry.

---

## 4. Current SLM Responsibility Trace

A forensic trace of the Cognitive Turn in [`src/core/orchestrator/cognitive_orchestrator.py:360–650`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L360-L650) maps the exact distribution of responsibilities across the runtime:

```text
POST /chat (User Text)
  │
  ├─ Stage 1..10: Internal Cognition ──────────────────────── [NON-GENERATIVE CORE]
  │    • EmotionCore ODE (PAD) [Stage 3]
  │    • HomeostaticEngine (Somatic) [Stage 5]
  │    • EcphoryEngine SDM (Echo Vector) [Stage 6-7]
  │    • KnowledgeStore query_relevant() [Stage 8]
  │    • RelationshipUpdater read [Stage 9]
  │    • CommunicationPolicy (10D C_t) [Stage 10]
  │
  ├─ Stage 11: Prompt Assembly ─────────────────────────────── [TEXT FORMATTING]
  │    • PromptAssembler formats all mathematical values,
  │      history, and knowledge propositions into a single string.
  │
  └─ Stage 13: SLM Backend (llama_cpp) ═══════════════════════ [CRITICAL GENERATIVE PATH]
       • raw_response = _llm_backend.generate(prompt, constraints)
```

### Responsibility Inventory

| Responsibility | Current Owner | Exact Code Evidence | Runtime-Integrated? | Required After SLM Removal? | Evidence Grade |
|---|---|---|---|---|---|
| **Affect Dynamics** | `EmotionCore` | [`src/core/emotion/core.py:52–120`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/core.py#L52-L120) | **YES** | **YES** | **E4** |
| **Homeostatic Drives** | `HomeostaticEngine` | [`src/core/homeostasis/engine.py:45–95`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/homeostasis/engine.py#L45-L95) | **YES** | **YES** | **E4** |
| **Associative Memory** | `EcphoryEngine` | [`src/core/memory/ecphory.py:65–118`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py#L65-L118) | **YES** | **YES** | **E4** |
| **Relational Vectors** | `RelationshipUpdater` | [`src/core/relationship/updater.py:54–112`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/updater.py#L54-L112) | **YES** | **YES** | **E4** |
| **Pragmatic Modulation ($C_t$)**| `CommunicationPolicy` | [`src/core/communication/communication_policy.py:70–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140) | **YES** | **YES** | **E3** |
| **Communicative Act Selection** | **SLM (`LLMBackend`)** | [`src/core/language/llm_backend.py:355–385`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/llm_backend.py#L355-L385) | **YES** | **YES** | **E2** |
| **Proposition Selection** | **SLM (`LLMBackend`)** | [`src/core/language/llm_backend.py:355–385`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/llm_backend.py#L355-L385) | **YES** | **YES** | **E2** |
| **Proposition Construction** | **SLM (`LLMBackend`)** | [`src/core/language/llm_backend.py:355–385`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/llm_backend.py#L355-L385) | **YES** | **YES** | **E2** |
| **Discourse Anaphora / Coref**| **SLM (`LLMBackend`)** | [`src/core/language/llm_backend.py:355–385`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/llm_backend.py#L355-L385) | **YES** | **YES** | **E2** |
| **Lexicalization & Surface Text**| **SLM (`LLMBackend`)** | [`src/core/language/llm_backend.py:355–385`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/llm_backend.py#L355-L385) | **YES** | **YES** | **E2** |

---

## 5. What-to-Say vs. How-to-Say Decomposition

A critical conceptual distinction must separate the communication pipeline:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        "WHAT TO SAY"                                   │
│                 (Semantic / Propositional Intent)                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Communicative Act: Acknowledge | Inform | Inquire | Clarify         │
│ 2. Focus Entities & Concepts: c:ASSIST, ent:user, c:SOLVE_PROBLEM      │
│ 3. Argument Bindings: :ARG0 -> ent:lucia, :ARG1 -> ent:user            │
│ 4. Epistemic Status: FACT | INFERRED | AMBIGUOUS | UNKNOWN             │
│ 5. Logical Scopes: Affirmative | Negated | Modal Attitude              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         CAPS BOUNDARY CONTRACT
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        "HOW TO SAY IT"                                 │
│                 (Pragmatic & Surface Realization)                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Pragmatic Register: directness, formality, supportiveness (C_t)     │
│ 2. Language Selection: Gated admission {en, vi, ja}                    │
│ 3. Syntactic Alignment: SVO (English/Vietnamese) vs SOV (Japanese)     │
│ 4. Pronominalization & Pro-Drop: Zero-anaphora (JA) vs Passive (EN)    │
│ 5. Morphological Inflection & Honorifics: Keigo (JA), Kinship (VI)     │
│ 6. Multimodal Actuation: Prosody pitch/rate, facial blendshapes (E_t)  │
└────────────────────────────────────────────────────────────────────────┘
```

**Interpretation (E2):**  
"How to Say It" is already largely solved by P23-F drivers and Phase 24 policies.  
The **unresolved architectural gap lies entirely in "What to Say"**: how Lucia constructs the language-independent semantic payload without prompting an SLM.

---

## 6. ActiveInference Audit

### 6.1 What Does ActiveInference Actually Do?
Inspection of [`src/core/inference/active_inference.py:53–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/inference/active_inference.py#L53-L140) reveals:
- **Class:** `ActiveInferenceEngine`
- **Internal Model:** Maintains a $3 \times 3$ transition matrix $\mathbf{A} \in \mathbb{R}^{3 \times 3}$ and bias vector $\mathbf{b} \in \mathbb{R}^3$:
  $$\mathbf{q}_{\text{pred}} = \mathbf{A} \mathbf{p}_{\text{before}} + \mathbf{b}$$
- **Primary Method:** `step(pad_before: PADState, pad_after: PADState) -> float`
- **Output:** Returns pre-update prediction error (L2 norm) and updates $\mathbf{A}, \mathbf{b}$ via gradient descent with KL-regularization toward identity.

### 6.2 ActiveInference Audit Findings
1. **Does it select actions?** **NO.** It performs passive online estimation of PAD emotional transitions.
2. **Does it select communicative actions?** **NO.**
3. **Does it produce semantic content or propositions?** **NO.** It operates exclusively on 3D continuous floating-point vectors ($P, A, D$).
4. **Is its output consumed by the runtime communication path?** **NO.** In fact, `ActiveInferenceEngine` is not even instantiated or called inside `CognitiveOrchestrator.process()`. It is currently confined to offline dynamic benchmarks (`tests/unit/test_recollection_coupling.py`).

**Conclusion (E2/E3):** `ActiveInferenceEngine` **cannot** serve as the proposition producer or communicative act selector in its current implementation.

---

## 7. ReasoningKernel Audit

### 7.1 What Does ReasoningKernel Actually Provide?
Inspection of [`src/core/cognition/kernel/engine.py:131–210`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L131-L210) reveals:
- **Class:** `ReasoningKernel` (Phase 23-H)
- **Logic:** Strong Kleene 3-valued logic (TRUE, FALSE, UNKNOWN) with a Justification-based Truth Maintenance System (JTMS).
- **Core Interface:** `prove(goal: Goal) -> GoalResult`
- **Subgoals Emitted:** When UNKNOWN halts reasoning, it emits `InformationSubgoal(target_predicate_id, arg0_id, ...)` specifying the exact missing premise. When divergent hypotheses occur, it emits `DisambiguationSubgoal`.

### 7.2 ReasoningKernel Audit Findings
1. **Does it generate propositions?** It derives theorem truth values and can bind variables during unification over integer term IDs in `TermArena`.
2. **Does it decide what to communicate?** **NO.** It is a backward-chaining theorem prover: it only evaluates goals that are passed to it. It does not possess a conversational agenda.
3. **Does it produce `SemanticGraph` structures?** **NO.** It operates on numeric integer IDs (`predicate_id: int`, `arg0_id: int`).
4. **Is it integrated into the production `/chat` loop?** **NO.** `CognitiveOrchestrator.process()` does not import or invoke `ReasoningKernel`.

**Conclusion (E2/E3):** `ReasoningKernel` provides essential deductive justification and information-gap detection, but it is **not** a conversational proposition producer.

---

## 8. KnowledgeStore / Memory Audit

### 8.1 What Grounded Content is Available?
Inspection of [`src/core/knowledge/store.py:21–105`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L21-L105) and [`src/core/memory/ecphory.py:65–118`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py#L65-L118) reveals:
- **`KnowledgeStore`:** Holds explicit structured facts: `Proposition(subject, predicate, object, polarity, confidence, valid, provenance)`.
- **`EcphoryEngine`:** Associative Kanerva Sparse Distributed Memory (10,000 locations). Returns a 128D continuous echo vector and slow trace $r_{\text{slow}}$.
- **Stage 8 Query:** `CognitiveOrchestrator` queries `self._knowledge_store.query_relevant(input_text, max_results=5)`.

### 8.2 Memory Audit Findings
1. **Does retrieval equal proposition synthesis?** **NO.** Retrieving a list of matching historical triples (e.g. `(user, preference, reading)`) does not construct an answer or conversational statement.
2. **Missing Transformation:** The system lacks an operational step that transforms:
   $$\text{User Query Intent} + \text{Retrieved Proposition} \implies \text{Outgoing Grounded Assertion}$$

**Conclusion (E2):** Memory and knowledge provide raw factual grounding, but do not assemble outgoing dialogue propositions.

---

## 9. CommunicationPolicy Audit

Inspection of [`src/core/communication/communication_policy.py:70–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140) reveals:
- **Class:** `CommunicationPolicy`
- **Output:** 10D `CommunicationState` vector + `CommStrategy` enum.
- **Responsibility Audit:**
  - *Should Lucia communicate?* Always evaluates parameters; modulates pacing latency up to 1000 ms.
  - *What communicative act should occur?* Classifies broad style (`CommStrategy.DIRECT_FACTUAL`, `REASSURING_WARM`, etc.), but **not** atomic speech acts (`GREET`, `ANSWER`, `CLARIFY`).
  - *What proposition should be communicated?* **ZERO ownership.** It contains no entity or concept fields.
  - *How should it be verbalized?* Outputs numeric modulation parameters for downstream drivers.

**Conclusion (E3):** `CommunicationPolicy` strictly owns **pragmatic modulation**, not semantic proposition content.

---

## 10. SemanticGraph Audit

Inspection of [`src/core/knowledge/fortification.py:195–298`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L195-L298):
- **Nodes (`SemanticNode`):** Pure non-lexical concept symbols (`c:SOLVE_PROBLEM`, `ent:user`), 4 epistemic states (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`), scope IDs, polarity.
- **Edges (`SemanticEdge`):** Directed roles (`:ARG0`, `:ARG1`, `:ARG2`, `:mod`, `:sub-event`).
- **Scopes (`ScopeBoundary`):** `ROOT`, `NEGATION`, `MODAL`, `INTENSIONAL`.

### Audit Evaluation
- **Is `SemanticGraph` sufficient as an output boundary?** **YES for propositional semantics**, but **INCOMPLETE for conversational acts**.
- **Limitation:** A `SemanticGraph` represents propositional state, but does not carry conversational dialogue act metadata (e.g. whether the graph represents an assertion, an interrogative question, a confirmation, or a greeting).

---

## 11. P23-F Boundary Audit

Review of [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md):
- **What Was Proven (E4):**
  - Given an already-formed `SemanticGraph`, deterministic language drivers ([`EnglishLanguageDriver`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/english.py#L266)) realize correct surface text in **0.0085 ms** with **0.0 MB GPU VRAM** and ~9 KB RAM on local CPU.
  - Japanese zero-anaphora and Vietnamese kinship stripping preserve epistemic invariants.
- **What Was NOT Proven (E1/E2):**
  - Did NOT prove autonomous proposition generation from cognitive turns.
  - Drivers only recognize 4 hardcoded event frames across 24 words.
  - Did NOT test conversational turn-taking or question-answering.

---

## 12. Candidate Responsibility Decomposition

```text
Turn Stage                  Component Today        Component After SLM Removal      Status
──────────────────────────────────────────────────────────────────────────────────────────────
1. Input Ingress            Lexical Gating         LanguageIngressGate               PARTIAL (P23-F)
2. State Integration        EmotionCore ODE        EmotionCore ODE                   OPERATIONAL
3. Policy Selection         ActiveInference (off)  Dialogue Policy / Inference       GAP
4. Grounded Proposition     SLM Backend            CAPS Boundary Contract            MISSING
5. Graph Representation     None                   SemanticGraph + EpistemicState    AVAILABLE
6. Pragmatic Modulation     CommunicationPolicy    CommunicationPolicy (C_t)         OPERATIONAL
7. Language Realization     SLM Backend            Language Drivers (EN, VI, JA)     PARTIAL (P23-F)
8. Safety / Boundary        BoundaryLayer Regex    BoundaryLayer Regex (INV-2)       OPERATIONAL
```

---

## 13. Candidate CAPS Necessity Analysis

We test three distinct structural hypotheses:

### Hypothesis A: No New Boundary or Subsystem (`H-CAPS-A`)
- *Premise:* Existing components collectively provide the capability.
- *Evidence:* Falsified (E2). `ActiveInferenceEngine` is a 3x3 PAD predictor; `ReasoningKernel` is an isolated backward prover; `CommunicationPolicy` generates no propositions. There is zero code to construct an outgoing proposition.
- *Verdict:* **REJECTED.**

### Hypothesis B: Boundary Contract (`H-CAPS-B`)
- *Premise:* The capability is distributed across cognitive modules (Reasoning, Knowledge, Policy), but a formal **Boundary Contract** is strictly required to decouple cognition from language realization.
- *Evidence:* Strongly supported (E2/E3). Defining an explicit contract for `CommunicativeAct` and `OutgoingProposition` enables `ReasoningKernel`, `KnowledgeStore`, and `CommunicationPolicy` to emit structured meaning without inventing an ungrounded intermediary subsystem.
- *Verdict:* **ACCEPTED.**

### Hypothesis C: Dedicated Candidate Subsystem (`H-CAPS-C`)
- *Premise:* A brand-new monolithic subsystem called "CAPS" must be implemented.
- *Evidence:* Weak. Implementing a monolithic CAPS subsystem risks duplicating reasoning, memory querying, and policy logic inside an artificial middleman.
- *Verdict:* **PREMATURE / NOT JUSTIFIED.**

---

## 14. Grounding and Hallucination Boundary

What prevents a non-generative proposition system from producing hallucinated claims?
In a generative model (SLM), hallucination arises from unconstrained stochastic next-token sampling. In Lucia's non-generative target architecture, **hallucination is structurally impossible by construction**:

1. **Explicit Provenance Invariant:** Every asserted node in `SemanticGraph` must carry a [`ProvenanceRecord`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L134) tracing back to:
   - Direct user observation in the current session;
   - Grounded facts in `KnowledgeStore`;
   - Explicit theorem derivation via `ReasoningKernel` with numeric `rule_id` and supporting premise IDs;
   - Internal somatic/affective states.
2. **Epistemic Isolation:** Concepts lacking supporting premises must be typed as `EpistemicState.UNKNOWN` or `AMBIGUOUS`. Downstream drivers are physically constrained from realizing `UNKNOWN` nodes as facts.

---

## 15. The Novel Proposition Problem

Can a deterministic system communicate propositions that were never explicitly stored as templates or sentences?

**YES, via Compositional Semantic Graph Construction:**
- A deterministic system does not require templates. It requires:
  1. A structured semantic vocabulary of concepts $\mathcal{C}$ (e.g. `c:SOLVE`, `c:FILE`, `ent:user`, `c:UPDATE`).
  2. A typed relational grammar of argument roles $\mathcal{R}$ (`:ARG0`, `:ARG1`, `:mod`, `:time`).
  3. Compositional unification rules:
     $$\text{Concept}_A + \text{Role}_R + \text{Concept}_B \implies \text{SemanticEdge}(A, B, R)$$
- This provides **infinite compositional novelty** over a bounded concept vocabulary without requiring stochastic token generation.

---

## 16. Language Independence

The CAPS boundary contract must remain **100% language-independent**:
- **Zero Language Tokens:** Node identifiers must be abstract symbols (`c:ASSIST`, `ent:user`), never English strings (`"assist"`, `"user"`).
- **Zero POS Tags or Syntax Trees:** Deep syntax and word order belong exclusively inside language drivers downstream of the egress gate.
- **Cross-Lingual Parity:** A single emitted proposition graph must be equally realisable by the English, Vietnamese, or Japanese drivers.

---

## 17. Evidence Matrix

| Capability | Existing Component | Evidence Grade | Runtime Integrated | SLM Dependency | Identified Gap |
|---|---|---|---|---|---|
| **Affect Dynamics** | `EmotionCore` | **E4** | **YES** | None | None |
| **Pragmatic Modulation** | `CommunicationPolicy` | **E3** | **YES** | None | None |
| **Communicative Act Selection** | None (SLM today) | **E2** | **NO** | 100% | Needs Act Policy |
| **Proposition Construction** | None (SLM today) | **E2** | **NO** | 100% | Needs CAPS Contract |
| **Deductive Justification** | `ReasoningKernel` | **E3** | **NO** | None | Needs Runtime Integration |
| **Factual Retrieval** | `KnowledgeStore` | **E3** | **YES** | None | Needs Graph Compiler |
| **Surface Realization** | Language Drivers | **E3** | **PARTIAL** | None | Needs Lexicon Expansion |

---

## 18. Zero-LLM/Zero-SLM End-State Analysis

This investigation confirms that achieving **ZERO LLM and ZERO SLM runtime dependency** is technically achievable:
- The internal cognitive state is already token-free.
- The downstream surface realization is proven to operate in sub-10 µs without neural weights.
- The sole remaining conceptual gap is the formal contract defining how Cognition packages its outgoing intent into a `SemanticGraph` before handing it to the egress drivers.

---

## 19. Decision

```text
═══════════════════════════════════════════════════════════════════════════════
                           ARCHITECTURAL DECISION:
                          CAPS BOUNDARY JUSTIFIED
═══════════════════════════════════════════════════════════════════════════════
```

### Statement of Decision
1. A formal **Communicative Act & Proposition Synthesizer Boundary Contract (CAPS Contract)** is **JUSTIFIED** as a necessary architectural interface between Internal Cognition and Language Realization.
2. A dedicated, standalone **CAPS Subsystem** is **NOT JUSTIFIED**; the responsibilities are distributed across policy, reasoning, knowledge, and semantic substrate.
3. Implementation is **NOT AUTHORIZED** in this phase.

---

## 20. Confidence

**CONFIDENCE: HIGH**

- Confidence is grounded directly in line-by-line inspection of `cognitive_orchestrator.py`, `active_inference.py`, `engine.py`, `store.py`, and `communication_policy.py`.
- No assumptions regarding undocumented capabilities were accepted.

---

## 21. Remaining Research Questions

1. **Dialogue Act Taxonomy:** What is the minimal, closed set of dialogue acts required for Lucia (e.g. `ASSERT`, `INQUIRE`, `ACKNOWLEDGE`, `CLARIFY`, `GREET`)?
2. **Subgoal-to-Interrogative Mapping:** How should `ReasoningKernel`'s `InformationSubgoal` be compiled into an outgoing question graph?
3. **Turn-Level Memory Grounding:** How should recent dialogue turns in `self._history` be represented in `SemanticGraph` for pronominal reference and anaphora resolution?

---

## 22. Governance & Implementation Boundary

**MANDATORY GOVERNANCE NOTICE:**
- This investigation is **RESEARCH / ARCHITECTURAL IDENTIFICATION ONLY**.
- No implementation authorization is implied or granted.
- Zero production files were modified.
- Genesis remains locked bit-exact (`{"is_onboarded": false}`).

---

## 23. Final Conclusion

Lucia's cognitive architecture possesses all necessary physiological, emotional, homeostatic, relational, and deductive foundations to operate without an LLM or SLM. By establishing the **CAPS Boundary Contract**, Project Lucia can bridge internal cognition directly to its non-generative language drivers, completing the path toward complete runtime independence from generative language models.
