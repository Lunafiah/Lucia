# Phase 23-D — Candidate Architecture Specifications

> **Document Type:** Formal Architecture Specifications & Candidate Taxonomy  
> **Status:** `[EVALUATION CANDIDATE SPECIFICATION]`  
> **Authority:** `AGENTS.md` §0, §7; Phase 23-D Evaluation Scaffold  
> **Production Boundary:** Evaluation models only. No code in `src/core/` or production runtime.

---

## 1. Candidate Architecture Overview

Phase 23-D evaluates three distinct semantic representational architectures plus two auxiliary associative baselines:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 23-D ARCHITECTURAL TAXONOMY                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [PRIMARY CANDIDATE]                                                                   │
│  UMR-TPG: Universal Meaning Representation on Typed Property Graph                     │
│  • Pure structural DAG + document-level discourse/modal links                          │
│  • Reified events, Neo-Davidsonian participant roles, cross-lingual schema invariance  │
│                                                                                        │
│  [SECONDARY CANDIDATE]                                                                 │
│  V-UMR: Vector-Augmented Universal Meaning Representation                              │
│  • UMR-TPG graph topology augmented with localized metric embeddings / hypervectors    │
│  • Dual-layer: discrete topology for logic, continuous vectors for associative recall  │
│                                                                                        │
│  [CONTROL CANDIDATE]                                                                   │
│  DRS-Graph: Discourse Representation Structure Graph                                   │
│  • Formal box-structure DRT (Kamp & Reyle) mapped to nested graph partitions           │
│  • Precise logical quantification, conditional subordination, and negation scopes      │
│                                                                                        │
│  [AUXILIARY ASSOCIATIVE BASELINES - NOT PRIMARY PERSISTENT SUBSTRATES]                 │
│  • HDC/VSA: 1024D Bipolar Hypervector Gestalt (Fast associative indexing only)        │
│  • Compressed TPR: Smolensky Tensor Product Representation (Short-term binding only)   │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Primary Candidate: UMR-TPG (Universal Meaning Representation on Typed Property Graph)

### 2.1 Theoretical Foundation
Universal Meaning Representation (UMR; Van Gysel et al., 2021) extends Abstract Meaning Representation (AMR) by adding:
1. Cross-lingual applicability (supporting typologically diverse languages including head-initial and head-final languages).
2. Explicit multi-sentence discourse-level structures (coreference, temporal relations, modal dependencies).
3. Reification of non-eventive concepts and aspectual annotations.

### 2.2 Formal Graph Schema
UMR-TPG realizes UMR as a **Typed Property Graph (TPG)** $G = (V, E, \tau_V, \tau_E, \lambda)$:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ UMR-TPG SCHEMA                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Node Types τ_V(v) ∈ {CONCEPT, EVENT, ENTITY, ATTRIBUTE, MODAL_FRAME, TIME_REF}:       │
│  ├── CONCEPT:     Unique ontological concept node (e.g. `c:TRUST_01`)                  │
│  ├── EVENT:       Reified event instance (e.g. `e1:HELP_01`)                           │
│  ├── ENTITY:      Discourse referent / participant (e.g. `x1:USER`, `x2:LUCIA`)        │
│  ├── ATTRIBUTE:   Scalar or categorical value (e.g. `attr:DEGREE_HIGH`)                │
│  ├── MODAL_FRAME: Epistemic / deontic modality box (e.g. `m1:BELIEF_MODAL`)            │
│  └── TIME_REF:    Temporal anchor / ordering node (e.g. `t1:PAST_INTERVAL`)           │
│                                                                                        │
│  Edge Types τ_E(e) ∈ {ARG0..ARG4, MOD, TIME, MODAL_SCOPE, COREFERENCE, DISCOURSE}:    │
│  ├── Thematic:    `:ARG0` (Agent), `:ARG1` (Patient), `:ARG2` (Beneficiary/Goal)       │
│  ├── Modifiers:   `:degree`, `:manner`, `:polarity` (negative = -1)                    │
│  ├── Discourse:   `:cause`, `:contrast`, `:condition`, `:temporal-before`              │
│  └── Reference:   `:same-entity`, `:subset-of`, `:zero-anaphoric-link`                │
│                                                                                        │
│  Node Properties λ(v):                                                                 │
│  ├── `id`: UUID (e.g. `8f2a1b9c`)                                                      │
│  ├── `salience`: s ∈ [0.0, 1.0]                                                        │
│  ├── `provenance`: `SessionTurnID` (e.g. `S14:T03`)                                    │
│  └── `justification_ptrs`: [List of upstream supporting node IDs]                      │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Key Operational Properties
- **Persistent Substrate:** The primary persistent memory is the explicit graph structure.
- **Traversal & Inference:** Directed graph walks, breadth-first neighborhood queries, and topological cycle checks.
- **Language Independence:** Surface lexical forms (EN, VI, JA) are detached attributes. An entity representing the user is identical regardless of whether addressed as *"you"*, *"bạn"*, or *"ユーザー"*.
- **Hypothesized Trade-Off:** Pure pointer navigation on CPU; lacks intrinsic continuous metric similarity without secondary projection.

