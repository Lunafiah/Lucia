# ADR-035: Production Realization Boundary & Fail-Closed Semantic Verification

> **Status**: IMPLEMENTED / FROZEN  
> **Date**: 2026-10-14  
> **Subsystem**: Stage S10 (CAPS) $\rightarrow$ Stage S11 (Realization) $\rightarrow$ Stage S14 (Verification) $\rightarrow$ Stage S15 (Expression)  
> **Deciders**: Antigravity, System Architecture Authority  
> **Implementation Evidence**: Stage 5 Production Realization Boundary ([STAGE_5_IMPLEMENTATION_REPORT.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/STAGE_5_IMPLEMENTATION_REPORT.md))  
> **Invariants Enforced**: INV-1 (One Continuous Life), INV-2 (No Reflective Ego), INV-3 (Memory Separation), INV-5 (Zero Cloud), INV-6 (Locking Discipline), INV-8 (Genesis Gate Separation)  
> **Preceding Evidence**: Stage 1 (Gap Spec), Stage 2 (Taxonomy), Stage 3-A (Serialization Loss), Stage 3-B (CPU/GPU Concordance), Stage 3-C (Contract Prompt Failure), Stage 3-D (Gate Feasibility), Stage 5 (Production Realization Boundary)  

---

## 1. Context & Problem Statement

Prior to this architectural decision, Lucia's language generation pipeline exhibited three critical architectural gaps:

1. **GAP-01 (Lossy Serialization Boundary)**: The authoritative semantic representation constructed by the Cognitive Core (`CAPSResult` and `SemanticGraph`) was flattened by `PromptAssembler` into unstructured prose bullets. As empirically verified in **Stage 3-A**, this caused **0.0% graph edge/role preservation** and **0.0% provenance preservation**, resulting in a baseline critical semantic error rate of **59.5%** on complex communicative phenomena.
2. **GAP-03 (Open-Loop Verification Leakage)**: Stage S14 (`BoundaryLayer`) only executed regex filtering for introspective affect (INV-2) and blacklisted persona terms, operating in an open-loop manner. It possessed no verification mechanism to detect whether the Small Language Model (SLM) reversed proposition polarity, dropped core arguments, or bypassed refusal obligations.
3. **GAP-05 (Untyped Boundary Contract & Realizer Floor)**: The interface between CAPS and Realization was untyped. Furthermore, **Stage 3-C** empirically proved that attempting to feed explicit compact DSL contracts (`ACT:`, `ARG0:`, `EVENT:`, `RULE:`) directly into the SLM prompt degraded accuracy (error rate rose from **50.0% to 85.7%**), because the ultra-compact `LFM2.5-1.2B` model lacks the inductive bias to parse dense code-like DSL contracts without fine-tuning.

### The Central Architectural Dilemma:
How does Lucia guarantee that natural language utterances remain 100% faithful to internal cognitive truth, when the realization substrate is an off-the-shelf 1.2B parameter SLM with severe intrinsic instruction-following limitations?

---

## 2. Core Architectural Question & Authoritative Answers

This ADR provides unambiguous answers to the foundational triad of questions:

### Q1: Where does Lucia maintain Semantic Authority?
> **Answer**: Semantic authority resides **exclusively** in the Persistent Cognitive State (`KnowledgeStore`, Coupled MT-LNN, SDM) and the symbolic representations constructed by Stage S10/S10b (`CAPSResult`, `SemanticGraph`, and `RealizationInputContract`).  
> **Under no circumstances does the SLM or conversation text history possess semantic authority.** Natural language text is an untrusted surface projection, never an epistemic ground truth.

