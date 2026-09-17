# Phase 22 H1 — R3 Epistemic Relevance & Action-Value Attribution Study

> **Status:** RESEARCH EVIDENCE RECORD — ARCHITECTURE GATE STRICTLY LOCKED  
> **Governance Invariants:** Phase 22 H1 is **INCONCLUSIVE** | Quality Gate 2 is **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$)  
> **ADR-029 Status:** **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**  
> **Production Admission:** **NOT ADMITTED** (Zero mutations to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Gate:** `data/profile.json` preserved bit-exact `{"is_onboarded": false}`  
> **Scope:** Evaluates continuous action-value differentiation, orthogonal variance decomposition, and directional correspondence under the Epistemic-Action Relevance Diagnostic (research-harness proxy)  
> **Hardware Discipline:** 100% CPU Execution / 0.0 MB GPU VRAM Allocation  
> **Date:** September 2026  
> **Artifact Type:** Formal Research Specification & Evidence Report (Phase 22 H1)

---

## 1. Executive Summary

This study addresses the fundamental question left open by previous Phase 22 H1 investigations:

> **When two states have nearly identical scalar surprise ($|\Delta S| \le 0.020$) but different directional residuals ($\mathbf{d}_i \ne \mathbf{d}_j$), does the directional information encoded by $R3 = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ correspond to measurable differences in the expected values of available actions ($V(a \mid s)$), or does it merely produce downstream action differentiation by nudging marginal actions across arbitrary decision boundaries?**

Previous studies demonstrated that R3 differentiates states that were previously scalar-collapsed, and that this effect is sensitive to directional correspondence under tested consumers. However, action identity differentiation ($\operatorname{argmax}$ flips) alone is a binary, thresholded observable that cannot distinguish between:
1. Meaningful restructuring of continuous action values ($V(a)$);
2. Trivial boundary noise pushing nearly tied actions across a sharp decision threshold;
3. Uniform common-mode shifts that elevate or depress all actions equally without altering their relative ranking or trade-offs.

To resolve this ambiguity, this study deploys the **Epistemic-Action Relevance Diagnostic** across 358 matched discordant probe pairs on the canonical Candidate G1 stimulus corpus ($N=270$, Master Seed 9999) across 4 downstream consumers and 5 conditions under 5 consumer robustness seeds (42–46).

```
                 [R3 Epistemic Action-Value Attribution Architecture]
                                          │
    ┌─────────────────────────────────────┴─────────────────────────────────────┐
    ▼                                                                           ▼
[Canonical Signed Valuation V]                                     [Orthogonal Variance Decomposition]
- Consumer C: V = U (Utility, higher = better)                     ||ΔV||² = SS_cm (6 * Δ_bar²) + SS_spec (||ΔV - Δ_bar*1||²)
- Consumers A/B/D: V = -G (EFE Cost, higher = better)              - Scalar C0:  80.95% Common-Mode (shifts all actions together)
- Unified metric semantics: ΔV > 0 means higher action value       - Canonical C2: 96.76% Action-Specific (restructures action trade-offs)
```

### Key Empirical Findings

1. **Continuous Valuation Differentiation is Omnipresent**:
   - In Primary Consumer C ($\gamma_C = 1.50$), canonical R3 (Condition C2) produces continuous action-value differentiation ($\|\Delta \mathbf{V}\|_2 > \tau_{\text{val}} = 10^{-4}$) on **$100.00\%$** ($358 / 358$) of discordant pairs, with mean displacement $\|\Delta \mathbf{V}\|_2 = 1.0464 \pm 0.0000$ (median: $1.1713$, P95: $1.1720$).
   - Across all 4 consumers (C, A, B, D), continuous action-value differentiation occurs on **$100.00\%$** of discordant pairs under C2, demonstrating that the observed differentiation rate ($79.89\%$) is a thresholded subset of a continuous underlying valuation divergence.

2. **Action-Specific Restructuring Dominates Total Variance**:
   - Under canonical R3 (C2), orthogonal L2 decomposition reveals that **$96.76\%$** of the valuation variance in Consumer C is **action-specific** ($\text{SS}_{\text{spec}} / \text{SS}_{\text{tot}} = 0.9676$), while common-mode shifts account for only **$3.24\%$**.
   - This pattern replicates across Reference Consumer A ($98.85\%$ action-specific), Separable Consumer B ($97.50\%$ action-specific), and Qualifying Corner D ($96.28\%$ action-specific).
   - In stark contrast, under the scalar baseline (Condition C0), total valuation displacement is minute ($\|\Delta \mathbf{V}\|_2 = 0.0132$) and **$80.95\%$** of it is common-mode. R3 does not merely raise or lower general urgency; it differentially restructures relative action trade-offs.

3. **Directional Correspondence Over Shuffled Multiset Preserving Nulls**:
   - Shuffling direction vectors (Condition C3, preserving probe $S$ and corpus direction multiset) reduces mean valuation displacement from **$1.0464$ down to $0.3857$** ($-63.14\%$ drop, $p < 10^{-6}$) and collapses action differentiation rate to **$29.16\%$**.
   - Independent direction vectors (Condition C5, preserving empirical direction multiset) reduce mean displacement to **$0.3798$** ($-63.70\%$ drop) and differentiation rate to **$24.53\%$**.
   - Directional correspondence contrast $\Delta_{\text{C2-C3}} = +0.6607$ and empirical structure contrast $\Delta_{\text{C2-C5}} = +0.6666$ confirm that action-value restructuring is specifically aligned with stimulus orientation.

4. **Action-Specific Divergence Hierarchy**:
   - Under Consumer C, continuous valuation shifts are concentrated in cognitive actions: `answer` ($\overline{|\Delta V|} = 0.7219$), `clarify` ($0.4483$), `retrieve` ($0.4329$), and `reason` ($0.3474$), whereas `derive` ($0.0496$) and `wait` ($0.0989$) exhibit negligible sensitivity.
   - The directional residual selectively re-weights exploration, clarification, and retrieval relative to immediate execution.

5. **Critical Distinction Between Action-Value Relevance and Epistemic Validity**:
   - The **Epistemic-Action Relevance Diagnostic** satisfies all 5 pre-registered criteria under the evaluated consumers.
   - **Crucial Limitation**: Satisfying this diagnostic demonstrates *action-value relevance under stylized consumer response functions*; it does **NOT** establish *epistemic validity* in the formal Active Inference sense. There is no representation of latent beliefs, Bayesian belief updating, information gain, or expected reduction of uncertainty in this diagnostic harness.

---

## 2. Research Questions & Hypotheses

| RQ # | Research Question | Specific Hypothesis | Evaluation Metric | Outcome |
|---|---|---|---|---|
| **RQ1** | Does directional residual produce genuine continuous action-value differentiation, or merely decision boundary crossing? | $H_1$: Continuous valuation norm $\|\Delta \mathbf{V}\|_2 > \tau_{\text{val}}$ on $>75\%$ pairs. | $\text{DiffRate}_{\text{cont\_val}} = \frac{1}{N_{\text{pairs}}} \sum \mathbb{I}(\|\Delta \mathbf{V}\|_2 > \tau_{\text{val}})$ | **Confirmed (100.00%)** |
| **RQ2** | Is valuation differentiation structured across specific actions, or is it an isotropic common-mode shift? | $H_2$: Action-specific variance exceeds $50\%$ of total variance ($\text{SS}_{\text{spec}} / \text{SS}_{\text{tot}} > 0.50$). | Orthogonal variance decomposition: $\text{action\_specific\_fraction}$ | **Confirmed (96.76%)** |
| **RQ3** | Does continuous valuation differentiation require true directional correspondence to the stimulus? | $H_3$: Mean displacement under C2 significantly exceeds shuffled C3 and independent C5. | Directional correspondence contrast: $\Delta_{\text{C2-C3}} > 0$, $\Delta_{\text{C2-C5}} > 0$ | **Confirmed (+0.6607, +0.6666)** |
| **RQ4** | Which specific actions exhibit the greatest valuation divergence under directional residual? | $H_4$: Action-level divergence $\overline{|\Delta V_a|}$ is non-uniform across the 6 canonical actions. | Action-specific means: $\overline{|\Delta V_a|}$ for $a \in \{\text{answer}, \dots, \text{wait}\}$ | **Confirmed (Non-uniform, max `answer`=0.72)** |
| **RQ5** | Does action-value differentiation establish epistemic validity in the Active Inference sense? | $H_5$: Action-value relevance under stylized consumers does not imply Active Inference epistemic foraging. | Epistemic-Action Relevance Diagnostic status vs Active Inference belief update audit | **Action-Value Relevance: YES / Active Inference Epistemic Validity: NO** |

---

## 3. Valuation Semantics & Sign Normalization

### 3.1 Resolving Sign Mixing Between Utility and Free Energy Cost

In previous iterations, downstream consumer response models employed conflicting native valuation orientations:
- **Consumer C (Multiplicative Utility)**: Native quantity is utility $U(a)$ where **higher is better** ($\operatorname{argmax}_a U(a)$).
- **Consumers A, B, D (Active Inference / EFE Adapters)**: Native quantity is expected free energy cost $G(a)$ where **lower is better** ($\operatorname{argmin}_a G(a)$).

Taking raw differences $\Delta \mathbf{V}$ across consumers without sign normalization inverted the semantic direction of action desirability. To establish rigorous, unambiguous semantics, this study locks the **Canonical Signed Action Value $V(a)$**:

$$\boxed{V(a) \equiv \begin{cases} U(a) & \text{for Consumer C (Utility Model)} \\ -G(a) & \text{for Consumers A, B, D (Cost/Free Energy Models)} \end{cases}}$$

Under this canonical signed quantity:
1. **Higher $V(a)$ is always better** across all four consumers.
2. **Action Selection**: $\operatorname{selected\_action} = \operatorname{argmax}_a V(a) = \begin{cases} \operatorname{argmax}_a U(a) & \text{(Consumer C)} \\ \operatorname{argmin}_a G(a) & \text{(Consumers A, B, D)} \end{cases}$.
3. **Action Probability**: Softmax distribution over canonical signed values:
   $$P(a) = \frac{\exp(\gamma (V(a) - \max_{a'} V(a')))}{\sum_{a''} \exp(\gamma (V(a'') - \max_{a'} V(a')))}$$
4. **Valuation Difference Vector**: For matched probe pair $(i, j)$:
   $$\Delta \mathbf{V} \equiv \mathbf{V}_i - \mathbf{V}_j \in \mathbb{R}^6$$
   where $\Delta V(a) > 0$ indicates that action $a$ is valued more highly (more desirable) in state $i$ than in state $j$.
5. **Native Transparency**: Native quantities ($U(a)$ and $G(a)$) are stored separately and exported alongside canonical values in raw action profiles.

---

## 4. Orthogonal Variance Decomposition

For each discordant probe pair $(i, j)$ with canonical signed action values $\mathbf{V}_i, \mathbf{V}_j \in \mathbb{R}^6$, the pairwise valuation difference is $\Delta \mathbf{V} = \mathbf{V}_i - \mathbf{V}_j$.

The mean shift across all 6 actions represents the **common-mode displacement**:
$$\bar{\Delta} = \frac{1}{6} \sum_{a=1}^6 \Delta V(a)$$

The difference vector decomposes uniquely and orthogonally into common-mode and action-specific components:
$$\Delta \mathbf{V} = \Delta \mathbf{V}_{\text{cm}} + \Delta \mathbf{V}_{\text{spec}} = \bar{\Delta} \mathbf{1}_6 + (\Delta \mathbf{V} - \bar{\Delta} \mathbf{1}_6)$$

The total sum of squares decomposes without cross-terms:
$$\text{SS}_{\text{tot}} = \|\Delta \mathbf{V}\|_2^2 = \sum_{a=1}^6 \Delta V(a)^2$$
$$\text{SS}_{\text{cm}} = \|\Delta \mathbf{V}_{\text{cm}}\|_2^2 = 6 \bar{\Delta}^2$$
$$\text{SS}_{\text{spec}} = \|\Delta \mathbf{V}_{\text{spec}}\|_2^2 = \sum_{a=1}^6 (\Delta V(a) - \bar{\Delta})^2$$

$$\boxed{\text{SS}_{\text{tot}} = \text{SS}_{\text{cm}} + \text{SS}_{\text{spec}}}$$

$$\text{common\_mode\_fraction} = \frac{\text{SS}_{\text{cm}}}{\text{SS}_{\text{tot}}}, \quad \text{action\_specific\_fraction} = \frac{\text{SS}_{\text{spec}}}{\text{SS}_{\text{tot}}} = 1 - \text{common\_mode\_fraction}$$

---

## 5. Experimental Conditions & Exact Multiset Preservation

To prevent permutation artifacts from confounding empirical marginal distributions, negative control conditions C3, C4, and C5 enforce **exact multiset preservation** via deterministic bijections $\pi: \{1, \dots, N\} \to \{1, \dots, N\}$ on the finite corpus ($N=270$):

| Condition | Scalar Input $S_i$ | Direction Vector $\mathbf{v}_{\text{dir}, i}$ | Multiset Preservation Guarantee |
|---|---|---|---|
| **C0** | $S_i$ | $\mathbf{0}_3$ | Pure scalar baseline; direction zeroed |
| **C2** | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{d}_i$ | Canonical R3 ternary residual ($\epsilon=0.010$) |
| **C3** | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{d}_{\pi_{\text{dir}}(i)}$ | **Preserves probe-wise $S$ multiset + direction multiset** (bijection $\pi_{\text{dir}}$ on direction indices) |
| **C4** | $S_{\pi_S(i)}$ | $\frac{1}{\sqrt{3}} \mathbf{d}_i$ | **Preserves probe-wise direction multiset + scalar $S$ multiset** (bijection $\pi_S$ on scalar indices) |
| **C5** | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{d}_{\pi_{\text{indep}}(i)}$ | **Preserves empirical direction multiset** (independent bijection $\pi_{\text{indep}}$); probe-wise $S$ unchanged |

---

## 6. Epistemic-Action Relevance Diagnostic (Research-Harness Proxy)

The diagnostic evaluates 5 pre-registered criteria on matched discordant pairs ($N_{\text{pairs}} = 358$):

| # | Diagnostic Criterion | Operational Threshold | Evaluated Result (C_qual_1.50) | Status |
|---|---|---|---|---|
| **1** | Continuous Valuation Differentiation | $\text{DiffRate}_{\text{cont\_val}} > 0.75$ ($\|\Delta \mathbf{V}\|_2 > \tau_{\text{val}} = 10^{-4}$) | **$100.00\%$** ($358 / 358$) | **PASSED** |
| **2** | Survives Scalar Matched Pairs | $\text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) > \text{mean}(\|\Delta \mathbf{V}_{\text{C0}}\|_2)$ | **$1.0464 > 0.0132$** ($+7827\%$ gain) | **PASSED** |
| **3** | Structured Superiority Over Shuffles | $\text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) > \text{mean}(\|\Delta \mathbf{V}_{\text{C3}}\|_2)$ | **$1.0464 > 0.3857$** ($+171\%$ gain) | **PASSED** |
| **4** | Action-Specific Variance Dominance | $\text{action\_specific\_fraction} > 0.50$ | **$96.76\%$** ($> 50\%$) | **PASSED** |
| **5** | Probability Restructuring | $\text{mean}(D_{\text{JS}}) > \tau_{\text{JS}} = 10^{-5}$ | **$0.024406 > 0.000010$** ($2440\times$) | **PASSED** |

