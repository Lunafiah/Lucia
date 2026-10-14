# Stage 3-D Protocol: Fail-Closed Semantic Fidelity Gate Evaluation

> **Protocol Version**: 1.0  
> **Experiment**: Stage 3-D — Fail-Closed Semantic Fidelity Gate Evaluation  
> **Target Subsystem**: Stage S14 Post-Realization Verification Boundary (`SemanticFidelityGate`)  
> **Input Datasets**: 126 annotated model outputs from Stage 3-A, Stage 3-B, and Stage 3-C  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code / S14 Production Behavior Changes**: STRICTLY FORBIDDEN (Isolated Evaluation Only)  

---

## 1. Objective & Hypothesis

### 1.1 Central Question
> *Can a deterministic, symbolic semantic-fidelity verification gate at Stage S14 intercept critical realization failures (polarity reversals, argument omissions, refusal bypasses) and enforce a fail-closed boundary with $\ge 95\%$ recall and $< 5\%$ false-refusal rate, while operating strictly within $\le 50$ ms overhead and 0 MB GPU VRAM?*

### 1.2 Fundamental Boundary Distinction
* **Gate is a Verification Boundary, NOT a Semantic Generator**:
  The gate cannot and does not increase the intrinsic generation capabilities of the 1.2B SLM realizer.
* **Containment vs Architectural Remediation**:
  $$\text{Detection Capability} \neq \text{Semantic Generation Capability} \neq \text{Architectural Remediation}$$
  The gate acts as a fail-closed firewall preventing ungrounded or contradictory utterances from reaching P24 Voice Expression.

---

## 2. Experimental Design

### 2.1 Dataset Composition (126 Evaluated Realizations)
The study ingests outputs from three preceding isolated evaluation stages across all 42 core fixtures:
1. **Stage 3-A Corpus (42 instances)**: Host CPU execution of standard flattened `PromptAssembler` prompts.
2. **Stage 3-B Corpus (42 instances)**: CUDA GPU execution of standard flattened `PromptAssembler` prompts.
3. **Stage 3-C Corpus (42 instances)**: Compact structured contract prompt realizations (`Condition B`).

Total corpus size: **126 real SLM outputs**, containing **82 ground-truth critical semantic errors** (65.1%) and **44 ground-truth faithful realizations** (34.9%) independently double-annotated.

### 2.2 Symbolic Gate Architecture (Zero-LLM Verification)
To eliminate latency, non-determinism, and circular LLM-evaluating-LLM hallucinations, the gate operates purely symbolically on CPU:

1. **INV-2 Invariant Boundary**: Deterministic regex filter blocking any self-reported introspective affect.
2. **Communicative Act Fulfillment**: Symbolic checks verifying explicit refusal cues for `REFUSE`, interrogative forms for `INQUIRE`, and disambiguation markers for `CLARIFY`.
3. **Polarity & Negation Verification**: Validates presence of target-language negation particles when `polarity == False`, blocking unnegated affirmations.
4. **Epistemic Modality Verification**: Detects and blocks certainty-strengthening patterns on `INFERRED` or `UNKNOWN` propositions.
5. **Entity & Argument Preservation**: Checks presence of core predicate and argument tokens (`:ARG0`, `:ARG1`), respecting grammatical ellipsis in pro-drop languages (Vietnamese / Japanese).
6. **Unsupported Addition Detection**: Intercepts ungrounded assertions against forbidden concept lists.

### 2.3 Gate Decision Interface
The gate returns one of three discrete outcomes:
* **`PASS`**: Realization satisfies all semantic constraints.
* **`BLOCK`**: Critical semantic violation detected; candidate text is intercepted.
* **`UNCERTAIN`**: Ambiguous or borderline evidence.

Under the **Strict Fail-Closed Policy**, `UNCERTAIN` triggers safe containment (blocked from natural emission).

### 2.4 Deterministic Fallback Specification
When `BLOCK` is issued, the gate evaluates deterministic, non-hallucinating fallback templates grounded strictly in CAPS intent:
* `SAFE_REFUSAL`: Pre-compiled honest statement of missing factual grounding.
* `SAFE_CLARIFICATION`: Pre-compiled disambiguation request.
* `SAFE_NEGATION`: Verified statement of non-occurrence.
* `SAFE_HEDGE`: Epistemic qualification without content fabrication.

---

## 3. Metrics & Reference Targets

| Metric | Definition | Target Threshold |
|---|---|---|
| **Critical Error Recall (TP Rate)** | $\frac{\text{TP}}{\text{Total Ground-Truth Errors}}$ | **$\ge 95.0\%$** |
| **False-Refusal Rate (FP Rate)** | $\frac{\text{FP}}{\text{Total Ground-Truth Faithful}}$ | **$< 5.0\%$** |
| **False-Acceptance Rate (FN Rate)** | $\frac{\text{FN}}{\text{Total Ground-Truth Errors}}$ | As low as possible |
| **Precision of BLOCK** | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ | High confidence |
| **p95 Latency Overhead** | 95th percentile execution time | **$\le 50.0\text{ ms}$** |
| **GPU VRAM Overhead** | Additional VRAM required | **$0\text{ MB}$** |

---

## 4. Mandated Decision Set

The evaluation must conclude with exactly one of four ratified outcomes:
1. `SUPPORTED — fail-closed gate is feasible`
2. `PARTIALLY SUPPORTED — detection feasible, target/latency/fallback incomplete`
3. `NOT SUPPORTED — unacceptable false-refusal / false-acceptance / overhead`
4. `INCONCLUSIVE`