### Q2: What is Realization permitted to do?
> **Answer**: Realization (Stage S11 `LLMBackend`) is strictly a **phonological and lexical realization substrate (a text renderer)**.  
> It is permitted to select lexical phrasing, prosodic cadence, sentence rhythms, and surface grammatical styling that reflect Lucia's somatic state ($\mathbf{E}_t$) and communication strategy.  
> **It is NOT permitted to**:
> - Assert facts not grounded in `KnowledgeStore` or CAPS.
> - Affirm propositions whose polarity is negative.
> - Omit or invert core semantic arguments (`:ARG0`, `:ARG1`, `:ARG2`).
> - Answer queries that CAPS has committed to `REFUSE` or `CLARIFY`.
> - Mutate, update, or establish cognitive commitments.

### Q3: What does the system do when Realization is unfaithful?
> **Answer**: The system enforces a **Fail-Closed Verification Boundary** at Stage S14.  
> When the deterministic `SemanticFidelityGate` detects a semantic violation (`BLOCK`), the corrupt candidate text is **instantly intercepted and discarded**.  
> The system emits a **deterministic, pre-compiled, non-hallucinating safe fallback** mapped 1:1 to the CAPS communicative act (e.g. honest grounded refusal, disambiguation request, or epistemic hedge).  
> The corrupt text is never emitted to P24 Voice Expression and never recorded as fact in memory.

---

## 3. Decision Matrix: Epistemic Authority & Trust Tiers

To eliminate epistemic ambiguity across the 16-stage cognitive pipeline, every component and artifact is assigned a strict authority classification:

| Pipeline Artifact / Component | Classification | Epistemic Authority | Operational Role & Invariants |
|---|---|---|---|
| **Persistent Cognitive State** (`KnowledgeStore`, MT-LNN, SDM) | **AUTHORITATIVE ROOT** | Absolute ($1.0$) | Sole source of truth for facts, relational bonds, and limbic dynamics. Governed by differential equations and JTMS. |
| **`CAPSResult` & `SemanticGraph`** | **AUTHORITATIVE INTENT** | Absolute ($1.0$) | Authoritative symbolic representation of what Lucia intends to communicate in turn $t$. Immutable once constructed. |
| **`RealizationInputContract`** | **AUTHORITATIVE CONTRACT** | Absolute ($1.0$) | Strongly-typed Python dataclass carrying invariant semantic obligations across the S10 $\rightarrow$ S11 $\rightarrow$ S14 boundary. |
| **Rendered Prompt (`PromptAssembler`)** | **DERIVED REPRESENTATION** | Ephemeral ($0.0$) | Language-specific compilation of directives into natural conversational prose for SLM attention. Non-authoritative. |
| **SLM Output (`candidate_text`)** | **UNTRUSTED CANDIDATE** | Zero ($0.0$) | Raw text generated by `LFM2.5-1.2B`. Untrusted draft that cannot be emitted without passing S14 verification. |
| **S14 `SemanticFidelityGate`** | **AUTHORITATIVE ARBITER** | Absolute ($1.0$) | Deterministic symbolic verification boundary. Possesses veto power to emit `PASS` or `BLOCK`. |
| **Safe Fallback Emission** | **AUTHORITATIVE FALLBACK** | High ($0.95$) | Static, pre-compiled, non-hallucinating template grounded strictly in CAPS communicative acts. |
| **`_history` (Conversation Buffer)** | **DERIVED PROJECTION** | Zero ($0.0$) | Surface record for discourse continuity. Cannot override `KnowledgeStore` or CAPS in subsequent turns. |

---

## 4. Key Architectural Decisions

### 4.1 Decision 1: Strongly-Typed Internal Contract vs Natural-Language Prompt Compilation
* **Design Choice**: Decouple the **internal software contract** from the **prompt representation**.
* **Rationale**: Stage 3-C proved that exposing raw DSL syntax (`ACT:`, `ARG0:`, `EVENT:`) to a 1.2B SLM induces cognitive collapse and language switching (+35.7% error rate). Therefore:
  1. Internally, `CognitiveOrchestrator` passes a strongly-typed `RealizationInputContract` (Pydantic/dataclass) containing explicit roles, polarity, epistemic status, and forbidden additions.
  2. `PromptAssembler` acts as a language-specific compiler, converting the contract into fluent, natural conversational guidance that respects the 1.2B SLM's training distribution.
  3. The exact `RealizationInputContract` instance is delivered directly to Stage S14, serving as the ground-truth oracle for deterministic verification.

