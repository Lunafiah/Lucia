# P23 Semantic Formation Microbenchmark v0.2 — Scientifically Audited

> **Preregistered Evaluation Specification & Benchmark Protocol for Phase 23 (Revision 2)**  
> **Status:** `[RESEARCH BENCHMARK SPECIFICATION / REVISED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md`  
> **Supersedes:** `SEMANTIC_FORMATION_MICROBENCHMARK_v0.1.md` (v0.1 invalidated per audit findings)  
> **Evaluation Harness Path:** `tests/evaluation/phase23/`  
> **Artifacts Destination:** `evaluation_artifacts/phase23/`  
> **Production Safety Invariant:** 100% Isolated. Zero modifications to `src/core/**`, `electron/**`, runtime lifecycle, or `data/profile.json` (`{"is_onboarded": false}`).

---

## 1. Audit Invalidation Notice & Rationale for v0.2

The scientific validity audit of Microbenchmark v0.1 identified six critical experimental and epistemological defects:
1. **Invalidated G-MB-5 ($RF_3$):** Proposition retrieval fidelity was hardcoded to static literals (`0.98`, `0.88`, `0.72`) rather than empirically measured via representation unbinding.
2. **Invalidated G-MB-2 (ISAA):** Formation used a direct string-copy constructor from intention to node labels, making alignment evaluation circular.
3. **Invalidated G-MB-4 ($D_{50}$):** Drift was artificially bounded by hardcoding an anchor restoration vector ($0.02 \times \mathbf{v}_{\text{anchor}}$) into each turn's drift step.
4. **Invalidated G-MB-8 ($\lambda_{\max}$):** The Lyapunov exponent was measured on an uncoupled synthetic decaying generator rather than the closed-loop coupled limbic-semantic system.
5. **Invalidated G-MB-9 / G-MB-10 (RUF / Drift):** Updates modified metadata versions without touching fact labels, rendering 100% retention trivial.
6. **Invalidated G-MB-11 (TPA):** Concept grounding evaluated handcrafted keywords that mirrored the internal ontology dictionary, failing to test out-of-distribution (OOD) generalization.
7. **Invalidated Baseline Claim:** C4 was evaluated in isolation without head-to-head empirical comparison against C1, C2, C3, and C5 on identical test inputs.

**Microbenchmark v0.2 completely rebuilds all six tracks to eliminate circularity, hardcoded readouts, and oracle leakage.**

---

## 2. Benchmark Architecture & Candidate Matrix

### 2.1 Evaluated Candidate Representations (Head-to-Head)

All representations are benchmarked on the exact same seed-generated test inputs:
- **C1 (Pure Structured Frame):** Flat slot-value JSON frame.
- **C2 (Typed Relational Graph):** Labeled directed property graph ($V, E$).
- **C3 (Dense HDC Hypervector):** $D=1024$ bipolar hypervector superposition (historical baseline).
- **C4 (Hybrid Graph + HDC Gestalt):** Inherited Phase 22 baseline (Typed graph bound to global HDC hypervector).
- **C5 (Tensor Product Representation):** Smolensky outer-product tensor binding $\mathbf{T} = \sum_i \mathbf{r}_i \otimes \mathbf{f}_i$.

---

## 3. Revised Preregistered Evaluation Tracks (U1–U6)

### Track 1 (U1): Causal Cognitive-to-Intention Semantic Formation
- **Input:** Seed-generated continuous cognitive state $\mathbf{x}_{\text{cog}} = [P, A, D, \text{energy}, \text{trust}, H_{\text{epistemic}}]$.
- **Causal Mechanism:**
  - High arousal ($A > 0.2$) + high entropy ($H > 0.5$) $\to$ `CLARIFY_QUERY`.
  - Negative valence ($P < -0.15$) + low trust $\to$ `ASSERT_BOUNDARY` with defensive modifiers.
  - High valence + high trust $\to$ `COLLABORATIVE_PROPOSAL`.
  - Somatic energy dynamically bounds graph cardinality ($N \le 3$ under low energy; $N \ge 5$ under high energy).
- **Metrics:**
  - **Causal Formation Sensitivity (CFS):** Statistical divergence between semantic graphs generated under contrasting cognitive regimes ($\ge 0.80$).
  - **Structural Graph Validity Rate (SGVR):** Formal schema and DAG validation ($\ge 95.0\%$).
  - **Token Independence Metric (TIM):** Exactly 0 LLM tokens ($1.0$).

### Track 2 (U2): Associative Referential Grounding under Distractor Noise
- **Mechanism:** Entities possess 64-dimensional bipolar semantic vectors. Memory pool contains $K=20$ distractor traces. Incoming observations are corrupted by Gaussian noise ($\sigma = 0.25$).
- **Retrieval:** Nearest-neighbor cosine matching over SDM memory space without dictionary lookup.
- **Drift:** Free drift under 50-turn random perturbation without artificial anchor forcing. Auto-associative SDM projection acts as the sole memory anchor.
- **Metrics:**
  - **Referential Grounding Precision (RGP):** Fraction of noisy queries correctly resolved to the target anchor ($\ge 90.0\%$).
  - **50-Turn Drift ($D_{50}$):** Real Euclidean displacement of entity coordinate representation ($\le 0.050$).

