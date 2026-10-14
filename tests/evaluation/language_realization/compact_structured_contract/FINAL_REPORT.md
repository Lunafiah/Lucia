# Stage 3-C Evaluation Report: Compact Structured Realization Contract Evaluation

> **Experiment**: Stage 3-C — Compact Structured Realization Contract Evaluation  
> **Status**: COMPLETED / ISOLATED EVALUATION  
> **Target Subsystem**: S11 Realization Input Boundary (`PromptAssembler` vs Compact Structured Contract)  
> **Model**: `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (SHA-256: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`)  
> **Corpus**: 42 Paired Semantic Fixtures from Stage 3-A/3-B (14 EN, 14 VI, 14 JA)  
> **Hardware Evaluated**: NVIDIA GeForce RTX 3050 Ti Laptop GPU (CUDA sm_86, 32 layers offloaded, `llama-cpp-python` v0.3.20)  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code / Architecture Changes**: ZERO (Strictly Isolated Evaluation)  

---

## Executive Summary

Stage 3-C empirically evaluated whether replacing the current flattened natural-language directives (`Condition A`) with a **compact structured realization contract** (`Condition B`, targeting <80 tokens encoding communicative act, semantic roles `:ARG0`/`:ARG1`/`:ARG2`, polarity, epistemic status, and scope) improves semantic fidelity and closes GAP-01/GAP-05 on `LFM2.5-1.2B`.

The evaluation was executed as a controlled, paired study across all 42 fixtures under identical seed (`seed=42`), decoding parameters (`temperature=0.3`, `max_tokens=96`), and deterministic evaluation harness.

### Key Quantitative Findings:

* **Condition A (Current Flattened Representation) Error Rate**: **50.0%** (21 / 42 fixtures failed semantically).
* **Condition B (Compact Structured Contract) Error Rate**: **85.7%** (36 / 42 fixtures failed semantically).
* **Delta Error Rate ($\Delta = \text{ERR}_B - \text{ERR}_A$)**: **+35.71%** (severe performance degradation).
* **Transitions**:
  - **`RESOLVED` (Fixed by Contract)**: **0 / 42 (0.0%)** — Not a single fixture was cured by introducing the contract.
  - **`REGRESSED` (Broken by Contract)**: **15 / 42 (35.7%)** — 15 fixtures that succeeded under Condition A failed under Condition B.
  - **`UNCHANGED` (Identical Outcome)**: **27 / 42 (64.3%)**.
* **Payload Budget & Overhead**:
  - Average contract payload: **89.12 tokens** (slightly exceeded the 80-token target by ~9 tokens due to compact rule strings).
  - Total prompt tokens: **300.24** (B) vs **306.90** (A) ($\Delta = -6.66$ tokens).
  - Latency overhead: **703.61 ms** (B) vs **708.90 ms** (A) ($\Delta = -5.29$ ms, functionally identical).

---

## 1. Comparative Analysis: Condition A vs Condition B

### 1.1 Transition & Error Rate Summary

```text
Condition A (Current Flattened):   21 / 42 errors (50.0%)
Condition B (Structured Contract): 36 / 42 errors (85.7%)
Paired Error Rate Delta:           +35.71% (p < 0.001)

Transition Breakdown:
  - Resolved (A Fail -> B Pass):    0 ( 0.0%)
  - Regressed (A Pass -> B Fail):  15 (35.7%)
  - Unchanged:                     27 (64.3%)
```

### 1.2 Error Category Breakdown

| Error Category | Condition A Count | Condition B Count | Net Change ($\Delta$) | Manifestation Mechanism |
|---|---|---|---|---|
| **`ARGUMENT_ENTITY_LOSS`** | 21 | 36 | **+15 (Regressed)** | Model fails to bind `:ARG0`/`:ARG1` tokens, reverting to generic conversational filler |
| **`COMMUNICATIVE_ACT_FAILURE`** | 5 | 6 | **+1 (Regressed)** | Model ignores formal `ACT: REFUSE` / `ACT: CLARIFY` tokens and engages in speculation |
| **`CONTRADICTED`** | 2 | 3 | **+1 (Regressed)** | Direct assertion of negated events despite explicit `POLARITY: NEG` contract tag |
| **`EPISTEMIC_DISTORTION`** | 0 | 0 | **0** | No epistemic promotion observed in either condition |
| **`UNSUPPORTED_ADDITION`** | 0 | 0 | **0** | No ungrounded factual additions |

### 1.3 Per-Language Breakdown

| Language | Total Fixtures | Condition A Errors | Condition B Errors | Delta ($\Delta_{\text{ERR}}$) | Resolved | Regressed |
|---|---|---|---|---|---|---|
| **English (`en`)** | 14 | 6 (42.9%) | **12 (85.7%)** | **+42.9%** | 0 | 6 |
| **Vietnamese (`vi`)** | 14 | 10 (71.4%) | **13 (92.9%)** | **+21.4%** | 0 | 3 |
| **Japanese (`ja`)** | 14 | 5 (35.7%) | **11 (78.6%)** | **+42.9%** | 0 | 6 |