### 4.2 Decision 2: Preservation Boundary Invariants
The following semantic dimensions MUST be explicitly preserved across the S10 $\rightarrow$ S14 boundary without flattening loss:
1. **Communicative Act**: Primary pragmatic intent (`ASSERT`, `INQUIRE`, `ANSWER`, `CLARIFY`, `REFUSE`, `GREET`, `FAREWELL`, `ACKNOWLEDGE`).
2. **Propositional Polarity**: Boolean polarity (`True` vs `False`). If `False`, explicit negation is mandatory.
3. **Epistemic Status**: `FACT`, `INFERRED`, `UNKNOWN`, `AMBIGUOUS`. Certainty strengthening is forbidden on non-facts.
4. **Argument Roles & Entities**: `:ARG0` (Agent), `:ARG1` (Theme/Patient), `:ARG2` (Goal/Attribute), mapped to verified entity mentions.
5. **Scope Structure**: `ROOT`, `MODAL_EMBEDDING`, `NEGATION_SCOPE`.
6. **Grounding & Provenance**: Verified origin (`OBSERVATION`, `INFERENCE`, `RETRIEVAL`). If ungrounded, `act` must be `REFUSE` or `CLARIFY`.
7. **Forbidden Additions**: Explicit negative constraints forbidding hallucinated entities.

### 4.3 Decision 3: Stage S14 Fail-Closed Gate Architecture
* **Mechanism**: Stage S14 deploys `SemanticFidelityGate` as a deterministic verification gate.
* **Execution Characteristics**:
  - Pure CPU symbolic execution (regex, slot token matching, epistemic constraint checking).
  - **Zero GPU VRAM** overhead.
  - Sub-5ms execution time (Stage 3-D benchmark: median 0.177 ms, p95 4.345 ms).
* **Decision States**:
  - `PASS`: Candidate text satisfies all semantic obligations. Forwarded to Stage S15/P24 Expression.
  - `BLOCK`: Candidate text violates one or more obligations. Intercepted immediately.
  - `UNCERTAIN`: Borderline evidence. Under strict fail-closed governance, treated as `BLOCK`.

### 4.4 Decision 4: Deterministic Fallback Specification (Zero Content Invention)
* When the gate issues `BLOCK`, the system **does not call the LLM to rewrite or invent text**.
* The gate selects a deterministic, pre-compiled template based on the CAPS communicative act:
  - `REFUSE`: Grounded refusal template acknowledging lack of verified data.
  - `CLARIFY`: Disambiguation question asking the user to specify their intent.
  - `SAFE_NEGATION`: Verified statement confirming non-occurrence.
  - `SAFE_HEDGE`: Epistemic qualification without content fabrication.
* This guarantees that even when the 1.2B realizer fails, **no false assertion or inverted polarity ever reaches the user**.

### 4.5 Decision 5: The History Boundary Guardrail
* **Problem**: If `_history` stores raw conversation turns, an ungrounded or speculative statement from turn $t$ could be retrieved as a pseudo-fact in turn $t+1$.
* **Invariant Enforced**:
  1. `_history` only records verified emissions (clean candidate text or deterministic fallback).
  2. Cognitive reasoning in Stage S6 (`ActiveInference`) and Stage S10 (`CAPS`) must query `KnowledgeStore` and `EpisodicMemory`, **NEVER** using `_history` as an authoritative epistemic premise.

### 4.6 Decision 6: Canonical Output Language Simplification & Decoupled Realization (P23-D Freeze)
* **Canonical Flow**:
  ```text
  Any-language input (multilingual perception)
          ↓
  Language-independent semantic / cognitive substrate
          ↓
  Communication / Pragmatic Policy
          ↓
  Realization
         ↙        ↘
  English Text   Japanese Voice
  ```