### Track 3 (U3): Empirical Recursion & Negation Decoding for C1–C5
- **Mechanism:** True recursive propositions $P_0(\text{AGENT}, P_1(\dots))$ generated for depths $D=1, 2, 3, 4$.
- **Decoding:**
  - In C3: Recursive unbinding $\hat{\mathbf{v}} = \text{bind}(\mathbf{r}_{\text{role}}, \mathbf{v}_{\text{nested}})$ evaluated by cosine similarity against ground-truth constituent codebooks.
  - In C5: Tensor contraction $\hat{\mathbf{f}} = \mathbf{r}^T \mathbf{T}$ matched against codebook.
  - In C4: Combined graph path verification with gestalt vector unbinding similarity.
- **Metrics:**
  - **$RF_D$:** Empirical decoding accuracy derived from similarity margin $\ge 0.60$ for depth $D$.
  - **Negation Polarity Accuracy (NPA):** Empirical separation margin between affirmative and negated representations.

### Track 4 (U4): Closed-Loop Continuous-to-Semantic Feedback Coupling
- **Mechanism:** Closed-loop dynamical system where continuous MT-LNN ODE ($d\mathbf{x}/dt = -\gamma(\mathbf{x} - \mathbf{x}_{\text{Philia}}) + \mathbf{W}_f \mathbf{s}_{\text{sem}}$) couples bidirectionally with semantic node salience and urgency.
- **Metrics:**
  - **Decision Flapping Rate (DFR):** Measured across 100 closed-loop integration steps with deadband hysteresis ($\le 5.0\%$).
  - **Closed-Loop Lyapunov Exponent ($\lambda_{\max}$):** Empirically computed from the perturbed trajectory; must satisfy $\le 0.000$ (asymptotically stable).

### Track 5 (U5): Genuine Multi-Turn Semantic Revisions
- **Mechanism:** 10-turn sequence of genuine operations: additions, attribute mutations, relationship rewiring, belief contradiction reversals, and entity mergers.
- **Metrics:**
  - **Fact Retention After Delta (RUF):** Exact preservation of unaffected facts ($\ge 98.0\%$).
  - **Historical Semantic Drift ($\Delta_{\text{drift}}$):** Real cosine displacement on unaffected historical facts ($\le 0.050$).

### Track 6 (U6): Distributional Contextual OOD Concept Grounding
- **Mechanism:** Novel concepts from held-out domains (medical, aerospace, musicology) represented by 32-dimensional contextual embeddings.
- **Classification:** Nearest-centroid matching against taxonomic categories without keyword lookups or LLM queries.
- **Metrics:**
  - **Taxonomic Placement Accuracy (TPA):** Accuracy on held-out concept embeddings ($\ge 80.0\%$).
  - **Edge Execution SLA:** CPU latency $\le 5.0\text{ ms}$, VRAM $== 0.0\text{ MB}$.

---

## 4. Master Acceptance Gates (12/12)

| Gate ID | Track | Focus Metric | Requirement | Falsification |
|---|---|---|---|---|
| **G-MB-1** | Track 1 (U1) | Structural Graph Validity Rate (SGVR) | $\ge 95.0\%$ | $< 80.0\%$ |
| **G-MB-2** | Track 1 (U1) | Causal Formation Sensitivity (CFS) | $\ge 80.0\%$ | $< 60.0\%$ |
| **G-MB-3** | Track 2 (U2) | Referential Grounding Precision (RGP) | $\ge 90.0\%$ | $< 80.0\%$ |
| **G-MB-4** | Track 2 (U2) | 50-Turn Longitudinal Drift ($D_{50}$) | $\le 0.0500$ | $> 0.1500$ |
| **G-MB-5** | Track 3 (U3) | Empirical Proposition Fidelity @ $D=3$ ($RF_3$) | $\ge 85.0\%$ | $< 70.0\%$ |
| **G-MB-6** | Track 3 (U3) | Negation Polarity Accuracy ($NPA$) | $\ge 95.0\%$ | $< 85.0\%$ |
| **G-MB-7** | Track 4 (U4) | Closed-Loop Decision Flapping ($DFR$) | $\le 5.0\%$ | $> 10.0\%$ |
| **G-MB-8** | Track 4 (U4) | Closed-Loop Lyapunov Exponent ($\lambda_{\max}$) | $\le 0.0000$ | $> 0.0000$ |
| **G-MB-9** | Track 5 (U5) | Fact Retention After Delta ($RUF$) | $\ge 98.0\%$ | $< 90.0\%$ |
| **G-MB-10**| Track 5 (U5) | Historical Semantic Drift ($\Delta_{\text{drift}}$) | $\le 0.0500$ | $> 0.1500$ |
| **G-MB-11**| Track 6 (U6) | OOD Taxonomic Placement Accuracy ($TPA$) | $\ge 80.0\%$ | $< 65.0\%$ |
| **G-MB-12**| Hardware | CPU Latency P50 / GPU VRAM Allocation | $\le 5.0\text{ ms}$ / $0.0\text{ MB}$ | $> 30.0\text{ ms}$ / $> 0.0\text{ MB}$ |