---

## 3. Secondary Candidate: V-UMR (Vector-Augmented Universal Meaning Representation)

### 3.1 Theoretical Foundation
V-UMR maintains the structural integrity of UMR-TPG while augmenting every node and subgraph with continuous vector representations. It addresses the limitation of pure symbolic graphs by enabling direct metric distance calculations (e.g., cosine similarity or Euclidean distance) for fast approximate search in long-term memory.

### 3.2 Formal Schema & Dual-Representation
In V-UMR, each node $v \in V$ is a composite pair:

$$v = \langle \mathbf{z}_v, \mathcal{S}_v \rangle$$

where:
- $\mathcal{S}_v$ is the symbolic UMR-TPG schema containing type $\tau_V(v)$, edges $E(v)$, and logical properties.
- $\mathbf{z}_v \in \mathbb{R}^{32}$ is a local continuous metric embedding representing perceptual/contextual coordinates.
- Additionally, subgraphs and sentences generate a composite 1024D hypervector $\mathbf{h}_G \in \{-1, +1\}^{1024}$ via vector symbolic binding for global indexing.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ V-UMR DUAL NODE ARCHITECTURE                                                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  ┌───────────────────────────────┐     ┌──────────────────────────────────────────┐    │
│  │   Symbolic UMR Property Graph │     │    Continuous Vector Annotations         │    │
│  │   • Node ID: `e1:ASSIST_01`   │ <-> │    • Perceptual Centroid: z_v ∈ ℝ³²      │    │
│  │   • :ARG0 -> `x1:LUCIA`       │     │    • Covariance Radius: σ_v² ∈ ℝ³²       │    │
│  │   • :ARG1 -> `x2:USER`        │     │    • HDC Subgraph Signature: h_G ∈ ℤ₂¹⁰²⁴│    │
│  └───────────────────────────────┘     └──────────────────────────────────────────┘    │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Key Operational Properties
- **Associative Search:** Approximate nearest-neighbor queries can be executed directly in $\mathbb{R}^{32}$ or hypervector space without graph traversal.
- **Continuous Limbic Resonance:** Vector coordinates can be modulated directly by continuous ODE states ($[P, A, D]$).
- **Hypothesized Trade-Off:** Substantially higher memory footprint (~2.5× to 3.5× that of UMR-TPG); requires continuous synchronization between graph topology edits and vector representations.

---

## 4. Control Candidate: DRS-Graph (Discourse Representation Structure Graph)