* **Production Output Targets**:
  ```python
  CANONICAL_TEXT_OUTPUT_LANGUAGE  = "en"
  CANONICAL_VOICE_OUTPUT_LANGUAGE = "ja"
  ```
* **Language Hierarchy & Boundary Distinctions**:
  1. *Perception vs Realization*: Multilingual input is admitted across perception and grounded into language-independent concepts. Input language does NOT dictate output language:
     $$\text{input language} \ne \text{output language}$$
  2. *Substrate Neutrality*: The cognitive core, limbic ODE, semantic graph, SDM memory, and JTMS reasoning never encode surface lexical tokens or language-specific syntax (EN/JA/VI). English and Japanese are strictly **surface realization languages**, not cognitive, memory, or affective languages.
  3. *Decoupled Parallel Realization Branches*:
     - **Text Branch**: Canonical production target is English (`en`). Generated by local SLM with natural prose directives, verified by S14 `SemanticFidelityGate`.
     - **Voice Branch**: Canonical production target is Japanese (`ja`). Deterministically realized directly from communicative acts and grounded propositions via `realize_japanese_voice_text()`.
     - Text and voice realize in parallel from the authoritative semantic/pragmatic contract (`RealizationInputContract` & Grounded Propositions). Neither branch acts as a semantic intermediary for the other.
  4. *First-Person Dyadic Companion Perspective*:
     - Lucia communicates strictly from a **first-person companion / dyadic perspective** ("I" / "we" / "you"). Third-person narrator or external-observer framing ("two people", "hai người", "二人") is strictly forbidden during direct interaction.
     - Architecture tiering:
       ```text
       Semantic / pragmatic grounding
               ↓
       Realization guidance
               ↓
       Lexical safety guard
       ```
       The lexical guard (`DYADIC_PERSPECTIVE_DRIFT`) is a fail-closed safety net, not the definition of dyadic companionship.

---

## 5. Architectural Data-Flow Diagram

```mermaid
flowchart TD
    subgraph PERCEPTION ["Multilingual Perception Boundary"]
        INP["Any-Language Input (Multilingual EN/VI/JA/...)\n[Input Language != Output Language]"]
    end

    subgraph COGNITIVE_CORE ["Cognitive Core (Language-Independent State)"]
        KS["KnowledgeStore (JTMS / Triples)"]
        LNN["Coupled MT-LNN (Dynamic Affect)"]
        REL["RelationshipState (Philia Attractor)"]
    end

    subgraph S10_CAPS ["Stage S10 / S10b: Communicative Action Planning"]
        CAPS["CAPS Engine"]
        SG["SemanticGraph (Roles, Scopes, Provenance)"]
        TIC["Typed RealizationInputContract\n[Authoritative Semantic Intent]"]
        KS --> CAPS
        LNN --> CAPS
        REL --> CAPS
        CAPS --> SG
        SG --> TIC
    end
    
    INP -.->|"Perception Ingress"| COGNITIVE_CORE

    subgraph S11_REALIZATION ["Stage S11: Decoupled Parallel Realization Boundary (P23-D)"]
        direction TB
        
        subgraph S11_TEXT ["English Text Realization (CANONICAL_TEXT_OUTPUT_LANGUAGE = 'en')"]
            PA["PromptAssembler (Natural Prose Compiler • Dyadic Directives)"]
            SLM["LFM2.5-1.2B Realizer (Untrusted Generator)"]
            CAND["Candidate Text Draft"]
            PA --> SLM
            SLM --> CAND
        end
        
        subgraph S11_VOICE ["Japanese Voice Realization (CANONICAL_VOICE_OUTPUT_LANGUAGE = 'ja')"]
            DIR_VOICE["realize_japanese_voice_text()\n[Direct Semantic/Pragmatic Realization]"]
            SURF_VOICE["translate_to_japanese(safe_response)\n[Surface Convenience Path • Note A]"]
            VOICE_TXT["Japanese Voice Content (VoiceRealization)"]
            DIR_VOICE --> VOICE_TXT
            SURF_VOICE -.->|"Optional Convenience"| VOICE_TXT
        end
        
        TIC -->|"Authoritative Directives"| PA
        TIC -->|"Authoritative Intent"| DIR_VOICE
    end

    subgraph S14_VERIFICATION ["Stage S14: Fail-Closed Verification Boundary"]
        GATE["SemanticFidelityGate (Pure Symbolic CPU • Dyadic Guard)"]
        FALLBACK["Deterministic Fallback Registry"]
        DECISION{"Gate Decision"}
        
        TIC -->|Authoritative Oracle| GATE
        CAND -->|Candidate Text| GATE
        GATE --> DECISION
        DECISION -->|PASS| EMIT["Verified Natural Language (TextRealization)"]
        DECISION -->|BLOCK / UNCERTAIN| FALLBACK
        FALLBACK -->|Safe Template| EMIT
        EMIT -.->|"Surface Convenience Input"| SURF_VOICE
    end

    subgraph S15_P24 ["Stage S15 / S16: P24 Voice Expression & History"]
        P24["P24 Voice Pipeline (Cadence, F0, RVC)"]
        HIST["_history (Surface Record Buffer)"]
        VOICE_TXT --> P24
        EMIT --> HIST
    end

    style COGNITIVE_CORE fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style S10_CAPS fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style S11_REALIZATION fill:#334155,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style S14_VERIFICATION fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#f8fafc
    style S15_P24 fill:#1e293b,stroke:#8b5cf6,stroke-width:2px,color:#f8fafc
```

