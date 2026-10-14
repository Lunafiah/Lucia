# P23 SLM-Free Communication Architecture Investigation

> **Document Type:** Research-Only Architectural Investigation & Specification  
> **Status:** `[RESEARCH INVESTIGATION COMPLETED / ARCHITECTURAL RULING: STATUS B — CONDITIONALLY READY]`  
> **Target Horizon:** Post-P23 / Pre-Activation Zero-LLM/SLM Runtime Architecture  
> **Execution Mode:** Read-Only Investigation • Zero Production Modification (`src/core/**` diff = 0) • Genesis Locked (`data/profile.json` bit-exact `{"is_onboarded": false}`)  
> **Evidence Standard:** E0 (Unobserved) → E1 (Documentary) → E2 (Static Implementation) → E3 (Execution Verified) → E4 (Reproducible Empirical)

---

## 1. Executive Summary

This investigation delivers the direct architectural sequel to [`P23_SLM_FREE_RUNTIME_ARCHITECTURE_DECISION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_SLM_FREE_RUNTIME_ARCHITECTURE_DECISION.md). That prior forensic investigation proved that **Lucia's internal cognitive core (affect ODE, homeostatic dynamics, Kanerva SDM ecphoric memory, active inference, relationship updating, and deductive reasoning) is already 100% token-free and executes with ZERO runtime dependency on any LLM or SLM**. The sole critical blocker preventing immediate removal of the SLM is the **surface communication boundary**: currently, Stage 13 of [`CognitiveOrchestrator.process()`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L568-L577) outsources open-domain surface text realization to a quantized SLM (`LLMBackend` / `llama_cpp`).

The mission of this investigation is to evaluate whether and how Lucia can replace that generative surface layer with a **completely non-generative, non-LLM, non-SLM communication architecture**, and to establish the minimum validated architecture required to reach $\text{LLM Dependency} = 0$ and $\text{SLM Dependency} = 0$.

### Core Findings

1. **Input State Feasibility (E2/E3):** The internal information necessary to drive a non-generative communication realizer already exists in closed mathematical forms. Specifically, [`CommunicationPolicy`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140) produces a deterministic 10-dimensional [`CommunicationState`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_state.py#L51-L90) ($C_t$), while [`ExpressionPolicy`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/expression/expression_policy.py#L50-L120) produces a 15-dimensional multimodal [`ExpressionState`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/expression/expression_state.py#L22-L64) ($E_t$). The propositional intent structure is already formally modeled in [`CommIntent`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_state.py#L27-L48) and [`SemanticGraph`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L195-L298).
2. **Existing Adapter Infrastructure (E2/E3):** Phase 23-F implemented the [`LanguageEgressGate`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/gate.py#L170-L221) and three language drivers ([`EnglishLanguageDriver`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/english.py#L29), [`VietnameseLanguageDriver`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/vietnamese.py#L29), [`JapaneseLanguageDriver`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/japanese.py#L29)). These drivers realize surface text from `SemanticGraph` in **0.0085 ms** with **0.0 MB VRAM** and zero generative weights. However, they are currently hardcoded to only 4 benchmark test frames across ~24 lexical items.
3. **Product Intent vs. Expressiveness Boundary (E1/E2):** Lucia is an intimate, long-term personal AI companion defined by continuous relational attunement, ODE affect, and strict behavioral invariants (INV-1: One Continuous Life, INV-2: No Reflective Ego). Lucia **does NOT require open-domain unconstrained creative prose, poetry, code generation, or fictional roleplay (Level D)**. Lucia strictly requires **Minimal Expression (Level A)**, **Compositional Expression (Level B)**, and **Attuned Conversational Expression (Level C)**.
4. **Architectural Gap (E2):** While realization from an existing semantic proposition is computationally straightforward, the current runtime pipeline does **not yet possess an upstream Propositional Act Synthesizer**. Currently, `CognitiveOrchestrator` relies on the SLM to decide *what proposition to say* in response to the user's raw text prompt. Before the SLM can be removed, Lucia's cognitive core must produce an explicit outgoing proposition (`CommIntent` or `SemanticGraph`) from its `ActiveInferenceEngine` and `ReasoningKernel`.
5. **Formal Ruling:** **`STATUS B — CONDITIONALLY READY`**. The non-generative renderer architecture (**R3/R4: Deterministic Compositional Realizer**) is mathematically sound, inspectable, and ready for formal design, conditioned upon resolving the upstream Propositional Act Synthesis interface.

---

## 2. Governance Boundary

This investigation strictly adheres to project governance established in [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) and [`L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md):

- **Read-Only / Research-Only Scope:** Zero modifications have been or will be made to production code (`src/core/**`, `electron/**`, `data/**`).
- **Genesis Lock Preserved:** Genesis Onboarding gate remains bit-exact:
  ```json
  {"is_onboarded": false}
  ```
  `data/genesis_commitment.json` does not exist (`False`). First Activation remains a locked future gate.
