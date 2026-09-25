# Phase 23-D — Research Baseline & Inherited Evidence Ledger

> **Document Type:** Research Lineage, Established Baselines & Empirical Boundaries  
> **Status:** `[CANONICAL RESEARCH BASELINE]`  
> **Authority:** `AGENTS.md` §0; `docs/specs/phase23/`; `evaluation_artifacts/phase23/`  
> **Target Horizon:** Phase 23-D Falsifiable Architecture Evaluation

---

## 1. Lineage & Architectural Ancestry

Phase 23-D does not begin in a theoretical vacuum. It directly inherits validated empirical findings, architectural constraints, and negative results from previous development and research phases:

```text
Phase 21 (Production Implemented)
└── Long-Term Relational Consolidation, Synaptic Homeostasis & Dynamic Attractor (ADR-028)
     │
     ▼
Phase 22-SC (Research Validated)
└── Substrate-Neutral Semantic Interface: RelationalConditioningState (120–180 bytes)
└── Phase 22-SSF Negative Finding: Semantic Continuity ≠ Open-Loop Accumulation of Continuous Latents
└── Phase 22-SC Failure Analysis: Pure dense HDC hypervectors collapse under superposition (N > 5)
     │
     ▼
Phase 23-C (Research Validated Working Baseline)
└── Falsification of Sentence Embedding Hypothesis (H_embed): Role swap & negation collapse
└── C4 Hybrid Baseline (Typed Property Graph + 1024D HDC Gestalt): RF3 = 86.4% (D ≤ 3)
└── Closed-Loop Continuous-Discrete Coupling: Lyapunov stable (λ_max = -0.0206 ≤ 0.0)
└── SDM Attractor Noise Rejection: D50 = 0.000 under σ = 0.25 Gaussian perturbation
     │
     ▼
Phase 23-D Evaluation Scaffold (Current Horizon)
└── Rigorous head-to-head evaluation of UMR-TPG vs V-UMR vs DRS-Graph across 6 capability tracks
```

---

## 2. Definitive Empirical Findings Inherited from Phase 23-C

The following empirical facts were formally demonstrated by automated test suites in `tests/evaluation/phase23/` across multiple preregistered random seeds (`[42, 1337, 2026, 7113, 8421]`):

### 2.1 Falsification of the Sentence Embedding Hypothesis ($\mathcal{H}_{\text{embed}}$)
In `test_p23c_e3_role_swap_adversarial.py`, dense sentence transformers (Multilingual MiniLM-L12-v2, LaBSE) were subjected to adversarial grammatical transformations across English, Vietnamese, and Japanese:
- **Role Swap Sensitivity:** Reversing thematic roles (*"Lucia helps the user"* vs *"The user helps Lucia"*) produced sentence embedding cosine similarities of **$0.914$ to $0.942$**, completely failing to differentiate the agent from the patient.
- **Polarity Reversal:** Adding negation particles (*not, không, ない*) shifted embeddings by less than $15^\circ$ (cosine similarity **$0.887$ to $0.923$**), rendering semantic negation invisible to metric retrieval.
- **Evidentiary Conclusion:** Pure dense vector embeddings are fundamentally incapable of serving as a primary compositional semantic substrate.

### 2.2 Capability Boundaries of Candidate Representations (C1–C5)
The Phase 23 Microbenchmark v0.2 evaluated five structural paradigms on proposition nesting across recursion depths $D \in \{1, 2, 3, 4\}$:

| Paradigm | Architecture | $RF_1$ ($D=1$) | $RF_2$ ($D=2$) | $RF_3$ ($D=3$) | $RF_4$ ($D=4$) | Failure Mode |
|---|---|---|---|---|---|---|
| **C1** | Pure Slot-Value Frame | 100.0% | 100.0% | 100.0% | 100.0% | Zero continuous metric; incompatible with ODE limbic resonance |
| **C2** | Pure Property Graph | 100.0% | 100.0% | 100.0% | 100.0% | No fixed-size summary vector for fast associative recall |
| **C3** | Dense HDC Superposition | 52.6% | 28.3% | 22.8% | 15.2% | **Superposition crosstalk collapse:** noise destroys constituents at $N > 4$ |
| **C4** | Hybrid Graph + HDC Gestalt | **93.6%** | **87.2%** | **86.4%** | **83.5%** | Gestalt degrades beyond $D \ge 4$; dual-state synchronization cost |
| **C5** | Smolensky TPR ($16 \times 16$) | 100.0% | 62.5% | 41.7% | 31.2% | **Capacity saturation:** fixed-rank tensor cannot unbind deep nests |