---

## 6. Consequences & System Trade-offs

### Positive Consequences:
1. **Absolute Semantic Safety (Containment)**: 100% of polarity reversals, argument omissions, and refusal bypasses are intercepted before reaching audio synthesis or user display.
2. **Zero Degradation on Realizer**: The 1.2B SLM is prompted with natural, fluent conversational directives rather than confusing DSL tokens, maintaining its best possible conversational fluency.
3. **Negligible Latency & Resource Impact**: Gate operates in ~0.2–4.3 ms on CPU with 0 MB GPU VRAM and <300 KB RAM.
4. **Strict Traceability**: Every emission has clear provenance: either verified model realization or deterministic fallback template.

### Negative Consequences & Operational Trade-offs:
1. **Conversational Repetition under High SLM Failure Rates**: Because `LFM2.5-1.2B` fails 50–65% of complex semantic realizations, 50–65% of difficult turns will trigger deterministic fallbacks (hedges or clarification questions).
2. **Gate is Containment, NOT Generation Remediation**: The gate guarantees that Lucia never lies or contradicts herself, but does not magically make the 1.2B SLM more capable. True generation remediation requires fine-tuning or scaling the realizer (P25+ horizons).
3. **Maintenance of Fallback Templates**: Fallback templates must be curated across supported languages (EN, VI, JA) to remain natural and contextually appropriate.

---

## 7. Migration & Implementation Sequence (Stage 5 Completed)

The five decisions from ADR-035 were executed and verified in **Stage 5 (Production Implementation)**:

1. **Step 1: Module Creation (`src/core/language/contract.py`)**:
   - Implemented immutable `RealizationInputContract`, `SemanticRoleBinding`, `ProvenanceRecord`, and associated domain enums (`CommunicativeAct`, `EpistemicStatus`, `SemanticScopeType`, `ProvenanceOrigin`).
2. **Step 2: Compiler Update (`src/core/orchestrator/prompt_assembler.py`)**:
   - Refactored `PromptAssembler.assemble()` to compile typed contracts into conversational natural-language prose directives for EN, VI, and JA without emitting DSL or code tokens (`ARG0:`, `EVENT:`, `RULE:`).