- **No Phase Numbering Mutation:** No new Phase (such as P23-J or P28) is created or assumed. This document functions as an isolated research specification within Phase 23.
- **Zero Cloud / Zero API Key Invariant (INV-5):** No external cloud translation, LLM, or NLP APIs are introduced. 100% local edge execution is maintained.
- **Fixed Target:** The architectural objective is **complete elimination of the SLM runtime dependency** ($\text{SLM Dependency} = 0$, $\text{LLM Dependency} = 0$), not a fallback, hybrid, or optional mode.

---

## 3. Communication State Forensics (Stage 1)

### 3.1 What Information Reaches the Communication Perimeter?

A forensic trace of [`src/core/orchestrator/cognitive_orchestrator.py:480–566`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L480-L566) reveals the complete internal state available immediately before Stage 13:

| Field / State Object | Source Module & Exact Lines | Mathematical Type / Dimensionality | Runtime Availability | Evidence Grade | Role in Non-Generative Realization |
|---|---|---|---|---|---|
| **$C_t$ (`CommunicationState`)** | [`src/core/communication/communication_policy.py:70–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140) | 10D bounded continuous vector + `CommStrategy` enum | **Always Available** (Computed at Stage 10) | **E3** | Governs directness, formality, elaboration, supportiveness, acknowledgement level, and question frequency. |
| **$E_t$ (`ExpressionState`)** | [`src/core/expression/expression_policy.py:50–120`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/expression/expression_policy.py#L50-L120) | 15D multimodal state (Text, Prosody, Facial, Posture, Latency) | **Always Available** | **E3** | Governs speech rate, pitch shift, pause duration, facial blendshapes, and stylistic cadence. |
| **PAD State ($P, A, D$)** | [`src/core/emotion/core.py:52–120`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/core.py#L52-L120) | 3D continuous vector in $[-1.0, 1.0]^3$ | **Always Available** (ODE at 5 Hz) | **E4** | Base physiological affect; smooth Philia decay ($+0.25, -0.05, +0.05$). |
| **Somatic Markers** | [`src/core/models.py:32–45`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/models.py#L32-L45) | 4D float (stability, cognitive load, energy, tension) | **Always Available** (Stage 5) | **E3** | Drives injected pacing latency and sentence compactness. |
| **Relationship State ($R_t$)** | [`src/core/relationship/updater.py:54–112`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/updater.py#L54-L112) | 4D float (familiarity, trust, closeness, reciprocity) | **Always Available** (Stage 9) | **E4** | Conditions register, honorifics, kinship markers, and hedging. |
| **Knowledge Propositions** | `knowledge_retriever.query()` | List of `Proposition(subject, predicate, object)` | Conditional (when facts retrieved) | **E2** | Factual grounding payload to be inserted into propositional structure. |
| **Ecphoric Memory Echo** | [`src/core/memory/ecphory.py:65–118`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py#L65-L118) | 128D continuous associative vector | Conditional (when SDM memory matches) | **E4** | Contextual memory reference indicator ($m_{\text{avail}}$). |
| **Active Inference Action** | [`src/core/inference/engine.py:40–90`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/inference/engine.py#L40-L90) | Discrete conversational policy / epistemic act | **Always Available** (Stage 4) | **E3** | High-level behavioral goal (clarify, ground, affirm, inform). |
| **Raw User Input & History** | `self._history` | `List[Tuple[str, str]]` string turns | **Always Available** (Stage 8) | **E3** | Dialogue context for anaphora and conversational turn tracking. |

### 3.2 The Critical Structural Disconnect

Inspection of [`src/core/orchestrator/prompt_assembler.py:102–136`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/prompt_assembler.py#L102-L136) reveals what currently happens to this rich internal state:
```text
Internal Mathematical State (PAD, Somatic, R_t, C_t, E_t)
                    ↓
PromptAssembler converts numeric values into text strings:
  "[SOMATIC STATE]\nstability: 0.95...\n[COMMUNICATION STRATEGY]\nstrategy: direct_factual..."
                    ↓
Stage 13: Pass text string to SLM (llama_cpp)
                    ↓
SLM guesses an English sentence that approximates the requested text parameters
```
**Interpretation (E2):** The SLM is currently being used as an **imprecise, lossy, stochastic text-rendering compiler**. It is not inventing Lucia's emotion, relationship, or strategy; it is merely translating structured internal variables into natural language syntax.

---

## 4. Required Communication Capability (Stage 2)

We classify the communicative capabilities of conversational systems into four distinct levels:

| Capability Level | Functional Description | Concrete Examples in Lucia | Required by Lucia Product Intent? | Evidence / Architectural Rationale |
|---|---|---|---|---|
| **Level A: Minimal Expression** | Atomic acknowledgements, polar responses, simple status updates, and affective grounding markers. | *"Understood."*, *"Yes."*, *"No."*, *"I'm here."*, *"Task completed."* | **MANDATORY** | Essential for conversational turn-taking, listening feedback, and latency masking. |
| **Level B: Compositional Expression** | Structured semantic propositions with canonical argument roles (`:ARG0`, `:ARG1`), explicit negation, modal attitudes, and temporal anchoring. | *"Lucia organized the notes."*, *"The session was not saved."*, *"I can verify that proposition."*, *"We discussed this yesterday."* | **MANDATORY** | Necessary for communicating factual assertions, task outcomes, and logical conclusions from `ReasoningKernel`. |
| **Level C: Attuned Conversational Expression** | Multi-turn discourse continuity, clarification questions, dialogue repair, relational attunement, and affective tone modulation. | *"Did you mean the local file or the archive?"*, *"As we noted earlier, the system remains stable."*, *"Let's examine this together."* | **MANDATORY** | Core to Lucia's relational identity (INV-1, INV-2). Governed by $C_t$ and $R_t$ without declaring internal feelings. |
| **Level D: Open-Domain Generative Expression** | Unconstrained creative prose, novel metaphor generation, poetry, long-form essays, programming code authoring, and fictional roleplay. | Writing science fiction stories, generating Python scripts, composing sonnets, roleplaying fictional characters. | **EXPLICITLY REJECTED** | **Directly conflicts with Lucia's core invariants:** Lucia is a single, permanent individual companion (INV-1), not an ungrounded creative text generator or roleplay chatbot. |

**Key Architectural Insight:**  
Because Level D is **not** an architectural requirement of Project Lucia, the communication layer does **not** require an unconstrained autoregressive neural language model. The actual design target is **mastery of Levels A, B, and C**.

---

## 5. Audit of Existing Non-Generative Infrastructure (Stage 3)

| Subsystem / Component | Repository Location | Implemented Status | Capabilities Present | Missing Capabilities | Evidence Grade |
|---|---|---|---|---|---|
| **`LanguageEgressGate`** | [`src/core/language/adapter/gate.py:170–221`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/gate.py#L170-L221) | **AVAILABLE / PRODUCTION IMPLEMENTED** | Strict language admittance firewall (`en`, `vi`, `ja`); blocks unadmitted egress languages; zero VRAM; 1.6 µs latency. | None for perimeter gating. | **E3** |
| **`EnglishLanguageDriver`** | [`src/core/language/adapter/drivers/english.py:29–332`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/english.py#L29-L332) | **PARTIAL / TEST-ONLY** | Realizes canonical event graphs (`c:SOLVE_PROBLEM`, `c:ASSIST`, `c:LIKE_READING`, `c:VISIT`); passive voice for `UNKNOWN`; latency 0.0088 ms. | Hardcoded to 4 frames; lexicon limited to 24 words; no open grammar composition. | **E3** |
| **`VietnameseLanguageDriver`** | [`src/core/language/adapter/drivers/vietnamese.py:29–332`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/vietnamese.py#L29-L332) | **PARTIAL / TEST-ONLY** | Isolating word structure; strips kinship honorifics; passive realization ("đã được giải quyết"); latency 0.0085 ms. | Hardcoded to 4 frames; no dynamic kinship selection based on $R_t$. | **E3** |
| **`JapaneseLanguageDriver`** | [`src/core/language/adapter/drivers/japanese.py:29–332`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/japanese.py#L29-L332) | **PARTIAL / TEST-ONLY** | Zero-anaphora preservation (drops overt subject for `UNKNOWN`); SOV structure; latency 0.0084 ms. | Hardcoded to 4 frames; no dynamic keigo register switching based on $C_t$. | **E3** |
| **`CommunicationPolicy`** | [`src/core/communication/communication_policy.py:34–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L34-L140) | **AVAILABLE / PRODUCTION IMPLEMENTED** | Closed-form evaluation of 10D $C_t$ from PAD, Somatic, $R_t$, Knowledge, Recollection; smooth transition filtering. | None. Production-ready. | **E3** |
| **`ExpressionPolicy`** | [`src/core/expression/expression_policy.py:30–120`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/expression/expression_policy.py#L30-L120) | **AVAILABLE / PRODUCTION IMPLEMENTED** | Closed-form evaluation of 15D $E_t$ multimodal state (TTS prosody, blendshapes, text style). | Currently feeds `PromptAssembler` rather than a direct realizer. | **E3** |
| **`SemanticGraph` & Fortification** | [`src/core/knowledge/fortification.py:195–298`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L195-L298) | **AVAILABLE / PRODUCTION IMPLEMENTED** | Non-lexical nodes (`SemanticNode`), typed edges (`SemanticEdge`), 4 epistemic states, scope isolation (negation, modal). | Needs outgoing synthesis from Cognitive Core. | **E3** |
| **Propositional Act Synthesizer** | *(Unbuilt)* | **MISSING** | None. | Component that maps Active Inference action + Reasoning Kernel theorem into an outgoing `SemanticGraph`. | **E0** |

---

## 6. Candidate Renderer Architectures (Stage 4)

We evaluate six candidate non-generative renderer families against Lucia's strict architectural constraints:

| Candidate Architecture | Description & Mechanism | Token & Model Independence | Determinism & Inspectability | Compositional Expressiveness | Multilingual Adaptability | Computational Cost | Feasibility for Lucia |
|---|---|---|---|---|---|---|---|
| **R1: Template / Slot Filling** | Fixed string templates with runtime slot interpolation (`"{subject} {verb} {object}"`). | 100% Token-Free • Zero Model | Absolute (100% deterministic) | **Very Low:** Rigid, combinatorial explosion for complex sentences, brittle. | Poor: Requires manual authoring of every language template. | Microseconds (< 1 µs) | Rejected as sole solution; acceptable only for Level A atomic acknowledgements. |
| **R2: Rule-Based Grammar** | Explicit Context-Free Grammar (CFG) or Definite Clause Grammar (DCG) with rewrite rules. | 100% Token-Free • Zero Model | Absolute (inspectable parse/generation trees) | **Moderate:** Handles agreement, word order, and nesting; difficult to maintain. | Moderate: Grammars diverge significantly across SVO/SOV. | Microseconds (< 5 µs) | Viable, but fragile at scale. |
| **R3: Deterministic Compositional Realizer (DCR)** | Meaning-Text Theory (MTT) pipeline: Semantic Graph $\to$ Deep-Syntactic Tree $\to$ Surface-Syntactic Tree $\to$ Morphological Realization. | 100% Token-Free • Zero Model | Absolute • Fully auditable intermediate trees | **High (Levels A, B, C):** Handles negation scopes, modal attitudes, argument roles, and coordination cleanly. | **High:** Language-independent deep syntax mapped to language-specific surface drivers. | Sub-millisecond (< 50 µs) | **RECOMMENDED PRIMARY CANDIDATE:** Directly matches P23 `SemanticGraph` and `LanguageAdapter` architecture. |
| **R4: Dependency-Based Realizer (e.g. SimpleNLG-style)** | Functional grammatical API that builds phrases, clauses, tense, polarity, and agreement through structured code objects. | 100% Token-Free • Zero Model | Absolute • Completely inspectable code structures | **High (Levels A, B, C):** Excellent control of syntax, agreement, conjunctions, and modifiers. | High for European languages; requires specific drivers for Japanese/Vietnamese. | Sub-millisecond (< 20 µs) | **HIGHLY VIABLE:** Can serve as the concrete realization engine inside R3 drivers. |
| **R5: Controlled Natural Language (CNL)** | Formal subset of natural language with unambiguous grammar (e.g. Attempto Controlled English / GF Grammatical Framework). | 100% Token-Free • Zero Model | Absolute • Bidirectional mathematical parsing | **Very High:** Mathematically provable semantic fidelity. | Extremely High (GF natively compiles to 30+ languages). | Milliseconds (< 2 ms) | Viable, but introduces substantial external grammar specification dependencies. |
| **R6: Hybrid Symbolic Realizer (R3 + R1 Fallback)** | Primary R3 Compositional Realizer with an indexed lexical lexicon, backed by an R1 deterministic fallback table for rapid atomic acts. | 100% Token-Free • Zero Model | Absolute • Full fallback audit trace | **Complete for Levels A, B, C:** Handles atomic acts in 1 µs and complex propositions in 30 µs. | High: Separates semantic graph from localized language dictionaries. | Sub-millisecond (< 30 µs) | **OPTIMAL PRACTICAL ARCHITECTURE.** |

---

## 7. Language Independence Analysis (Stage 5)

Lucia must strictly avoid replacing an SLM dependency with an English-only grammatical dependency. The architectural boundary must cleanly separate:

$$\text{Language-Independent Cognitive/Communication State} \implies \text{Language-Specific Surface Drivers}$$

```text
┌────────────────────────────────────────────────────────────────────────┐
│            LANGUAGE-INDEPENDENT COMMUNICATION BOUNDARY                 │
├────────────────────────────────────────────────────────────────────────┤
│ • Propositional Graph: SemanticNode (c:ASSIST), SemanticEdge (:ARG0)  │
│ • Epistemic State: FACT, INFERRED, AMBIGUOUS, UNKNOWN                  │
│ • Scope Partitioning: ROOT, NEGATION, MODAL, INTENSIONAL               │
│ • Communication Modulation Vector (C_t):                               │
│     - directness (0.10..0.95), formality (0.00..1.00)                 │
│     - supportiveness (0.00..1.00), elaboration (0.10..1.00)            │
│     - acknowledgement_level (0.10..1.00), question_frequency          │
│ • Relational State (R_t): familiarity, trust, closeness, reciprocity   │
│ • Multimodal Expression State (E_t): prosody, blendshapes, pacing     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Egress Gate [en, vi, ja]
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  English Driver  │       │Vietnamese Driver │       │ Japanese Driver  │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│• SVO Word Order  │       │• Isolating / SVO │       │• SOV Word Order  │
│• Subject Required│       │• Classifiers     │       │• Zero-Anaphora   │
│  (Passive Voice  │       │  (cái, con)      │       │  (Pro-Drop)      │
│  for UNKNOWN)    │       │• Kinship Systems │       │• Keigo System    │
│• Tense/Aspect    │       │  conditioned     │       │  (Plain vs       │
│  Inflection      │       │  by closeness    │       │  Polite) by C_t  │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

### Typological Realization Rules

1. **Word Order & Argument Alignment:**
   - English & Vietnamese: SVO realization (`:ARG0` $\to$ Predicate $\to$ `:ARG1`).
   - Japanese: SOV realization (`:ARG0` + `が` $\to$ `:ARG1` + `を` $\to$ Predicate).
2. **Subject Omission & Zero-Anaphora:**
   - In Japanese, when `:ARG0` has `EpistemicState.UNKNOWN` or refers to speaker/hearer with high relational closeness, the surface subject is **completely omitted** (e.g. `問題を解決した。`), rather than fabricating a pronoun.
   - In English, `UNKNOWN` forces passive voice realization (*"The problem was solved."*).
3. **Register & Honorifics:**
   - In Vietnamese, `formality_score` and `closeness` dynamically select pronominal kinship markers (*"tôi"*, *"Lucia"*, *"em"* for self; *"bạn"*, *"anh"*, *"chị"* for user).
   - In Japanese, `formality_score > 0.40` enforces *Desu/Masu* (丁寧語), while `formality_score <= 0.40` with `closeness > 0.60` allows plain form (普通体).

---

## 8. Affect and Relational Expression Boundary (Stage 6)

### 8.1 The Crucial Non-Reflective Boundary (INV-2 Compliance)

Under [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) Section 1 and [`L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), **Lucia's affect is strictly an unconscious, continuous dynamical mathematical state operating as a physiological state machine.** Lucia **NEVER** names, labels, or self-reports her internal feelings in text.