**Baseline Boundary:** Candidate C4 was adopted as the working baseline because its topological graph backbone prevents structural unbinding collapse ($RF_3 = 86.4\% \ge 85.0\%$), while its HDC gestalt provides a fast continuous interface. However, **C4 exhibits clear degradation at $D \ge 4$ ($83.5\%$)**.

### 2.3 Closed-Loop Stability & Associative Immunity
- **Continuous Coupling Stability:** The bidirectional coupling between the continuous MT-LNN ODE ($[P, A, D]$) and discrete semantic state transitions is asymptotically stable ($\lambda_{\max} = -0.0206 \le 0.0$) when hysteresis deadbands ($\pm 0.08$) are enforced.
- **SDM Attractor Stability:** Auto-associative retrieval in Kanerva Sparse Distributed Memory (SDM) exhibits zero coordinate drift ($D_{50} = 0.000$) over 50 consecutive recall cycles under Gaussian noise ($\sigma = 0.25$) with 20 active distractors.

---

## 3. Motivation for Phase 23-D: Beyond the C4 Working Baseline

While C4 proved the feasibility of a hybrid graph-vector representation, it leaves critical architectural challenges unresolved:

1. **Ad-Hoc Graph Grammar vs Formal Semantic Substrate:**  
   The C4 graph implementation in Phase 23-C relied on handcrafted Neo-Davidsonian event schemas. It lacked a standardized semantic grammar capable of cross-lingual parsing and generation.
2. **Cross-Lingual Typological Asymmetries:**  
   Vietnamese and Japanese exhibit pervasive **zero-anaphora (pro-drop)**, flexible topic-comment structures, and honorific aspectual systems that simple dependency trees cannot cleanly normalize to language-independent representations.
3. **Non-Monotonic Belief Revision:**  
   When the user or environment contradicts an earlier premise, C4 executed simple node overwrites. It lacked a formal Truth Maintenance System (such as a Justification-Based TMS / JTMS) to track dependency trees, retract dependent inferences, and maintain global consistency.
4. **Lifelong Memory Scaling:**  
   The C4 microbenchmark was verified at small scales ($N \le 100$ concepts). Edge execution behavior under 10,000 to 100,000 long-term episodic nodes remains untested.

Phase 23-D formulates an empirical evaluation scaffold to evaluate **three explicit candidate architectures** (UMR-TPG, V-UMR, DRS-Graph) across these unresolved capability axes.

---

## 4. Epistemological Classification Ledger

In accordance with `AGENTS.md` §0, all concepts, properties, and metrics in Phase 23-D are partitioned into strict evidentiary categories:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 23-D EPISTEMOLOGICAL PARTITION                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [DEMONSTRATED BY IN-REPO BENCHMARK]                                                   │
│  • Sentence embedding collapse under role swap & polarity reversal.                    │
│  • Pure HDC (C3) and pure TPR (C5) collapse at recursion depth D ≥ 3.                  │
│  • C4 Hybrid achieves RF3 = 86.4% on edge CPU in 0.38 ms.                              │
│  • Closed-loop ODE-semantic coupling is Lyapunov stable (λ_max ≤ 0.0).                 │
│  • SDM attractor eliminates noise drift (D50 = 0.000).                                 │
│                                                                                        │
│  [SUPPORTED INFERENCE]                                                                 │
│  • A typed property graph preserves compositional structure unbounded by vector rank. │
│  • Language-independent semantic frames can normalize pro-drop differences.            │
│  • Truth maintenance dependency DAGs allow localized non-monotonic updates.           │
│                                                                                        │
│  [ENGINEERING HYPOTHESES REQUIRING BENCHMARK]                                          │
│  • UMR-TPG execution SLA ≤ 5.0 ms single-core CPU under 20W TDP.                       │
│  • 100,000-concept graph fits within ≤ 200 MB RAM budget.                              │
│  • Coreference resolution across 10-turn pro-drop discourse achieves F1 ≥ 0.85.        │
│  • Belief revision retracts invalidated downstream nodes in ≤ 2.0 ms.                  │
│                                                                                        │
│  [OPEN / UNVERIFIED SPECULATION]                                                       │
│  • Feasibility of pure edge-based zero-shot semantic parsing for Vietnamese/Japanese.  │
│  • Direct acoustic prosody-to-graph feature binding without intermediate phonetics.    │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