### Critical Scientific Qualification

> [!CAUTION]
> **EPISTEMIC DISCLAIMER**:  
> Passing this diagnostic establishes **action-value relevance under tested stylized consumer response models**.  
> It does **NOT** constitute evidence of **epistemic validity or epistemic foraging** in Active Inference.  
> The diagnostic evaluates static response functions mapping state perturbations $(S, \mathbf{d})$ to action values $V(a)$. It contains **no latent belief states, no variational free energy epistemic term $D_{\text{KL}}[q(s \mid \pi) \parallel p(s)]$, no Bayesian uncertainty reduction, and no information gain**.  
> Action-value relevance and Active Inference epistemic validity must remain strictly decoupled in all governance and architectural deliberations.

---

## 7. Negative Controls Registry

Six negative controls were pre-registered and evaluated:

| Control | Description | Verification Method | Empirical Result |
|---|---|---|---|
| **NC1** | Scalar Baseline Historical Reproduction | C0 action differentiation must be $0.0000$ across all seeds, matching frozen transferability artifact | **$0.0000$ bit-exact match** ($0 / 358$ flips across all consumers) |
| **NC2** | Hard Tuple Identity Parity | Evaluating duplicate $(S, \mathbf{d})$ tuples must yield $\|\Delta \mathbf{V}\|_2 = 0.0$ and $D_{\text{JS}} < 10^{-12}$ | **$\Delta V = 0.0, D_{\text{JS}} = 0.0$** on all 4 consumers |
| **NC3** | Multiset Preservation | Exact multiset equality for $S$ and direction across permutations | **Verified bit-exact** across seeds 42–46 |
| **NC4** | Determinism Across Seeds | Reproducibility across 5 seeds (42–46) | **$\text{std} = 0.0000$** on C2 metrics |
| **NC5** | Production Isolation Audit | Zero modifications to production codebase | **`src/core/**` diff = 0** |
| **NC6** | Genesis Gate Bit-Exact Audit | Preservation of first-activation gate | `data/profile.json` bit-exact `{"is_onboarded": false}` |