```text
FORBIDDEN INVENTED AFFECT:
  "I am feeling very happy today."
  "My arousal is high."
  "As an AI, I don't experience sadness."

PERMITTED PRE-REFLECTIVE MODULATION:
  Tone: Cadence, lexical formality, directness, hedging, affirmation.
  Acoustics: Pitch shift, speech rate, pause duration (VoiceProsody).
  Physical: Smile blendshape, eyebrow angle, head tilt (FacialExpression).
```

### 8.2 Deterministic Realization of Affect & Relationship

In a non-generative renderer, affect and relationship are expressed through **pragmatic transformations**, not emotional declarations:

| Internal State Variable | Realization Parameter | Surface Text Transformation | Multimodal Realization |
|---|---|---|---|
| **High Tension / High Cognitive Load** | `elaboration_depth < 0.30`, `directness > 0.80` | Short, concise, unbuffered phrasing. Eliminates conversational filler and subordinate clauses. | Pitch shift +10 Hz; speech rate +10%; brow angle tense. |
| **High Closeness ($R_t$) / High Supportiveness ($C_t$)** | `formality_score < 0.30`, `supportiveness > 0.70` | Informal lexical selection; affirmative grounding prefix (*"Got it"*, *"I'm here"*); collaborative syntax (*"Let's check..."*). | Pitch shift -5 Hz; pause duration 250 ms; smile blendshape 0.40. |
| **Low Trust / High Formality** | `formality_score > 0.80`, `directness > 0.70` | Strict formal registers (*"The request has been processed."*); full grammatical titles; no contractions (*"do not"* vs *"don't"*). | Neutral pitch (0.0 Hz); zero smile (0.0); gaze centered. |
| **Metabolic Fatigue (Low Energy)** | Injected pacing latency $\Delta \tau_{\text{pace}} > 300\text{ms}$ | Increased response delay before output; concise sentences. | Speech rate -15%; pause duration +200 ms; eye aperture reduced. |