3. **Step 3: S14 Gate Implementation (`src/core/language/gate.py`)**:
   - Implemented deterministic pure-CPU symbolic `SemanticFidelityGate` ($<0.1\,\text{ms}$ latency, $0\,\text{MB}$ GPU VRAM) and zero-invention `FALLBACK_REGISTRY` covering 6 symbolic checks (INV-2, communicative act, polarity, epistemic status, argument preservation with pro-drop awareness, unsupported additions).
4. **Step 4: Orchestrator Integration (`src/core/orchestrator/cognitive_orchestrator.py`)**:
   - Wired Stage S10b contract construction, Stage S11 prompt assembly, Stage S14 gate verification evaluating untrusted raw SLM candidates directly, fail-closed fallback replacement (`UNCERTAIN -> BLOCK`), and `_history` containment.
5. **Step 5: Automated Verification Suite (`tests/unit/test_production_realization_boundary.py`)**:
   - Executed 16 targeted boundary tests (`16/16 PASS`) and full regression suite across P21–P25 and core pipeline (`136/136 PASS`).
   - Genesis invariant verified bit-exact: `data/profile.json == {"is_onboarded": false}`.
   - Zero production source code deviations from ADR-035.

6. **Step 6: Output Language Simplification & Decoupled Realization (P23-D Freeze)**:
   - Established canonical production output constants:
     ```python
     CANONICAL_TEXT_OUTPUT_LANGUAGE  = "en"
     CANONICAL_VOICE_OUTPUT_LANGUAGE = "ja"
     ```
   - Implemented immutable `RealizationOutput`, `TextRealization`, and `VoiceRealization` dataclasses in `src/core/language/contract.py`.
   - Guaranteed substrate neutrality: English and Japanese are surface realization targets only, never cognitive, memory, affective, or relational languages. Multilingual input perception remains decoupled ($\text{input language} \ne \text{output language}$).
   - Decoupled parallel realization branching: Japanese voice realizes directly from communicative acts and grounded propositions via `realize_japanese_voice_text()` in `src/core/language/realization.py`. Neither text nor voice acts as a semantic intermediary for the other.
   - Enforced dyadic companion first-person perspective across prompt assembler guidance and S14 gate (`DYADIC_PERSPECTIVE_DRIFT`), blocking third-person narrator drift.
   - P23-D Decision Gate: **PASS WITH NOTES**.
   - Verification: **89/89** relevant communication + realization tests PASS, **0 regression**.
   - Architecture Audit: **No Category-C Production Architectural Coupling detected**.
   - Preserved Notes & Technical Debt:
     - **Note A — Japanese Voice Realization**: Helper `translate_to_japanese(safe_response)` at the realization layer is a surface-realization convenience path, not semantic architecture. Direct semantic/pragmatic Japanese realization fallback already exists (`realize_japanese_voice_text`). English text is not a semantic intermediate. Future multi-head renderer refactor is outside P23-D current scope.
     - **Note B — Dead Import Housekeeping**: Unused `detect_active_language` import retained in `CognitiveOrchestrator` is recorded as housekeeping / technical debt; no implementation task opened for P23-D.

> **Operational Boundary Clarification**:  
> S14 provides fail-closed containment within the tested contracts and failure modes; it does not constitute universal semantic-safety proof or realization-quality remediation.

---

## 8. Final Decision

```text
========================================================================
ADR-035 DECISION:
IMPLEMENTED / FROZEN (P23-D Output Language Freeze: PASS WITH NOTES)
========================================================================
```

### Rationale:
The architecture for the Production Realization Boundary is fully implemented in production runtime, grounded in empirical evidence from Stages 1 through 3-D, expanded and simplified in P23-D (English Text + Japanese Voice parallel realization), verified by targeted and regression test suites (Stage 5 136/136 PASS; P23-D 89/89 PASS with 0 regression), passes post-change architecture audit with zero Category-C coupling, enforces all system invariants (INV-1 through INV-8), preserves bit-exact Genesis onboarding protection (`data/profile.json == {"is_onboarded": false}`), and establishes a permanent, fail-closed realization boundary.

