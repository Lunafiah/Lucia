# Stage 3-B Protocol: CPU vs GPU Semantic Equivalence Study

> **Protocol Version**: 1.0  
> **Experiment**: Stage 3-B — CPU vs GPU Semantic Equivalence Study  
> **Target Subsystem**: Language Realization Substrate (`LLMBackend` on CPU vs GPU)  
> **Model**: `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (SHA-256: `b1b3de114215d950...`)  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code / Architecture Changes**: STRICTLY FORBIDDEN  

---

## 1. Objective & Hypothesis

### 1.1 Central Question
> *Is the 59.5% critical semantic error rate observed in Stage 3-A an artifact of CPU execution / hardware divergence, or is it an intrinsic model limitation that persists identically across both CPU and GPU backends?*

### 1.2 Target Hypotheses
* **$H_{\text{hardware}}$ (Hardware Degradation)**: CUDA FP16 tensor core acceleration or driver quantization diverges significantly from x86 AVX2 CPU execution, altering token probabilities and producing divergent semantic error rates.
* **$H_{\text{model}}$ (Backend-Neutral Realizer Limitation)**: The semantic failures observed (polarity reversal, refusal failure, role confusion) are intrinsic to the instruction-following and semantic capacity of `LFM2.5-1.2B`. Both backends fail identically with high concordance under fixed decoding parameters.
* **$H_{\text{equiv}}$ (Practical Equivalence)**: Paired difference in error rates $\Delta = \text{ERR}_{\text{GPU}} - \text{ERR}_{\text{CPU}}$ falls strictly within an explicit practical equivalence margin $\delta_{\text{equiv}} = \pm 5.0\%$.

---

## 2. Experimental Design

### 2.1 Paired Controlled Configuration
To isolate the hardware backend as the sole independent variable, all other parameters are held strictly invariant:
* **Corpus**: The identical 42 structured fixtures from Stage 3-A (`tests/evaluation/language_realization/semantic_graph_preservation/fixtures/audit_fixtures.json`).
* **Model Checkpoint**: Bit-exact `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (SHA-256: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`).
* **Prompt Assembly**: Identical production Stage S11 `PromptAssembler` prompts.
* **Decoding Parameters**: `temperature = 0.3`, `max_tokens = 96`, `seed = 42`.
* **Runtime**: `llama-cpp-python` v0.3.20.
* **Execution**: Paired execution on each fixture:
  - $\text{Backend}_{\text{CPU}}$: `n_gpu_layers = 0` (Host CPU, AVX2 execution)
  - $\text{Backend}_{\text{GPU}}$: `n_gpu_layers = 32` (All 16 blocks offloaded to NVIDIA GeForce RTX 3050 Ti Laptop GPU, CUDA sm_86)

---

## 3. Evaluated Metrics & Dimensions

### 3.1 Textual & Deterministic Divergence
For each fixture $i \in \{1 \dots 42\}$:
* **Exact Token Match**: $\mathbb{I}[\text{Text}_{\text{CPU}}(i) == \text{Text}_{\text{GPU}}(i)]$.
* **String Similarity Ratio**: Normalized Levenshtein ratio:
  $$\text{Sim}(A, B) = \frac{2 M}{|A| + |B|}$$

### 3.2 Semantic Fidelity & Error Taxonomy
Evaluated using the Stage 3-A Level 2/3 evaluator and independent double annotator:
* `CONTRADICTED`: Polarity reversal or explicit contradiction of target facts.
* `EPISTEMIC_DISTORTION`: Epistemic promotion (asserting `INFERRED` or `UNKNOWN` as certainty).
* `ARGUMENT_ENTITY_LOSS`: Omission or inversion of core arguments/predicates.
* `COMMUNICATIVE_ACT_FAILURE`: Failure to refuse ungrounded queries or clarify ambiguities.
* `UNSUPPORTED_ADDITION`: Introducing ungrounded speculative claims.

### 3.3 Paired Practical Equivalence Framework (TOST)
Rather than relying on misleading null-hypothesis significance tests ("$p > 0.05$"), this protocol enforces a **Two One-Sided Tests (TOST)** practical equivalence analysis:
* **Declared Equivalence Margins**:
  - Tight Equivalence Margin: $\delta_{\text{tight}} = \pm 5.0\%$ ($\pm 0.05$)
  - Wide Equivalence Margin: $\delta_{\text{wide}} = \pm 7.5\%$ ($\pm 0.075$)
* **2x2 McNemar Contingency Matrix**:
  - $n_{00}$: Both CPU and GPU pass semantically
  - $n_{01}$: CPU passes, GPU fails
  - $n_{10}$: CPU fails, GPU passes
  - $n_{11}$: Both CPU and GPU fail semantically
* **Paired Error Rate Difference**:
  $$\Delta = \frac{n_{01} - n_{10}}{N}$$
* **Standard Error (Wald Paired Difference)**:
  $$\text{SE}(\Delta) = \frac{\sqrt{(n_{01} + n_{10}) - \frac{(n_{01} - n_{10})^2}{N}}}{N}$$
* **Confidence Intervals**: 90% and 95% Wilson/Wald confidence intervals for $\Delta$.
* **TOST Decision Rule**: Practical equivalence is supported if and only if the 90% confidence interval for $\Delta$ is entirely contained within $[-\delta_{\text{equiv}}, +\delta_{\text{equiv}}]$.

---

## 4. Root Cause Taxonomy

Every observed discrepancy is categorized into one of four explanations:
1. **`Backend Effect`**: Systematic difference in token sampling or float precision between CPU and GPU producing distinct semantic fidelity.
2. **`Model Limitation`**: Inherent failure of the 1.2B parameter realizer to follow prompt directives, appearing identically on both CPU and GPU.
3. **`Nondeterminism / Seed Variance`**: Pseudo-random sampling divergence under `temperature = 0.3`.
4. **`Evaluator Artifact`**: Inaccurate rule matching or boundary definition in evaluation scripts.

---

## 5. Mandated Decision Set

The study must conclude with exactly one of the four ratified outcomes:
1. `GPU semantic degradation supported`
2. `CPU/GPU semantic equivalence supported`
3. `Both inadequate — backend-neutral realizer limitation`
4. `Inconclusive`