---

## 8. Quantitative Empirical Results

### 8.1 Cross-Consumer Summary Across 5 Conditions

All values represent cross-seed means (seeds 42–46) on 358 matched discordant pairs ($|\Delta S| \le 0.020, \mathbf{d}_i \ne \mathbf{d}_j$):

| Consumer Model | Cond | Action DiffRate | Cont Val DiffRate | Mean $\|\Delta \mathbf{V}\|_2$ | Median $\|\Delta \mathbf{V}\|_2$ | Mean $D_{\text{JS}}$ | Common-Mode Frac | Action-Specific Frac | Dir Contribution | Scalar Contribution |
|---|---|---|---|---|---|---|---|---|---|---|
| **C_qual_1.50** | **C0** | $0.0000$ | $1.0000$ | $0.0132$ | $0.0134$ | $0.000001$ | $80.95\%$ | $19.05\%$ | $0.0000$ | $0.0132$ |
| | **C2** | **$0.7989$** | **$1.0000$** | **$1.0464$** | **$1.1713$** | **$0.024406$** | **$3.24\%$** | **$96.76\%$** | **$1.0501$** | $0.0132$ |
| | **C3** | $0.2916$ | $1.0000$ | $0.3857$ | $0.3280$ | $0.006236$ | $41.88\%$ | $58.12\%$ | $0.3796$ | $0.0132$ |
| | **C4** | $0.7989$ | $1.0000$ | $1.0662$ | $1.1687$ | $0.024744$ | $5.10\%$ | $94.90\%$ | $1.0501$ | $0.1114$ |
| | **C5** | $0.2453$ | $1.0000$ | $0.3798$ | $0.4321$ | $0.005928$ | $41.02\%$ | $58.98\%$ | $0.3734$ | $0.0132$ |
| **A_REFERENCE** | **C0** | $0.0000$ | $1.0000$ | $0.0074$ | $0.0075$ | $0.000000$ | $69.50\%$ | $30.50\%$ | $0.0000$ | $0.0074$ |
| | **C2** | **$0.7989$** | **$1.0000$** | **$0.5315$** | **$0.6028$** | **$0.007234$** | **$1.15\%$** | **$98.85\%$** | **$0.5330$** | $0.0074$ |
| | **C3** | $0.2916$ | $1.0000$ | $0.1945$ | $0.1479$ | $0.001885$ | $35.34\%$ | $64.66\%$ | $0.1911$ | $0.0074$ |
| | **C4** | $0.7989$ | $1.0000$ | $0.5494$ | $0.6019$ | $0.007328$ | $5.33\%$ | $94.67\%$ | $0.5330$ | $0.0894$ |
| | **C5** | $0.2453$ | $1.0000$ | $0.1887$ | $0.1943$ | $0.001726$ | $34.44\%$ | $65.56\%$ | $0.1852$ | $0.0074$ |
| **B_SEPARABLE** | **C0** | $0.0000$ | $1.0000$ | $0.0207$ | $0.0209$ | $0.000001$ | $85.91\%$ | $14.09\%$ | $0.0000$ | $0.0207$ |
| | **C2** | **$0.7989$** | **$1.0000$** | **$0.6901$** | **$0.7853$** | **$0.009393$** | **$2.50\%$** | **$97.50\%$** | **$0.6845$** | $0.0207$ |
| | **C3** | $0.2916$ | $1.0000$ | $0.2518$ | $0.1944$ | $0.002445$ | $44.09\%$ | $55.91\%$ | $0.2409$ | $0.0207$ |
| | **C4** | $0.7006$ | $1.0000$ | $0.7013$ | $0.7504$ | $0.009289$ | $8.17\%$ | $91.83\%$ | $0.6845$ | $0.1542$ |
| | **C5** | $0.2453$ | $1.0000$ | $0.2444$ | $0.2510$ | $0.002282$ | $42.83\%$ | $57.17\%$ | $0.2341$ | $0.0207$ |
| **D_CORNER** | **C0** | $0.0000$ | $1.0000$ | $0.0688$ | $0.0696$ | $0.000016$ | $77.47\%$ | $22.53\%$ | $0.0000$ | $0.0688$ |
| | **C2** | **$0.7989$** | **$1.0000$** | **$0.5576$** | **$0.6392$** | **$0.004417$** | **$3.72\%$** | **$96.28\%$** | **$0.5330$** | $0.0688$ |
| | **C3** | $0.2916$ | $1.0000$ | $0.2307$ | $0.1616$ | $0.001310$ | $40.93\%$ | $59.07\%$ | $0.1911$ | $0.0688$ |
| | **C4** | $0.7078$ | $1.0000$ | $0.8229$ | $0.7414$ | $0.005790$ | $40.15\%$ | $59.85\%$ | $0.5330$ | $0.5794$ |
| | **C5** | $0.2453$ | $1.0000$ | $0.2217$ | $0.1876$ | $0.001195$ | $40.01\%$ | $59.99\%$ | $0.1852$ | $0.0688$ |

