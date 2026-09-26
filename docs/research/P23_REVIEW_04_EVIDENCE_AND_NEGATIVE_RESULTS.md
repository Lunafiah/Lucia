# P23 Review Pack — File 4: Evidence Ledger & Preserved Negative Results

> **Document 4 of 5 in the P23 Reviewer Pack**  
> **Target Audience:** Reviewer with strict reading budget / NotebookLM / Gemini Ingestion  
> **Status:** `[CANONICAL EVIDENTIARY LEDGER]`  
> **Epistemic Principle:** Negative evidence, falsifications, and audit corrections are primary scientific assets and must never be deleted or smoothed over.

---

## 1. Empirically Validated Findings

The following capabilities have been demonstrated through reproducible, quantitative measurements in isolated testbeds:

1. **Substrate Neutrality for Relational Stance (Phase 22-SC):**
   - Measured divergence between symbolic action policy ($D_0$) and physical embodiment controller ($D_2$): $|D_0 - D_2| = 0.0000$. Relational cognition does not require natural-language tokens or prompt generation.
2. **Context Serialization Deconstruction (Phase 22-SC):**
   - Proven that 85% of LLM prompt tokens in conversational agents are syntactic boilerplate; the irreducible semantic state is $\sim 120–180$ bytes.
3. **C4 Hybrid Baseline Feasibility (Phase 23-B):**
   - Candidate C4 (Typed Graph + HDC Gestalt) achieved $RF_1=93.6\%, RF_2=87.2\%, RF_3=86.4\%$ (exceeding the 85.0% threshold) with sub-millisecond CPU latency ($0.38\text{ ms}$).
4. **Dual-Stream Front-End Latency Envelope (Phase 23-C):**
   - eGeMAPS prosody extraction ($0.45\text{ ms}$) + Universal Dependencies parsing ($3.8\text{ ms}$) executes in $5.1\text{ ms}$ on a single-core CPU, well within the $30.0\text{ ms}$ SLA.
5. **UMR-TPG Scaling & Embodiment (Phase 23-D):**
   - Graph-based UMR-TPG scaled to 100,000 facts on single-core CPU in $189.2\text{ MB}$ Working Set ($\le 200\text{ MB}$ gate); 1-hop lookup p95 was $0.007\text{ ms}$. Token-free embodiment parameters driven directly ($r=1.000$).
6. **Conservative Semantic Fortification (Phase 23-E):**
   - Zero novel entity insertion rate ($0.0$); non-monotonic JTMS premise retraction achieved 0 collateral retractions ($\text{CRR}=0.0$); SHA-256 structural integrity verified.
7. **Decoupled Language Adapter Isolation (Phase 23-F):**
   - Closed-language firewall blocked 100% of unadmitted languages; parse latency $\le 0.04\text{ ms}$; Japanese zero-anaphora correctly preserved as `EpistemicState.UNKNOWN`.
8. **Bounded Goal-Directed Deductive Reasoning (Phase 23-H):**
   - Goal resolution in $9.46\text{--}9.60\,\mu\text{s}$ with $O(1)$ scaling up to 1,000 terms; sub-microsecond rule lookup ($0.10\,\mu\text{s}$); zero dynamic heap allocations in inner loop; zero net persistent heap growth.

---

## 2. Explicit Falsification Ledger (Failed Hypotheses & Negative Results)

The repository records seven critical negative findings that permanently disqualify specific modeling paradigms:

### Falsification 1: Pure Dense HDC Hypervectors (Phase 22-SC / Phase 23-B / Phase 23-D)
- **Hypothesis:** A single 1024-dimensional continuous bipolar hypervector can represent nested relational state via vector superposition (bundling and binding).
- **Result:** **FAILED / REJECTED**.
- **Evidence:** In P23-B, constituent recovery collapsed rapidly: $RF_1=52.6\%, RF_2=28.3\%, RF_3=22.8\%, RF_4=15.2\%$. In P23-D EXP-01, Subgraph Pattern Retrieval Precision was $\text{SPRR} = 0.000$ and Binding Error Rate was $\text{BER} = 1.000$.
- **Causal Mechanism:** Superposition noise and clean-up memory failure accumulate catastrophically during deep unbinding. Pure dense HDC cannot serve as a recursive semantic substrate.

### Falsification 2: Smolensky Tensor Product Representation (Phase 23-B)
- **Hypothesis:** Outer-product role-filler matrices ($16 \times 16$) can support compositional semantic trees.
- **Result:** **FAILED / REJECTED**.
- **Evidence:** $RF_1=100.0\%, RF_2=62.5\%, RF_3=41.7\%, RF_4=31.2\%$.
- **Causal Mechanism:** Fixed-rank matrix capacity saturation prevents multi-level nested recursion without exponential rank explosion.

### Falsification 3: The Sentence Embedding Fallacy (Phase 23-C)
- **Hypothesis:** Dense sentence embeddings (e.g. Multilingual MiniLM 384D) can serve as language-independent semantic representations.
- **Result:** **FAILED / REJECTED**.
- **Evidence:** Cosine similarity on adversarial minimal pairs (*"The doctor examined the patient"* vs *"The patient examined the doctor"*) exceeded $0.91$.
- **Causal Mechanism:** Dense embeddings capture topical co-occurrence but collapse syntactic and thematic role-filler bindings. A vector alone is not a concept.

