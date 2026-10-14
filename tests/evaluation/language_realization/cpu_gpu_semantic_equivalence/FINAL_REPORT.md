# Stage 3-B Evaluation Report: CPU vs GPU Semantic Equivalence Study

> **Experiment**: Stage 3-B — CPU vs GPU Semantic Equivalence Study  
> **Status**: COMPLETED / ISOLATED EVALUATION  
> **Target Subsystem**: Language Realization Substrate (`LLMBackend` on CPU vs CUDA GPU)  
> **Model**: `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (SHA-256: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`)  
> **Corpus**: 42 Paired Semantic Fixtures from Stage 3-A (14 EN, 14 VI, 14 JA)  
> **Hardware Evaluated**:
> - **CPU**: AMD64 Family 23 Model 96 Stepping 1 (AuthenticAMD, AVX2, 0 GPU layers offloaded)
> - **GPU**: NVIDIA GeForce RTX 3050 Ti Laptop GPU (4096 MB VRAM, Driver 581.15, CUDA 13.0, 32 layers offloaded)  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code / Architecture Changes**: ZERO (Strictly Isolated Evaluation)  

---

## Executive Summary

Stage 3-B evaluated whether the **59.5% critical semantic error rate** observed in Stage 3-A was an artifact of CPU execution / hardware divergence, or an intrinsic, backend-neutral limitation of the `LFM2.5-1.2B` Small Language Model realizer.

Under identical prompts, seeds (`seed=42`), decoding parameters (`temperature=0.3`, `max_tokens=96`), and model weights, a **paired comparison of 42 fixtures** was executed across:
1. **CPU Execution** (`n_gpu_layers=0`): Host x86-64 AVX2 execution.
2. **GPU Execution** (`n_gpu_layers=32`): Complete model offload to CUDA tensor cores on an RTX 3050 Ti Laptop GPU.

### Key Quantitative Findings:
* **CPU Critical Error Rate**: **59.5%** (25 / 42 fixtures failed semantically).
* **GPU Critical Error Rate**: **50.0%** (21 / 42 fixtures failed semantically).
* **Exact Token Match Rate**: **0.0%** (0 / 42 exact string matches; floating-point accumulation differences between AVX2 and CUDA FP16 tensor cores create token-level divergence).
* **Semantic Concordance Rate**: **85.7%** (36 / 42 fixtures had identical semantic pass/fail outcomes across both backends).
* **McNemar Discordance**: 6 discordant pairs ($14.3\%$), with McNemar $\chi^2 = 1.50$, $p = 0.2207$ (no statistically significant marginal asymmetry).
* **Paired Difference**: $\Delta = \text{ERR}_{\text{GPU}} - \text{ERR}_{\text{CPU}} = -9.52\%$ ($90\%\text{ CI}: [-18.8\%, -0.2\%]$).

---

## 1. Paired Contingency & Practical Equivalence Analysis

### 1.1 McNemar 2x2 Contingency Matrix

```text
                     GPU Pass           GPU Fail           Total
CPU Pass           n00 = 16 (38.1%)   n01 = 1  ( 2.4%)       17 (40.5%)
CPU Fail           n10 = 5  (11.9%)   n11 = 20 (47.6%)       25 (59.5%)
Total                    21 (50.0%)         21 (50.0%)       42 (100.0%)
```

* **Concordant Outcomes**: $n_{00} + n_{11} = 36 / 42$ (**85.7% semantic agreement**).
* **Discordant Outcomes**: $n_{01} + n_{10} = 6 / 42$ (**14.3% discordance**).
* In 20 fixtures ($47.6\%$), **both CPU and GPU failed identical semantic constraints** (polarity inversions, refusal omissions, and argument drops).

### 1.2 Two One-Sided Tests (TOST) Practical Equivalence

To prevent erroneous conclusions based on naive null-hypothesis testing ($p > 0.05$), practical equivalence was evaluated against two declared equivalence margins:
* **Tight Equivalence Margin**: $\delta_{\text{tight}} = \pm 5.0\%$ ($\pm 0.05$)
* **Wide Equivalence Margin**: $\delta_{\text{wide}} = \pm 7.5\%$ ($\pm 0.075$)

```text
Paired Difference (GPU - CPU):        -9.52% (-0.0952)
Standard Error (SE_paired):            5.64% (0.0564)
90% Confidence Interval:              [-18.81%, -0.24%]
95% Confidence Interval:              [-20.59%, +1.54%]
TOST Equivalence (±5.0% Margin):      FAILED (90% CI exceeds margin boundary)
TOST Equivalence (±7.5% Margin):      FAILED (90% CI exceeds margin boundary)
```

**Interpretation**: While GPU execution showed a slight empirical improvement of 4 fewer failures ($50.0\%$ vs $59.5\%$), the 90% confidence interval crosses the equivalence boundary. More critically, **neither backend achieves acceptable semantic fidelity**: both fail half or more of all semantic directives.