### 8.2 Action-Specific Valuation Divergence Across 6 Actions ($\overline{|\Delta V_a|}$)

| Consumer Model | Cond | `answer` | `clarify` | `retrieve` | `derive` | `reason` | `wait` |
|---|---|---|---|---|---|---|---|
| **C_qual_1.50** | C0 | $0.0069$ | $0.0026$ | $0.0043$ | $0.0051$ | $0.0017$ | $0.0086$ |
| | **C2** | **$0.7219$** | **$0.4483$** | **$0.4329$** | **$0.0496$** | **$0.3474$** | **$0.0989$** |
| | C3 | $0.2352$ | $0.1478$ | $0.1500$ | $0.0796$ | $0.1089$ | $0.1436$ |
| | C4 | $0.7368$ | $0.4427$ | $0.4422$ | $0.0746$ | $0.3437$ | $0.1408$ |
| | C5 | $0.2310$ | $0.1406$ | $0.1374$ | $0.0792$ | $0.1097$ | $0.1503$ |
| **A_REFERENCE** | C0 | $0.0004$ | $0.0038$ | $0.0037$ | $0.0032$ | $0.0039$ | $0.0000$ |
| | **C2** | **$0.1791$** | **$0.3144$** | **$0.2450$** | **$0.0437$** | **$0.2798$** | **$0.0232$** |
| | C3 | $0.0563$ | $0.1083$ | $0.0843$ | $0.0485$ | $0.0896$ | $0.0517$ |
| | C4 | $0.1781$ | $0.3253$ | $0.2369$ | $0.0540$ | $0.2908$ | $0.0232$ |
| | C5 | $0.0564$ | $0.1005$ | $0.0770$ | $0.0483$ | $0.0908$ | $0.0528$ |
| **B_SEPARABLE** | C0 | $0.0048$ | $0.0065$ | $0.0069$ | $0.0067$ | $0.0147$ | $0.0074$ |
| | **C2** | **$0.2504$** | **$0.3969$** | **$0.3123$** | **$0.0742$** | **$0.3682$** | **$0.0595$** |
| | C3 | $0.0825$ | $0.1345$ | $0.1096$ | $0.0448$ | $0.1204$ | $0.0762$ |
| | C4 | $0.2593$ | $0.3834$ | $0.3270$ | $0.0753$ | $0.3409$ | $0.0717$ |
| | C5 | $0.0819$ | $0.1253$ | $0.1019$ | $0.0482$ | $0.1197$ | $0.0768$ |
| **D_CORNER** | C0 | $0.0129$ | $0.0343$ | $0.0214$ | $0.0257$ | $0.0472$ | $0.0069$ |
| | **C2** | **$0.1696$** | **$0.3420$** | **$0.2267$** | **$0.0148$** | **$0.3168$** | **$0.0301$** |
| | C3 | $0.0617$ | $0.1258$ | $0.0917$ | $0.0620$ | $0.1142$ | $0.0548$ |
| | C4 | $0.2096$ | $0.3709$ | $0.3097$ | $0.2255$ | $0.4563$ | $0.0707$ |
| | C5 | $0.0623$ | $0.1156$ | $0.0853$ | $0.0588$ | $0.1123$ | $0.0566$ |