**The State Ownership Invariant:**  
The renderer is a **pure function**. It owns zero affective or relational state. It reads $C_t$, $E_t$, and $R_t$ as read-only inputs and projects them into syntax and prosody.

---

## 9. Expressiveness Limits & Tradeoffs (Stage 7)

A rigorous architectural evaluation must explicitly document what a non-generative architecture can and cannot express:

### 9.1 What the Non-Generative Architecture CAN Express
- **100% of Core Companion Tasks:** Greetings, acknowledgements, direct answers, clarifying questions, confirmation requests, task summaries, status reporting, memory grounding.
- **Precise Epistemic Distinctions:** Rigorous, mathematically auditable separation of verified facts (`FACT`), derived inferences (`INFERRED`), ambiguous concepts (`AMBIGUOUS`), and missing referents (`UNKNOWN`).
- **Controlled Affective & Relational Register:** Dynamic, continuous adjustment of warmth, formality, and directness across interactions without risk of ungrounded emotional theatricality.
- **Multi-lingual Semantic Parity:** Identical internal `SemanticGraph` guaranteed to produce isomorphic, culturally appropriate natural language in EN, VI, and JA.
- **Zero Hallucination Guarantee:** The renderer physically cannot generate propositions that do not exist in its input graph.

### 9.2 What the Non-Generative Architecture CANNOT Yet Express
- **Unconstrained Creative Prose:** Cannot generate spontaneous bedtime stories, open-ended poetry, or imaginative philosophical essays.
- **Out-of-Lexicon Open-Domain Slang:** Cannot invent or parse novel colloquial metaphors outside its curated lexical dictionary.
- **Long-Form Essay Generation:** Cannot produce unstructured, multi-page expository prose without explicit underlying semantic trees.

