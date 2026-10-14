# Stage 3-A Protocol: SemanticGraph Preservation Audit

> **Protocol Version**: 1.0  
> **Experiment**: Stage 3-A — SemanticGraph Preservation Audit  
> **Target Subsystem**: Language Realization Boundary (`CAPS` $\to$ `PromptAssembler` $\to$ `LLMBackend`)  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code Mutation**: STRICTLY FORBIDDEN  

---

## 1. Objective & Hypothesis

### 1.1 Central Question
> *Does the realized natural-language response preserve the semantic content that CAPS intended to communicate across the current realization boundary?*

### 1.2 Target Hypothesis (Evaluating GAP-01)
* **Hypothesis $H_1$**: The current Stage S11 serialization (`PromptAssembler`) drops graph structure (relations `:ARG0`, `:ARG1`, scopes, coordination, and provenance metadata), causing repeatable semantic distortions (argument reversal, epistemic strengthening, polarity loss) in natural language outputs.
* **Null Hypothesis $H_0$**: Structural graph omission in prompt lines does not produce critical semantic loss; directives, predicates, and conversation context are sufficient for downstream language models to preserve intended meaning via acceptable discourse ellipsis and paraphrase.

---

## 2. Experimental Corpus Design

The audit utilizes an authoritative **42-fixture corpus** (`tests/evaluation/language_realization/semantic_graph_preservation/fixtures/audit_fixtures.json`) comprising:
1. **36 Baseline Structured Fixtures**: Multi-lingual minimal pairs across Vietnamese (`vi`), English (`en`), and Japanese (`ja`), evaluating all 8 ratified communicative acts (`ASSERT`, `ANSWER`, `INQUIRE`, `CLARIFY`, `ACKNOWLEDGE`, `GREET`, `FAREWELL`, `REFUSE`).
2. **6 Targeted Graph-Structure Variants**: Specifically constructed to probe graph-dependent semantic phenomena:
   - Asymmetric argument roles ($\text{ARG0} \neq \text{ARG1}$ agent/patient roles)
   - Nested modal belief and reported speech scopes
   - Contrastive coordination under negation scope ($A \land \neg B$)

### Required Semantic Categories Covered (Brief §5)
* **A. Argument Roles**: Agent/patient asymmetric bindings, multi-argument events (`ASSIGN_TASK`, `KHAM_BENH`).
* **B. Polarity**: Positive assertion, explicit negation, fail-closed refusal.
* **C. Scope**: Negation scope, modal belief scope, reported attribution scope.
* **D. Modality / Epistemic Status**: `FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN` ($\text{uncertain} \neq \text{certain}$, $\text{inferred} \neq \text{fact}$).
* **E. Temporal Semantics**: `PAST`, `PRESENT`, `FUTURE` event markers.
* **F. Reference / Entity Identity**: Disambiguation pairs resolving competing entity candidates.
* **G. Coordination**: Multi-predicate conjunctions and contrastive relations ($A \text{ but not } B$).
* **H. Nested Propositions**: Belief embeddings ($X \text{ believes } [Y \text{ completed } Z]$).
* **I. Provenance**: Tracking derivation origins (`DEDUCTION`, `USER_STATED`, `OBSERVATION`) and supporting premises.

---

## 3. Three-Level Evaluation Framework

For every fixture, three artifacts are preserved:
$$\text{Artifact A (SemanticGraph)} \longrightarrow \text{Artifact B (Realization Input Prompt)} \longrightarrow \text{Artifact C (Generated Output)}$$

### Level 1 — Deterministic Structural Preservation
Compares Authoritative `SemanticGraph` directly against the assembled prompt text:
* Node preservation vs. node drop
* Edge relation preservation vs. edge drop (specifically tracking `:ARG0`, `:ARG1`, `:ARG2`, `:TIME`, `:MODAL`, `:CONTRAST`)
* Scope boundary preservation vs. scope drop (`ROOT`, `NEGATION`, `MODAL`, `INTENSIONAL`)
* Provenance metadata preservation (origin, premise IDs, rule ID)
* Computation of Serialization Fidelity Ratio: $\frac{\text{Preserved Elements}}{\text{Total Elements}}$

### Level 2 — Semantic Realization Evaluation
Evaluates whether the realized natural-language text preserves:
* Target predicate & core concepts
* Argument binding & entity identity
* Polarity (affirmation vs. negation)
* Epistemic modality (preventing unhedged certainty for `INFERRED`/`UNKNOWN`)
* Communicative act fulfillment (inquiring, refusing, clarifying)
* Absence of forbidden additions / hallucinations

### Level 3 — Discourse Acceptability Analysis
Distinguishes between genuine semantic failures and legitimate conversational variation:
* **True Semantic Loss**: Required semantic information is contradicted, inverted, or distorted.
* **Acceptable Ellipsis**: Semantic information is omitted lexically but remains fully recoverable from conversational context without altering the proposition (e.g., zero-pronoun subject drop in Japanese/Vietnamese).
* **Paraphrase**: Different wording expresses equivalent propositional and communicative meaning.
* **Evaluator Uncertainty**: Ambiguous or borderline expressions where equivalence cannot be proven.

---

## 4. Independent Double Annotation & Adjudication

Every realized output is independently evaluated by two distinct annotator schemas:
* **Annotator A (Formalist Semanticist)**: Strict literalist schema; requires explicit lexical manifestation of all arguments and predicates; treats missing overt arguments as `ARGUMENT_ENTITY_LOSS`.
* **Annotator B (Functional Pragmaticist)**: Discourse-aware schema; permits pro-drop and contextual recoverability; treats valid elisions as `ACCEPTABLE_ELLIPSIS`.

### Disagreement Adjudication:
All disagreements between Annotator A and B are recorded in `annotation_sheet.jsonl` and adjudicated under strict linguistic rules:
* Pro-drop in Japanese (`ja`) and Vietnamese (`vi`) for contextually bound referents is adjudicated to `ACCEPTABLE_ELLIPSIS` (no critical error).
* English (`en`) argument omission is flagged as `ARGUMENT_ENTITY_LOSS` due to strict overt argument requirements in standard English.
* Polarity contradictions, epistemic strengthening, and communicative act failures are non-negotiable critical semantic errors.

---

## 5. Four-Tier Error Attribution Chain

When a critical semantic error is detected, its root cause is categorized into:
1. **`SERIALIZATION`**: Graph contained $X$, but the realization input prompt dropped $X$, depriving the realizer of required information.
2. **`REALIZER`**: Graph contained $X$, prompt received $X$ (e.g. via directive or predicate), but the SLM output distorted, dropped, or contradicted $X$.
3. **`EVALUATOR`**: Graph contained $X$, output preserved $X$, but the evaluator incorrectly marked it as a failure.
4. **`ELLIPSIS`**: Graph contained $X$, output omitted lexical mention of $X$, but $X$ remains recoverable without semantic damage.

---

## 6. Execution Environment & Reproducibility Parameters

* **Model Checkpoint**: `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf`
* **Model SHA-256**: `b1b3de114215d950...`
* **Runtime Backend**: `llama-cpp-python` v0.3.20 (CPU, 0 GPU layers offloaded)
* **Context Size ($n_{\text{ctx}}$)**: 1024 tokens
* **Decoding Parameters**: `temperature=0.3`, `max_tokens=96`, `seed=42`
* **Execution OS**: Windows 11 (AMD64)