### 8.3 Directional Correspondence Contrasts on Continuous Valuation Norm

| Contrast Quantity | Description | Consumer C | Consumer A | Consumer B | Consumer D |
|---|---|---|---|---|---|
| **$\text{Gain}_{\text{dir}} = \text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) - \text{mean}(\|\Delta \mathbf{V}_{\text{C0}}\|_2)$** | Directional valuation gain above scalar | **$+1.0332$** | **$+0.5241$** | **$+0.6694$** | **$+0.4888$** |
| **$\Delta_{\text{C2-C3}} = \text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) - \text{mean}(\|\Delta \mathbf{V}_{\text{C3}}\|_2)$** | Directional correspondence attenuation | **$+0.6607$** | **$+0.3370$** | **$+0.4383$** | **$+0.3269$** |
| **$\Delta_{\text{C2-C4}} = \text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) - \text{mean}(\|\Delta \mathbf{V}_{\text{C4}}\|_2)$** | Magnitude scrambling displacement | **$-0.0198$** | **$-0.0179$** | **$-0.0112$** | **$-0.2653$** |
| **$\Delta_{\text{C2-C5}} = \text{mean}(\|\Delta \mathbf{V}_{\text{C2}}\|_2) - \text{mean}(\|\Delta \mathbf{V}_{\text{C5}}\|_2)$** | Empirical structure attenuation | **$+0.6666$** | **$+0.3428$** | **$+0.4457$** | **$+0.3359$** |

