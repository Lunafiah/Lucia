# Phase 23-D — EXP-01: Compositionality & Recursion Report

> **Experiment ID:** EXP-01  
> **Status:** `[EVALUATION REPORT / COMPLETE]`  
> **Governance:** Isolated under `evaluation/evaluation_phase23d/experiment_01_compositionality/`  
> **Production Mutation:** 0 files modified (Zero changes to `src/core/**` or runtime)

---

## 1. Executive Summary

Experiment 01 empirically evaluated the capacity of three candidate semantic architectures (**UMR-TPG**, **V-UMR**, **DRS-Graph**) and an auxiliary baseline (**HDC-Pure**) to preserve variable/role bindings, nested propositional structures, negation scoping, and path recovery across recursion depths $D \in \{1, 2, 3, 4\}$.

Input was delivered as deterministic abstract semantic structures, strictly isolating the substrate's representational fidelity from natural-language parsing artifacts.

---

## 2. Quantitative Results Summary

| Candidate Architecture | Architecture Role | SPRR ($D=1$) | SPRR ($D=2$) | SPRR ($D=3$) | SPRR ($D=4$) | BER | Scope Pres. (SPR) | Cross-Talk (CTR) | Mean Latency | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **Primary** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.000** | $0.017\text{ ms}$ | **`PASS`** |
| **V-UMR** | **Secondary** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.000** | $1.587\text{ ms}$ | **`PASS`** |
| **DRS-Graph** | **Control** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.000** | $0.018\text{ ms}$ | **`PASS`** |
| **HDC-Pure** | **Auxiliary Baseline** | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.833 | 0.000 | $0.335\text{ ms}$ | **`FAIL`** |

---

## 3. Key Findings per Candidate

### 3.1 Primary Candidate: UMR-TPG (`PASS`)
- **Recursion Fidelity:** Achieved $100\%$ Structural Path Reconstruction Rate across all depths $D \in \{1, 2, 3, 4\}$, successfully avoiding the $D \ge 4$ degradation boundary observed in the C4 hybrid baseline ($83.5\%$).
- **Binding Preservation:** Zero binding errors ($\text{BER} = 0.000$) across 64 tested role-filler bindings.
- **Adversarial Invariance:** Maintained $100\%$ accuracy on role inversion ($ARG0(A) \to ARG1(B)$ vs $ARG0(B) \to ARG1(A)$) and repeated entities across hierarchical levels.
- **Isolation:** Produced zero cross-talk ($\text{CTR} = 0.000$) against pre-existing independent assertions.

### 3.2 Secondary Candidate: V-UMR (`PASS`)
- **Structural Integrity:** Inherited the full topological fidelity of UMR-TPG ($\text{SPRR} = 1.000$, $\text{BER} = 0.000$).
- **Synchronization Latency:** Incurred an average execution latency of $1.587\text{ ms}$ due to the generation of 32D metric coordinates and 1024D hypervector bindings (an ~90× increase compared to pure UMR-TPG's $0.017\text{ ms}$, but well within the $\le 5.0\text{ ms}$ engineering SLA).

### 3.3 Control Candidate: DRS-Graph (`PASS`)
- **Scoping Rigor:** Box-subordinated partitioning maintained perfect negation and modal scoping ($\text{SPR} = 1.000$).
- **Deterministic Traversal:** Direct box-condition traversal resolved all paths at $0.018\text{ ms}$.

### 3.4 Auxiliary Baseline: HDC-Pure (`FAIL`)
- **Superposition Collapse:** As established in Phase 22-SC and Phase 23-C, dense hypervector unbinding without an explicit graph backbone collapses under nested compositionality, confirming why dense hypervectors cannot serve as the primary persistent substrate.

---

## 4. Epistemological Scope Boundaries

> [!CAUTION]
> **Strict Governance Boundary:**  
> The positive findings of EXP-01 **MUST NOT** be used to claim:
> 1. That UMR-TPG is officially adopted for production in Lucia.
> 2. That cross-lingual parsing (EN, VI, JA) is solved.
> 3. That 20W edge CPU feasibility is proven for full multimodal dialogue.
> 4. That 100,000-fact long-term memory scaling is proven.
>
> **EXP-01 answers strictly one scientific question:**  
> *Under controlled, direct semantic ingestion, can candidate graph substrates preserve compositional binding, deep recursion ($D=4$), and negation scope without signal degradation or cross-talk?*  
> **Answer: YES for UMR-TPG, V-UMR, and DRS-Graph; NO for HDC-Pure.**
