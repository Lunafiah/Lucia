# Phase 23-D — Final Scientific Synthesis & Candidate Disposition

> **Milestone:** Phase 23-D — Semantic Substrate Evaluation  
> **Status:** `[RESEARCH COMPLETED / ARCHITECTURAL SYNTHESIS]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `candidate_spec.md`; `metrics.md`  
> **Production Boundary:** Evaluation and documentation only. Zero modifications to `src/core/**` or runtime behavior.  
> **Genesis Gate Invariant:** Preserved bit-exact (`data/profile.json` $\to$ `{"is_onboarded": false}`).

---

## 1. Executive Summary & Evaluation Mission

Phase 23-D evaluated candidate architectures for Lucia's language-independent semantic layer across six pre-registered experimental tracks:
- **EXP-01:** Compositionality & Recursion (Depth scaling $D \in [1, 4]$)
- **EXP-02:** Cross-Lingual Semantic Convergence (English, Japanese, Vietnamese parallel frames)
- **EXP-03:** Reference Resolution & Zero-Anaphora (Overt pronouns, pro-drop, kinship deixis)
- **EXP-04:** Belief Revision & Contradiction (Non-monotonic JTMS dependency retraction, bitemporal auditing)
- **EXP-05:** Scaling & Hardware Feasibility (Single-core CPU scaling $1\text{k} \to 100\text{k}$ facts)
- **EXP-06:** Multimodal Grounding & Token-Free Embodiment (Limbic ODE and eGeMAPS prosody coupling)

The evaluation investigated three candidate substrates:
1. **UMR-TPG (Primary):** Universal Meaning Representation with Temporal-Predicate Graph.
2. **V-UMR (Secondary):** Vectorized UMR with metric concept coordinates and hypervector bindings.
3. **DRS-Graph (Control):** Discourse Representation Theory box-condition universe.
*(Additionally, HDC-Pure dense-vector superposition was evaluated as a baseline in EXP-01).*

---

## 2. Cross-Experiment Evidence Matrix

The following matrix consolidates empirical measurements across all six Phase 23-D experiments. Every entry reflects verified test outputs from the isolated evaluation testbed:

| Capability | EXP | UMR-TPG | V-UMR | DRS-Graph | Evidence Boundary |
|---|---|---|---|---|---|
| **Compositionality** | EXP-01 | **PASS** (100% role-binding at $D \le 4$) | **PASS** (100% role-binding at $D \le 4$) | **PASS** (100% box nesting at $D \le 4$) | Evaluated on structured proposition trees ($D=1..4$); HDC-pure collapsed ($\text{SPRR}=0.0, \text{BER}=1.0$) |
| **Recursion** | EXP-01 | **PASS** ($RF_D = 1.000$ at $D \le 4$) | **PASS** ($RF_D = 1.000$ at $D \le 4$) | **PASS** ($RF_D = 1.000$ at $D \le 4$) | Syntactic/semantic tree depth scaling without representation degradation |
| **Cross-Lingual Representation** | EXP-02 | **PASS** (Oracle $\text{SQI} = 1.000$) | **PASS** (Oracle $\text{SQI} = 1.000$) | **PASS** (Oracle $\text{SQI} = 1.000$) | Parallel semantic frames (EN/JA/VI); topology varies while functional meaning is equivalent |
| **Surface Transduction** | EXP-02 | **Rule-Based $\text{SQI} = 0.887$** | **Rule-Based $\text{SQI} = 0.887$** | **Rule-Based $\text{SQI} = 0.950$** | Rule-based transducers exhibit inherent cross-lingual lexical/classifier limitations; open-domain NLU unverified |
| **Coreference** | EXP-03 | **PASS** ($\text{CEAF}_e = 1.000, \text{EPR} = 1.000$) | **PASS** ($\text{CEAF}_e = 1.000, \text{EPR} = 1.000$) | **PASS** ($\text{CEAF}_e = 1.000, \text{EPR} = 1.000$) | Discourse entity ledger maintains identity across 5-sentence chains without chain splitting |
| **Zero-Anaphora** | EXP-03 | **PASS** ($\text{URP} = 1.000, \text{CRA} = 1.000$) | **PASS** ($\text{URP} = 1.000, \text{CRA} = 1.000$) | **PASS** ($\text{URP} = 1.000, \text{CRA} = 1.000$) | Subject/object pro-drop resolved; ungrounded zero-anaphora safely preserved as `UNKNOWN_ENTITY` |
| **Belief Revision** | EXP-04 | **PASS** ($\text{RC} = 1.0, \text{DPA} = 1.0, \text{CRR} = 0.0$) | **PASS** ($\text{RC} = 1.0, \text{DPA} = 1.0, \text{CRR} = 0.0$) | **PASS** ($\text{RC} = 1.0, \text{DPA} = 1.0, \text{CRR} = 0.0$) | Non-monotonic JTMS dependency retraction; multi-hop propagation ($A \to B \to C$); zero collateral retraction |
| **Temporal Contradiction Handling** | EXP-04 | **PASS** ($\text{CDR} = 1.000, \text{HRR} = 1.000$) | **PASS** ($\text{CDR} = 1.000, \text{HRR} = 1.000$) | **PASS** ($\text{CDR} = 1.000, \text{HRR} = 1.000$) | Bitemporal interval overlap distinguishes state transitions from conflicts; full audit ledger preserved |
| **Scaling (1k $\to$ 100k)** | EXP-05 | **PASS** ($2.0\text{s}$ build, $0.007\text{ms}$ lookup p95) | **PASS** ($16.1\text{s}$ build, $0.019\text{ms}$ lookup p95) | **PASS** ($2.5\text{s}$ build, $0.005\text{ms}$ lookup p95) | Single-core CPU scaling across 1k, 5k, 10k, 25k, 50k, 100k facts; 1-hop lookup p95 $\le 0.02\text{ms}$ |
| **Memory Envelope** | EXP-05 | **PASS** ($189.2\text{ MB}$ Working Set at 100k $\le 200\text{ MB}$) | **FAIL** ($660.3\text{ MB}$ Working Set at 100k $> 350\text{ MB}$) | **PASS** ($210.3\text{ MB}$ Working Set at 100k $\le 250\text{ MB}$) | Dual representation ($32\text{D}$ float + $1024\text{D}$ hypervectors) causes severe Working Set memory bloat under Python heap |
| **Multimodal Grounding** | EXP-06 | **PASS** ($\text{CPA} = 1.000, \text{CMC} = 1.000$) | **FAIL** ($\text{CPA} = 0.833 < 0.90$ gate) | **PASS** ($\text{CPA} = 1.000, \text{CMC} = 1.000$) | Continuous limbic ODE $[P, A, D]$ and eGeMAPS acoustic prosody mapped without tokens; V-UMR over-attributes on partial acoustic |
| **Token-Free Embodiment** | EXP-06 | **PASS** ($100\%$ token-free, $r = 1.000$) | **PASS** ($100\%$ token-free, $r = 1.000$) | **PASS** ($100\%$ token-free, $r = 1.000$) | Physical embodiment parameters (blendshape `Smile_W`, pitch shift, pacing delay) driven directly without LLM |
| **Physical 20W Power** | EXP-05/06 | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | Hardware package power meter absent in host test environment; software SLA gates evaluated independently |
| **Open-Domain Natural Language** | EXP-02/03/04 | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | Evaluated strictly on controlled deterministic structured representations; noisy unconstrained text unverified |

---

## 3. Explicit Falsification Ledger

The following hypotheses were experimentally tested and **falsified** under the pre-registered evaluation criteria:

### 1. V-UMR Memory Footprint Hypothesis ($H_2$ in EXP-05)
- **Pre-Registered Gate:** Total Resident Set Size / Working Set at $N=100\text{k}$ facts $\le 350.0\text{ MB}$.
- **Empirical Measurement:** Post-build Working Set reached **$660.3\text{ MB}$** ($167.2\text{ MB}$ Python heap tracing).
- **Verdict:** **`FAIL` (Falsified)**.
- **Causal Mechanism:** Storing 100,000 distinct 32-float tuples and 128-byte hypervector objects alongside symbolic graph adjacency lists induces severe memory fragmentation in standard Python object allocation. Without custom contiguous C-level memory arenas, dual-layer vector augmentation cannot satisfy the edge memory envelope at 100k facts.

### 2. V-UMR Continuous Grounding Accuracy Hypothesis ($H_2$ in EXP-06)
- **Pre-Registered Gate:** Centroid Placement Accuracy ($\text{CPA}$) $\ge 0.90$.
- **Empirical Measurement:** Achieved **$\text{CPA} = 0.833$** ($10 / 12$ samples).
- **Verdict:** **`FAIL` (Falsified)**.
- **Causal Mechanism:** When only acoustic prosody was observed without valence indicators (e.g. `SM_AC_01`), unconstrained Euclidean centroid distance in $\mathbb{R}^{32}$ projected identically onto multimodal `STATE_ALARM` and unimodal `PROSODY_AGITATED`. Without symbolic guardrails, continuous metric proximity produced false multimodal over-attribution.

### 3. HDC-Pure Primary-Substrate Hypothesis (EXP-01)
- **Pre-Registered Gate:** Subgraph Pattern Retrieval Precision ($\text{SPRR}$) $\ge 0.80$, Binding Error Rate ($\text{BER}$) $\le 0.10$ across recursion depths $D \in [1, 4]$.
- **Empirical Measurement:** **$\text{SPRR} = 0.000$** across $D=1 \dots 4$, **$\text{BER} = 1.000$**.
- **Verdict:** **`FAIL` (Falsified)**.
- **Causal Mechanism:** Dense hypervector superposition suffers crosstalk accumulation under dense-vector superposition and catastrophic clean-up memory degradation during deep unbinding. Pure vector superposition cannot serve as the primary persistent compositional semantic substrate.

---

## 4. Explicit Unverified Ledger

To preserve strict scientific boundaries, the following capabilities are explicitly classified as **`UNVERIFIED`** and must not be claimed:

```text
EVIDENCE CLASSIFICATION SCHEMA:
[TESTED AND PASSED UNDER CONTROLLED CONDITIONS] -> Verified on deterministic fixtures
[TESTED AND FAILED]                             -> Empirically rejected (see Falsification Ledger)
[UNVERIFIED]                                    -> Untested, out-of-scope, or tool-limited
```

1. **End-to-End Parsing of Unconstrained Vietnamese & Japanese:**  
   EXP-02 established semantic equivalence under oracle ingestion ($\text{SQI} = 1.000$) and measured rule-based parser limitations ($\text{SQI} = 0.887$). Real-world parsing of ungrammatical, noisy, or dialectal Japanese/Vietnamese conversational input is **`UNVERIFIED`**.
2. **Open-Domain Natural Language Semantic Transduction:**  
   The semantic substrate evaluation tested representation and internal reasoning. Converting arbitrary conversational text to valid semantic graphs in real time without external large models remains **`UNVERIFIED`**.
3. **Large-Scale Neural Concept Alignment:**  
   Cross-lingual concept identity was evaluated on a controlled 10-phenomenon parallel corpus. Open-domain multilingual ontology alignment across tens of thousands of concepts is **`UNVERIFIED`**.
4. **Real-World Noisy Microphone Distributions:**  
   EXP-06 utilized deterministic synthetic acoustic prosody vectors and limbic ODE trajectories. Live microphone stream parsing subject to background noise and acoustic variability is **`UNVERIFIED`**.
5. **Physical 20-Watt Package Power Consumption:**  
   While single-core CPU execution and zero GPU VRAM impact ($0.0\text{ MB}$) were verified, direct CPU package wattage was not physically monitored and remains **`UNVERIFIED`**.
6. **Production Runtime Integration:**  
   All evaluation code was isolated in `tests/evaluation/`. Zero components have been promoted into `src/core/**`. Production latency, memory safety, and thread safety under live conversational load remain **`UNVERIFIED`**.
7. **Long-Horizon Real-User Conversational Behavior:**  
   Continuous autobiographical interaction across months of live user interaction remains **`UNVERIFIED`**.

---

## 5. Candidate Disposition After Phase 23-D

The empirical evidence establishes the following candidate-specific dispositions:

### 1. UMR-TPG (Primary Candidate)
- **Empirical Status:** Passed all evaluated gates across EXP-01, EXP-02 (Representation), EXP-03, EXP-04, EXP-05, and EXP-06.
- **Strengths Demonstrated:**
  - Strict linear memory scaling: $43.0\text{ MB}$ heap / $189.2\text{ MB}$ Working Set at 100,000 facts (satisfies $\le 200\text{ MB}$ edge envelope).
  - Sub-millisecond 1-hop role lookups ($p95 = 0.007\text{ ms}$) and sub-millisecond local belief revision ($p95 = 0.033\text{ ms}$).
  - Complete multi-hop dependency retraction ($\text{DPA} = 1.000$) with zero collateral damage ($\text{CRR} = 0.000$).
  - Effective token-free embodiment coupling ($r = 1.000$) and zero decision flapping under deadband hysteresis ($\text{DFR} = 0.0\%$).
- **Disposition:** **Retained as the leading architectural candidate** for Lucia's language-independent semantic substrate. Requires downstream investigation into surface transduction (parsing) before any production integration.

### 2. DRS-Graph (Control Candidate)
- **Empirical Status:** Passed all capability and SLA gates across EXP-01 through EXP-06.
- **Strengths Demonstrated:**
  - Formal box-condition accessibility cleanly represents scope, negation, and modal attitudes.
  - Satisfied the 100k memory gate ($210.3\text{ MB}$ Working Set $\le 250\text{ MB}$) and latency gate ($p95 = 0.005\text{ ms}$).
- **Observed Trade-offs:**
  - Box partitioning introduces structural indirection, resulting in slightly higher memory footprint per fact ($534.7\text{ B/fact}$ vs $450.8\text{ B/fact}$ in UMR-TPG).
- **Disposition:** **Validated as a functionally sound formal control**. While viable, its box-nesting structural indirection offers no operational performance advantage over flat relational graphs (UMR-TPG) on edge CPU.

### 3. V-UMR (Secondary Candidate)
- **Empirical Status:** Passed controlled logical capability tests (EXP-01, EXP-02, EXP-03, EXP-04), but **FAILED** two critical evaluation gates:
  - Failed EXP-05 Memory Envelope ($660.3\text{ MB} > 350.0\text{ MB}$ gate at 100k facts).
  - Failed EXP-06 Multimodal Grounding Accuracy ($\text{CPA} = 0.833 < 0.90$ gate).
- **Disposition:** **Disqualified as a primary persistent substrate candidate**. Continuous vector embeddings must NOT serve as the primary source of truth or persistent state. Vector representations may be utilized strictly as transient, unpersisted auxiliary indices for approximate similarity search where memory allows.

---

## 6. Architectural Decision Boundary & What Phase 23-D Authorizes

### What Phase 23-D Authorizes:
1. **Candidate Narrowing:** Authorizes focusing future semantic research on **explicit graph-based architectures** (UMR-TPG as primary, DRS-Graph as formal reference), while permanently rejecting dense-vector superposition (HDC-Pure) and unconstrained dual-layer persistent vectors (V-UMR) as primary substrates.
2. **Separation of Concerns:** Authorizes treating semantic representation as an internal language-independent graph problem, while treating surface transduction (text $\to$ graph) as a separate peripheral extraction engineering track.
3. **Research Specification Authoring:** Authorizes drafting future research specifications (e.g. surface transduction, concept formation parsing pipelines) grounded in UMR-TPG representations.

### What Phase 23-D Does NOT Authorize:
1. **NO Production Mutation:** Does NOT authorize modifying `src/core/**`, `electron/**`, `config/**`, or `data/**`.
2. **NO Promotion to Runtime:** The evaluation engines developed in `tests/evaluation/` are disposable evaluation harnesses and must not be imported into the active cognitive pipeline.
3. **NO Activation:** Genesis Onboarding remains a locked future gate (`data/profile.json` $\to$ `{"is_onboarded": false}`).

---

## 7. Phase 23-D Conclusion

1. **Capabilities Demonstrated:**  
   Controlled evaluations provide empirical evidence that graph-based semantic substrates can:
   - represent nested propositions up to depth $D=4$ without role confusion;
   - preserve functionally equivalent meaning across English, Japanese, and Vietnamese representations;
   - track persistent discourse referents and conservative zero-anaphora without hallucinating antecedents;
   - execute non-monotonic belief revisions and multi-hop dependency retractions in $\le 0.036\text{ ms}$;
   - scale to 100,000 relational facts within a $189.2\text{ MB}$ Working Set on a single CPU core;
   - couple continuous limbic ODE states to physical avatar embodiment without requiring language tokens.

2. **Hypotheses Falsified:**  
   - The hypothesis that dense-vector superposition can maintain compositional recursion was falsified ($H_0$ in EXP-01).
   - The hypothesis that dual-representation stores (V-UMR) can remain within a 350 MB Working Set at 100k facts was falsified ($H_2$ in EXP-05).
   - The hypothesis that unconstrained metric vector distance achieves $\ge 0.90$ grounding accuracy without symbolic guardrails was falsified ($H_2$ in EXP-06).

3. **Unverified Boundaries:**  
   Open-domain natural language parsing, noisy microphone signal processing, and physical 20-Watt power package verification remain unverified.

4. **Supported Architectural Baseline:**  
   The evidence supports **UMR-TPG** as the primary semantic substrate candidate. It provides the required expressive richness, deterministic non-monotonic belief revision, and sub-millisecond edge performance within the target memory budget.

5. **Prerequisites for Future Production Promotion:**  
   Before any semantic substrate can be proposed for production promotion:
   - A deterministic or edge-compatible surface transducer (parser) from natural language to UMR-TPG must be designed and evaluated.
   - The concurrency and locking invariants of `AGENTS.md` §9 must be formally modeled and proven for multi-threaded access.
   - A formal Architectural Decision Record (ADR) and Production Realization Design must be authored and approved.