---

## 9. Scientific Discussion

### 9.1 Action-Value Relevance is Real, Continuous, and Action-Specific

The primary finding of this study is that R3's downstream behavioral differentiation is **not** an artifact of decision-boundary noise or arbitrary threshold crossings:
1. **Continuous Shifts on Every Pair**: Every single discordant pair ($100.00\%$) exhibits continuous valuation change exceeding the numerical threshold $\tau_{\text{val}} = 10^{-4}$. The $79.89\%$ action switch rate is simply the subset of continuous shifts that happen to change the top-ranked action under the model's base margins.
2. **Action-Specific Trade-Offs**: Under the scalar baseline (C0), valuation differences between stimuli with $|\Delta S| \le 0.020$ are minute ($0.0132$) and overwhelmingly common-mode ($80.95\%$). Under R3 (C2), valuation differences expand by nearly two orders of magnitude ($1.0464$) and shift into action-specific dimensions ($96.76\%$). This directly refutes the hypothesis that R3 acts as a scalar multiplier on general behavioral activation.

### 9.2 Directional Specificity is Robust Across Permutations

When direction vectors are shuffled across stimuli (C3) while preserving the exact multiset of direction vectors across the corpus, valuation displacement collapses from $1.0464$ to $0.3857$ ($-63.14\%$). Supplying independent random direction vectors (C5) reduces displacement to $0.3798$ ($-63.70\%$). This confirms that action-value differentiation is sensitive to the alignment of the direction vector with the stimulus trajectory, rather than being an artifact of injecting generic high-dimensional noise.