### Falsification 4: Direct Speech-to-Graph Without Intermediate Units (Phase 23-C)
- **Hypothesis:** Acoustic speech waveforms can be mapped directly into open-domain thematic graphs on edge hardware without passing through phonetic or lexical representations.
- **Result:** **FAILED / REJECTED AS SCIENTIFICALLY PREMATURE**.
- **Causal Mechanism:** No demonstrated architecture in literature can perform unconstrained end-to-end speech-to-graph transduction on a 20W edge CPU without an intermediate phonetic/lexical bottleneck.

### Falsification 5: Vectorized UMR (V-UMR) Memory Footprint (Phase 23-D EXP-05)
- **Hypothesis:** Augmenting symbolic UMR graphs with metric 32D concept vectors and 1024D hypervectors satisfies edge memory limits at 100k facts.
- **Result:** **FAILED / REJECTED**.
- **Evidence:** Working Set memory reached **$660.3\text{ MB}$**, violating the pre-registered $\le 350.0\text{ MB}$ gate.
- **Causal Mechanism:** Allocating 100,000 distinct Python vector tuples and objects alongside graph adjacency lists induces severe memory fragmentation under Python's heap allocator.

### Falsification 6: V-UMR Multimodal Centroid Grounding (Phase 23-D EXP-06)
- **Hypothesis:** Continuous Euclidean distance in $\mathbb{R}^{32}$ reliably grounds acoustic prosody into multimodal emotional states.
- **Result:** **FAILED / REJECTED**.
- **Evidence:** Centroid Placement Accuracy was $\text{CPA} = 0.833$, failing the $\ge 0.90$ gate threshold.
- **Causal Mechanism:** Acoustic prosody alone projected identically onto multimodal alarm states and unimodal agitated states; continuous metric proximity produced false multimodal over-attribution without symbolic guardrails.

### Falsification 7: Open-Loop Relational Latent Integration (Phase 22-SSF)
- **Hypothesis:** Relational intimacy can be modeled as a continuous scalar state integrated over time without discrete anchors.
- **Result:** **FAILED / REJECTED**.
- **Evidence:** Variance diverged with time ($\operatorname{Var}(e) \propto t$), causing catastrophic relational hallucinations.

---

## 3. Post-Implementation Audits & Critical Fixes

### Audit of P23-H (Commit `6b22269` $\to$ Commit `3eef803`)
During the post-implementation audit of Phase 23-H, four specific findings were documented:
1. **The Epistemic Bug (FIX-23H-01):** The initial engine returned `KleeneValue.FALSE` when premise deduction failed. This committed the formal fallacy of *denying the antecedent* ($\neg P \land (P \to Q) \not\vdash \neg Q$), converting unproven states into false certainty.
   - *Fix:* Rewrote evaluation into four sound quadrants: antecedent false $\to$ `UNKNOWN` with `InformationSubgoal`; negative fact $\to$ `FALSE`; negative rule firing $\to$ `FALSE`; positive fact $\to$ `TRUE`. Upholding: **UNKNOWN must never silently become certainty**.
2. **Allocation Claim Tightening:** The claim of "zero heap allocation" was tightened to "0 net persistent heap growth / 0 dynamic container growth in steady-state loop".
3. **Cross-Lingual Projection Verification:** Expanded test F6 to verify real ingress projection from EN, VI, and JA drivers through `LanguageIngressGate` into identical numeric terms.
4. **Deep Multi-Step Verification:** Verified zero container growth under recursive depth-4 deductions.

---

## 4. Known Subsystem Limitations

1. **Static Horn Clause Limitation (P23-H):** Supports only conjunctive Horn rules ($P_1 \land \dots \land P_k \to H$). Does not support disjunctive heads ($H_1 \lor H_2$), existential quantification, or higher-order logic.
2. **Hard Recursion & Step Bounds (P23-H):** Inference terminates at depth $\le 8$ and steps $\le 256$. Complex proofs exceeding these bounds terminate with `UNKNOWN`.
3. **Closed Language Firewall (P23-F):** Ingress/egress is strictly limited to English, Vietnamese, and Japanese. All other languages are blocked at the perimeter.
4. **Controlled Vocabulary Coverage (P23-F):** Language drivers currently support canonical frames and core vocabulary; unconstrained open-domain slang requires vocabulary expansion.

---

## 5. Hypotheses Evaluated in P23-I & Gemini Research Disposition

Gemini completed empirical investigation of these hypotheses in [`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md):
1. **The Concept-to-Reasoning Bridge:** Evaluated in simulation fixtures; Gemini concluded bridging is feasible (`RESEARCH-VALIDATED`) without token sequences.
2. **Open-Domain Dynamic Rules (Negative Result):** Evaluated and **REJECTED**; runtime compilation of novel Horn rules corrupts $O(1)$ lookup and violates bounded recursion invariants.
3. **Sub-Phase Disposition Candidate:** Gemini proposed advancing under `FREEZE WITH PARAMETER` as `Contract Transition Ready`.
4. **Epistemic Status:** These conclusions are attributed research proposals submitted for Ciah review ([`docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md)). Contract freeze is pending; implementation is strictly unauthorized.