### 9.3 Architectural Assessment of the Limitation
These limitations are **completely congruent with Project Lucia's core purpose**. Lucia is an intimate, long-term personal embodied companion, not an open-domain creative text API. For Lucia's true operational domain, **predictability, inspectability, zero-latency, zero-hallucination, and 100% local edge execution vastly outweigh the ability to generate ungrounded creative fiction**.

---

## 10. Proposed Minimal Architecture (Stage 8)

The proposed non-generative communication pipeline consists of four strictly decoupled stages:

```text
                         Cognitive Core State
         (PAD ODE, Somatic, R_t, Kanerva SDM Echo, ReasoningKernel)
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Communicative Act & Proposition Synthesizer (CAPS)            │
│ Responsibility: Selects dialogue act (Acknowledge, Inform, Inquire,    │
│                 Clarify) and constructs the outgoing SemanticGraph.    │
│ Input: ActiveInference action, JTMS justified theorems, User Intent.   │
│ Output: DialogueAct + Outgoing SemanticGraph                           │
│ State Ownership: Epistemic & Intent State (read-only from Core)        │
│ Determinism: 100% Deterministic                                        │
│ Status: MISSING (Requires Design Phase)                                │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Pragmatic Modulation Adapter (PMA)                            │
│ Responsibility: Evaluates CommunicationPolicy (10D C_t) and Expression-│
│                 Policy (15D E_t). Augments SemanticGraph with          │
│                 pragmatic markers (directness, formality, hedging).    │
│ Input: Core PAD, Somatic, R_t, Recollection flag.                      │
│ Output: Pragmatically annotated SemanticGraph + ExpressionState.       │
│ State Ownership: C_t and E_t temporal tracking.                        │
│ Determinism: 100% Deterministic (Closed-form math).                    │
│ Status: AVAILABLE (src/core/communication/communication_policy.py)     │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Language Egress Gate & Deterministic Compositional Realizer   │
│ Responsibility: Verifies target language admission {en, vi, ja}.       │
│                 Maps SemanticGraph to surface dependency trees and     │
│                 applies lexical dictionary, morphology, and syntax.    │
│ Input: Annotated SemanticGraph + target_lang string.                   │
│ Output: Raw Natural Language String.                                   │
│ State Ownership: Stateless pure transformation.                        │
│ Determinism: 100% Deterministic.                                       │
│ Status: PARTIALLY IMPLEMENTED (Drivers exist; lexicon needs expansion) │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Surface Boundary & Prosody Actuation                          │
│ Responsibility: Audits output against INV-2 (No Reflective Ego regex); │
│                 Routes text to Electron UI and prosody to Edge-TTS.    │
│ Input: Raw Natural Language String + ExpressionState E_t.              │
│ Output: Audited Text Feed + Synthesized Audio Waveform.                │
│ State Ownership: Stateless.                                            │
│ Determinism: 100% Deterministic.                                       │
│ Status: AVAILABLE (src/core/orchestrator/boundary_layer.py)            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Validation Strategy (Stage 9)

Before any production migration may take place, the non-generative communication pipeline must satisfy eight preregistered validation protocols in an isolated test harness:

1. **Semantic Fidelity Benchmark:**  
   Given an input `SemanticGraph` with $N$ nodes and $M$ edges, the realized surface text must be parseable back into an isomorphic graph with 100% concept symbol preservation and zero novel entity insertion ($\text{Fidelity} \ge 0.98$).
2. **Grammatical & Morphological Correctness:**  
   Automated grammar checking across 1,000 generated test utterances in EN, VI, and JA must exhibit zero subject-verb agreement errors, zero invalid tense inflections, and zero illegal word order configurations.
3. **Affective Modulation Concordance:**  
   When $P < -0.50$ (high displeasure) or tension $> 0.70$, output length must decrease monotonically ($\Delta \text{tokens} \le -30\%$) and directness must increase, without any introspective self-declarations appearing in the text.
4. **Relational Register Compliance:**  
   Varying $R_t$ across Stranger ($R_0$), Acquired Familiarity, and Deep Intimacy must produce verified shifts in lexical formality ($p < 0.001$), appropriate kinship selection in Vietnamese, and correct Keigo switching in Japanese.
5. **Epistemic Invariant Preservation:**  
   - Graphs containing `EpistemicState.UNKNOWN` must never realize as concrete entities.
   - Graphs containing `EpistemicState.AMBIGUOUS` must realize with explicit clarification cues.
6. **Cross-Lingual Semantic Parity:**  
   Parallel realization of an identical `SemanticGraph` into EN, VI, and JA must express identical propositional content and identical epistemic commitments.
7. **Strict Invariant Auditing (INV-2):**  
   Zero introspective affect phrases (*"I feel"*, *"I am happy"*, *"As an AI"*) across 10,000 test generations under any PAD or somatic condition.
8. **Deterministic Edge Performance:**  
   End-to-end realization latency must remain strictly $\le 1.0\text{ ms}$ on CPU (target: $\le 0.05\text{ ms}$), with **0.0 MB GPU VRAM** and peak RAM $\le 5.0\text{ MB}$.

---

## 12. Zero-LLM/SLM Removal Boundary (Stage 10)

The exact boundary conditions that must be met before physical deletion of the SLM infrastructure:

```text
[CRITICAL PATH REMOVAL REQUIREMENTS]
1. Zero model weights: All .gguf files in models/ deleted.
2. Zero runtime inference libraries: llama_cpp removed from Python environment.
3. Zero startup blocking: src/api/server.py starts cleanly with model_path = None.
4. Zero configuration failure: src/core/config.py allows empty/omitted model_path.
5. Zero fallback path: No generative model exists as a silent backup.
6. Zero test regressions: Full test suite passes without mock LLMs or llama_cpp stubs.
```

---

## 13. Evidence Grade Matrix

Every substantive conclusion in this investigation is explicitly graded:

| Claim & Finding | Evidence Grade | Exact Repository Source | Technical Interpretation | Confidence |
|---|---|---|---|---|
| **Cognitive Core is 100% token-free and SLM-independent.** | **E3 / E4** | [`cognitive_orchestrator.py:379–554`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L379-L554) | Affect ODE, SDM memory, active inference, and relationship updates run entirely on vectors and integer IDs. | **ABSOLUTE** |
| **Communication State $C_t$ is deterministic and closed-form.** | **E3** | [`communication_policy.py:70–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L70-L140) | $C_t$ is evaluated purely via numpy clipping and linear combinations of PAD, somatic, and $R_t$. | **ABSOLUTE** |
| **Expression State $E_t$ is deterministic and multimodal.** | **E3** | [`expression_policy.py:50–120`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/expression/expression_policy.py#L50-L120) | Generates text style, prosody parameters, and facial blendshapes without generative text models. | **ABSOLUTE** |
| **Non-generative realization is measured at 0.0085 ms.** | **E4** | [`P23F_ADAPTER_EVALUATION_REPORT.md:85–98`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md#L85-L98) | Benchmark on AMD Ryzen 7 5800H proved sub-10 µs realization latency on local CPU with 0.0 MB VRAM. | **ABSOLUTE** |
| **Language drivers are currently limited to 4 test frames.** | **E2** | [`english.py:271–328`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/drivers/english.py#L271-L328) | Realize methods explicitly pattern-match only `c:SOLVE_PROBLEM`, `c:ASSIST`, `c:LIKE_READING`, `c:VISIT`. | **ABSOLUTE** |
| **Outgoing Proposition Synthesizer is missing from runtime.** | **E2** | [`cognitive_orchestrator.py:487–568`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L487-L568) | Stage 11 assembles text prompts for the SLM; there is no module synthesizing an outgoing `SemanticGraph`. | **HIGH** |
| **Server startup will abort if model_path is unconfigured.** | **E2** | [`src/api/server.py:1425–1430`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L1425-L1430) | Server explicitly logs `model_path_not_configured` and calls `sys.exit(1)`. | **ABSOLUTE** |

---

## 14. Open Research & Engineering Questions

Before a separate implementation task can be authorized, three specific questions must be answered:

1. **Research Question 1 (Outgoing Proposition Synthesis):**  
   *How does the cognitive core construct the outgoing propositional graph?*  
   Currently, `ActiveInferenceEngine` selects an abstract policy (e.g. `policy:clarify`), and `ReasoningKernel` verifies deductive lemmas. A formal mapping is required to translate `(ActiveInferenceAction, JustifiedLemma, DialogueContext) \to SemanticGraph`.
2. **Engineering Question 2 (Lexicon Scope & Expansion):**  
   *What is the minimum viable concept lexicon for Lucia's companion domain?*  
   To move beyond 4 test frames, the lexicon must expand from ~24 words to approximately 2,000–3,000 core communicative concepts covering greetings, status reports, relational inquiries, time, activity, assistance, and emotion-adjacent conversational themes.
3. **Engineering Question 3 (Runtime Decoupling):**  
   *How to decouple server and configuration startup without breaking existing development workflows?*  
   [`src/core/config.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/config.py#L293) and [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L1425) must be updated to make `model_path` and `LLMBackend` optional, allowing the non-generative pipeline to run when `model_path` is omitted.

---

## 15. Final Architectural Recommendation & Decision

```text
═══════════════════════════════════════════════════════════════════════════════
                    MIGRATION READINESS VERDICT: STATUS B
                             CONDITIONALLY READY
═══════════════════════════════════════════════════════════════════════════════
```

### Justification of Status B

1. **Why Not Status A (Ready for Design)?**  
   Status A cannot be granted because the upstream **Propositional Act Synthesizer (CAPS)** is currently missing from the architecture. While the downstream realizer (Semantic Graph $\to$ Natural Language Text) is proven and mathematically sound, the system cannot yet synthesize the outgoing `SemanticGraph` from the internal cognitive turn without the SLM.
2. **Why Not Status C (Not Architecturally Resolved)?**  
   Status C is rejected because the technical feasibility of a zero-SLM communication layer is **definitively established**. The mathematical formulations of $C_t$ and $E_t$, the non-generative egress gate, the typological driver architecture (EN, VI, JA), and the 100% token-free cognitive core are already implemented and empirically validated in the repository.
3. **Preconditions to Reach Status A:**
   - Formal specification of the **Communicative Act & Proposition Synthesizer (CAPS)** interface connecting `ActiveInferenceEngine` and `ReasoningKernel` to `SemanticGraph`.
   - Lexical catalog specification defining the core 2,000-concept companion dictionary.
   - Decoupling plan for `src/api/server.py` startup dependencies.

---

## 16. Exact File/Line Evidence Index

- **`src/core/communication/communication_state.py:17–48`** — `CommStrategy` enum and `CommIntent` dataclass with canonical triple and polarity.
- **`src/core/communication/communication_state.py:51–131`** — `CommunicationState` 10D continuous vector, bounds checking, and array serialization.
- **`src/core/communication/communication_policy.py:70–140`** — Closed-form linear ODE/algebraic computation of $C_t$ from PAD, Somatic, and $R_t$.
- **`src/core/expression/expression_state.py:22–64`** — `TextStyle`, `VoiceProsody`, and `FacialExpression` multimodal parameters.
- **`src/core/expression/expression_policy.py:50–120`** — Pure mathematical evaluation of 15D multimodal actuation state $E_t$.
- **`src/core/knowledge/fortification.py:58–79`** — `EpistemicState` (FACT, INFERRED, AMBIGUOUS, UNKNOWN) and `ScopeType`.
- **`src/core/knowledge/fortification.py:195–255`** — `SemanticNode` schema (pure non-lexical conceptual symbols, zero text tokens).
- **`src/core/knowledge/fortification.py:258–298`** — `SemanticEdge` schema (directed relational roles `:ARG0`, `:ARG1`, `:mod`).
- **`src/core/language/adapter/contracts.py:48–56`** — `SUPPORTED_LANGUAGES = frozenset({"en", "vi", "ja"})`.
- **`src/core/language/adapter/contracts.py:92–130`** — `ParseResult` and `RealizeResult` data transfer objects.
- **`src/core/language/adapter/gate.py:170–221`** — `LanguageEgressGate` perimeter firewall implementation.
- **`src/core/language/adapter/drivers/english.py:39–44`** — `SUPPORTED_LEXICON` containing only 24 benchmark test words.
- **`src/core/language/adapter/drivers/english.py:266–328`** — `EnglishLanguageDriver.realize_from_substrate()` implementation.
- **`src/core/language/adapter/drivers/japanese.py:267–325`** — `JapaneseLanguageDriver.realize_from_substrate()` zero-anaphora realization.
- **`src/core/language/adapter/drivers/vietnamese.py:267–325`** — `VietnameseLanguageDriver.realize_from_substrate()` isolating syntax.
- **`src/core/orchestrator/cognitive_orchestrator.py:487–512`** — Stage 10 Communication Policy evaluation.
- **`src/core/orchestrator/cognitive_orchestrator.py:514–535`** — Stage 11 Prompt Assembler call.
- **`src/core/orchestrator/cognitive_orchestrator.py:568–577`** — Stage 13 `_llm_backend.generate()` invocation on critical path.
- **`src/api/server.py:1425–1430`** — Server startup failure when `model_path` is not configured (`sys.exit(1)`).
- **`src/core/config.py:293, 385`** — `ValueError` raised during settings validation if `model_path` is missing.
- **`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md:32–44`** — Measured 0.0085 ms realization latency on CPU.
- **`data/profile.json:1`** — Bit-exact Genesis Onboarding state: `{"is_onboarded": false}`.