### 9.3 Why Action-Value Relevance Does Not Equal Active Inference Epistemic Validity

While the empirical evidence demonstrates action-value relevance within the evaluated consumer models, it is essential to emphasize that **this does not constitute evidence of Active Inference epistemic foraging**:
1. **No Belief Updating**: In standard Active Inference, an epistemic action is valued because it minimizes expected free energy through the reduction of posterior entropy over hidden states:
   $$\mathbf{G}_{\text{epistemic}}(a) = -\mathbb{E}_{q(o, s \mid a)} \left[ \ln \frac{q(s \mid o, a)}{q(s \mid a)} \right]$$
   The evaluated consumers (A, B, C, D) do not maintain hidden state posterior distributions $q(s)$. They are static response functions evaluating algebraic combinations of $S$ and $\mathbf{d}$.
2. **Feedforward Perturbations**: R3 acts as an informative feedforward steering vector that modifies the expected utility or cost of actions. It communicates *which direction the internal limbic state shifted*, not *what uncertainty about the external environment was resolved*.
3. **Architectural Implication**: Calling R3 an "epistemic residual" in previous draft documentation was a conceptual overstatement. R3 is accurately characterized as a **directional state-displacement representation that provides continuous action-value relevance**.

---

## 10. Architectural Verdict & Governance Status

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            FINAL RESEARCH VERDICT                            │
│                                                                              │
│  Epistemic-Action Relevance Diagnostic:     PASSED (5/5 Criteria)            │
│  Continuous Action-Value Relevance:         CONFIRMED (100% pairs, 96.8% AS) │
│  Active Inference Epistemic Validity:       UNPROVEN (Out of Scope)          │
│                                                                              │
│  Phase 22 H1 Status:                        INCONCLUSIVE                     │
│  Quality Gate 2 Status:                     STRICTLY BLOCKED                 │
│  Architecture Gate:                         STRICTLY LOCKED (Diff = 0)       │
│  ADR-029 Status:                            DRAFT / RESEARCH RECORD ONLY     │
└──────────────────────────────────────────────────────────────────────────────┘
```

1. **Architecture Gate**: Remains **`STRICTLY LOCKED`**. Zero production modifications are authorized by these findings.
2. **ADR-029**: Remains **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**.
3. **Quality Gate 2**: Remains **`STRICTLY BLOCKED`** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$). Action-value differentiation in an offline diagnostic does not overcome the fundamental dynamical headroom deficit identified in Stage 1.
4. **Genesis Gate**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