### 4.1 Theoretical Foundation
Discourse Representation Theory (DRT; Kamp & Reyle, 1993) provides the canonical formal semantics baseline for multi-sentence discourse processing, scope resolution, and conditional reasoning. DRS-Graph maps classical DRS "boxes" into directed graph partitions.

### 4.2 Formal Schema
A DRS is a pair $\langle U, C \rangle$, where $U$ is a set of discourse referents and $C$ is a set of conditions:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ DRS-GRAPH SCHEMA                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  ┌── Box B1 (Main Universe: {x1, e1}) ──────────────────────────────────────────────┐  │
│  │  x1: USER(x1)                                                                    │  │
│  │  e1: TIRED(e1, x1)                                                               │  │
│  │                                                                                  │  │
│  │  ┌── Negation Subordinate Box ¬ B2 (Universe: {e2}) ──────────────────────────┐  │  │
│  │  │  e2: COMPLETED(e2, TASK)                                                  │  │  │
│  │  └───────────────────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

In the graph representation:
- Box partitions are represented as container nodes connected by scoping edges (`:scope`, `:presupposition`, `:subordinate-negation`).
- Discourse referents are vertices in the box's local subgraph.

### 4.3 Key Operational Properties
- **Logical Scoping Rigor:** Absolute precision for negation scopes, universal quantification, and counterfactuals.
- **Truth-Conditional Semantics:** Clean integration with formal automated theorem provers.
- **Hypothesized Trade-Off:** High structural rigidity; complex box splitting when handling zero-anaphora in casual dialogue; lacks natural continuous degradation.

---

## 5. Auxiliary Associative Baselines (Non-Primary Substrates)

To maintain continuity with Phase 22-SC and Phase 23-C, two vector architectures are included as **auxiliary associative baselines**:

1. **HDC/VSA (Hyperdimensional Computing / Vector Symbolic Architectures):**
   - 1024D bipolar vectors with Multiply-Add-Permute (MAP) algebra.
   - Evaluated as an auxiliary index for UMR-TPG and V-UMR.
   - *Confirmed Negative Finding:* Cannot serve as primary persistent substrate due to superposition noise collapse ($RF_4 = 15.2\%$).
2. **Compressed TPR (Tensor Product Representation):**
   - Smolensky outer-product unbinding on small tensor manifolds ($16 \times 16$).
   - Evaluated strictly as a short-term working-memory role-filler binder.

---

## 6. Candidate Comparison Matrix

| Dimensional Axis | UMR-TPG (Primary) | V-UMR (Secondary) | DRS-Graph (Control) | HDC/TPR (Auxiliary) |
|---|---|---|---|---|
| **Representation Format** | Typed Property Graph | Property Graph + Dense Vectors | Nested Box Partition Graph | High-D Vector / Tensor |
| **Primary Persistent Substrate** | Graph Topology | Graph Topology + Embeddings | Graph Box Partition | Vector Superposition |
| **Recursion Mechanism** | Edge Pointers (Unbounded) | Edge Pointers (Unbounded) | Box Nesting (Unbounded) | Vector Product (Bounded $D \le 2$) |
| **Continuous Metric Search** | None (Requires projection) | Native ($\mathbb{R}^{32}$ distance) | None (Requires theorem prover) | Native (Cosine / Hamming) |
| **Cross-Lingual Normalization** | Language-neutral roles/events | Language-neutral roles + vectors | Formal discourse referents | Multilingual token vector |
| **Non-Monotonic Revision** | Node & edge retraction DAG | Dual graph-vector retraction | Box condition retraction | Vector subtraction (lossy) |
| **Est. Memory / Fact** | $\approx 250 - 350\text{ bytes}$ | $\approx 650 - 900\text{ bytes}$ | $\approx 400 - 550\text{ bytes}$ | $128 - 1024\text{ bytes}$ |
| **Status in Phase 23-D** | **Primary Evaluation Candidate** | **Secondary Evaluation Candidate** | **Control Baseline** | **Auxiliary Baseline Only** |