---

## 2. Qualitative Failure Mode Analysis: Why Did Condition B Fail?

Detailed inspection of the paired outputs (`paired_comparison.jsonl`) reveals three concrete root causes for the degradation under Condition B:

### 2.1 Lack of Inductive Bias for Dense DSL / Structured Tokens
`LFM2.5-1.2B` was pretrained and instruction-tuned predominantly on natural prose dialogue. When presented with formal contract syntax such as:
```text
[STRUCTURED REALIZATION CONTRACT]
ACT: ASSERT | POLARITY: POS | EPISTEMIC: FACT
EVENT: deployment_status | ARG0: release_version_2
```
The model treats `ARG0: release_version_2` as foreign code or prompt noise rather than as semantic argument bindings. Instead of realizing the target proposition in natural prose, the model retreats to conversational evasions (e.g. *"That sounds like a lot to handle..."*, *"I see. It’s okay to feel that way..."*, *"You seem to be working hard..."*), completely dropping the required arguments.

### 2.2 Cross-Lingual Distraction on Non-English Targets
In Vietnamese and Japanese fixtures, injecting English DSL keywords (`ACT:`, `EVENT:`, `ARG0:`, `RULE:`) severely disrupted the SLM's language-conditioning subspace:
* On Vietnamese fixture `vi_pair_a_inferred`, Condition A produced valid Vietnamese dialogue, whereas Condition B caused the model to hallucinate in English:
  - *Condition B Output*: `"*You seem to be working hard. That’s admirable! It’s been a long day—maybe you need a break?*"`
* On Japanese fixtures, the model repeatedly dropped target lexical anchors to output generic polite formulas (*"いつも応援しています"*), losing specific predicates entirely.

### 2.3 Instruction-Following Floor
Even when explicit natural language rules were appended to the contract (e.g. `RULE: State event NOT completed/occurred. NEVER affirm.`), the 1.2B model continued to affirm negated events (e.g. in `vi_pair_b_negated` and `en_pair_b_negated`). This confirms that the failure is not simply a representation syntax issue, but an **intrinsic parameter capacity floor** of the 1.2B realizer.

---

## 3. Disentanglement: Preserving Structure vs Model Limitation

Stage 3-C provides unambiguous empirical evidence disentangling the two hypotheses:

| Factor | Hypothesis Tested | Empirical Finding |
|---|---|---|
| **Preserving Structure (GAP-01/GAP-05)** | Does providing structured slot bindings in prompt space improve semantic realization? | **Negative**. Without model fine-tuning, feeding structured contracts into an off-the-shelf 1.2B SLM increases confusion and argument omission. |
| **Model Limitation (Stage 3-B)** | Is semantic loss dominated by the 1.2B parameter realizer's incapacity? | **Confirmed (Dominant)**. The 1.2B realizer lacks the capacity to parse structured contracts and follow complex pragmatic constraints. |

---

## 4. Mandated Evaluation Verdict

Among the four mandated evaluation options:
1. `Structural benefit supported`
2. `No meaningful benefit`
3. `Mixed / phenomenon-specific benefit`
4. `Inconclusive`

```text
========================================================================
STAGE 3-C VERDICT:
No meaningful benefit — model limitation vẫn chi phối
========================================================================
```

### Official Rationale:
The compact structured contract yielded **zero resolved errors (0/42)** and an **elevated error rate (85.7% vs 50.0%)**, with **15 regressions**. 

The intrinsic capacity and instruction-following limitations of the `LFM2.5-1.2B` realizer completely dominate the realization boundary. The model cannot natively parse or ground dense DSL structured contracts without dedicated fine-tuning.

---

## 5. Architectural Implications

1. **Contract Validity vs Prompt-Level Remediation**:
   - The structured realization contract has **high architectural value** as an internal invariant contract between CAPS and Stage S11, and as a formal specification for deterministic Stage S14 verification gates.
   - However, **the contract is completely insufficient on its own as a prompt-level remediation for realization quality** on an off-the-shelf 1.2B SLM.
2. **Path to GAP-01 Closure**:
   - GAP-01 cannot be solved by simply restructuring prompt text for a 1.2B model.
   - Closing GAP-01 requires either:
     - **Supervised Fine-Tuning (SFT) / LoRA**: Training the realizer specifically on the structured contract format.
     - **Scaling the Realizer**: Moving to a 3B–7B parameter SLM with native structured instruction-following capabilities.
     - **Deterministic Stage S14 Fail-Closed Gate**: Automatically detecting and rejecting realizations that suffer from `ARGUMENT_ENTITY_LOSS` or `CONTRADICTED` prior to P24 expression.