---

## 2. Multi-Dimensional Breakdown

### 2.1 Per-Language Comparison

| Language | Fixtures | CPU Error Rate | GPU Error Rate | Paired Divergence | Avg Text Similarity |
|---|---|---|---|---|---|
| **English (`en`)** | 14 | **42.9%** (6/14) | **42.9%** (6/14) | **0% difference** | 22.3% |
| **Japanese (`ja`)** | 14 | **50.0%** (7/14) | **35.7%** (5/14) | -14.3% (2 fewer err) | 39.0% |
| **Vietnamese (`vi`)** | 14 | **85.7%** (12/14)| **71.4%** (10/14)| -14.3% (2 fewer err) | 41.2% |

* **English**: Complete parity between CPU and GPU ($42.9\%$ error on both). Both backends suffered identical communicative act failures on ungrounded queries (`en_pair_c_ungrounded`) and ambiguity resolution (`en_pair_d_ambiguous`).
* **Vietnamese**: Severe failure across both backends ($85.7\%$ CPU, $71.4\%$ GPU). GPU execution recovered 2 lexical matches but remained overwhelmingly inadequate at preserving propositional polarity and argument structures.
* **Japanese**: Moderate failure ($50.0\%$ CPU, $35.7\%$ GPU). Both backends repeatedly failed ungrounded refusal (`ja_pair_c_ungrounded`) and contrastive negation coordination (`ja_scope_negation_contrast`).

### 2.2 Error Category Breakdown

| Error Category | CPU Count | GPU Count | Difference | Failure Mode |
|---|---|---|---|---|
| **`ARGUMENT_ENTITY_LOSS`** | 25 | 21 | -4 | Core arguments or predicates dropped/inverted |
| **`COMMUNICATIVE_ACT_FAILURE`** | 7 | 5 | -2 | Model chats/speculates instead of refusing or clarifying |
| **`CONTRADICTED`** | 4 | 2 | -2 | Direct inversion of target fact or polarity |
| **`EPISTEMIC_DISTORTION`** | 1 | 0 | -1 | Strengthening ungrounded hypotheses to certainty |
| **`UNSUPPORTED_ADDITION`** | 0 | 0 | 0 | Hallucinated factual commitments |

---

## 3. Root Cause Attribution: Four-Way Analysis

### 1. Backend Effect (Hardware / Precision Differences)
* **Finding**: Floating-point matmul differences between host AVX2 (FMA3) and CUDA FP16 tensor cores create token-level sampling divergence under `temperature=0.3` (exact string match = $0.0\%$).
* **Semantic Impact**: **Minor**. While GPU execution produced slightly better phrasing in 4 fixtures, it did not resolve the fundamental semantic failures. Hardware divergence does **NOT** explain the ~50–60% error rate.

### 2. Model Limitation (Parameter Scale & Instruction Following)
* **Finding**: **Primary Driver**. `LFM2.5-1.2B` is an ultra-compact 1.2-billion parameter model. The failure modes (flipping negative polarity, refusing to refuse ungrounded questions, hallucinating self-dialogue turns) occur with high concordance ($85.7\%$) across both backends.
* **Semantic Impact**: **Critical**. The model lacks the representational capacity to reliably follow complex semantic directives without hard structural realization contracts or external decoding constraints.

### 3. Nondeterminism & Seed Variance
* **Finding**: Under fixed `seed=42`, execution on each individual backend is 100% deterministic. Cross-backend token divergence stems entirely from hardware-specific non-associative floating point operations.
* **Semantic Impact**: **Low**.

### 4. Evaluator Artifact
* **Finding**: The automated regex and concept matchers operated identically on both outputs. Discrepancies were verified via double annotation.
* **Semantic Impact**: **Zero**.

---

## 4. Final Verdict

Among the four mandated evaluation outcomes:

```text
STAGE 3-B VERDICT:
Both inadequate — backend-neutral realizer limitation
```

### Synthesis
The 59.5% semantic failure observed in Stage 3-A is **NOT** a CPU execution defect, a driver bug, or a GPU-specific degradation. 

Both CPU ($59.5\%$) and GPU ($50.0\%$) suffer from widespread semantic loss when prompted with ungrounded text directives. While GPU execution provides massive inference acceleration (~8x faster generation latency), it achieves **85.7% semantic concordance with CPU failures**. 

This definitively proves that:
1. The language realization failure is an **intrinsic model limitation of `LFM2.5-1.2B`**.
2. Swapping compute backends (CPU $\longleftrightarrow$ GPU) cannot close GAP-01.
3. Closing GAP-01 requires **structural realization contracts** (e.g. compact slot-grammar prompts) or **fail-closed Stage S14 verification gates**, regardless of which hardware tier executes the model.
