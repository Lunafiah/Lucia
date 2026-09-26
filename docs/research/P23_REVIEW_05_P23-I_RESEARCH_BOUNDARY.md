# P23 Review Pack — File 5: P23-I Research Boundary & Non-Implementation Mandate

> **Document 5 of 5 in the P23 Reviewer Pack**  
> **Target Audience:** Reviewer with strict reading budget / NotebookLM / Gemini Ingestion  
> **Status:** `[CANONICAL RESEARCH BOUNDARY SPECIFICATION]`  
> **Current Active State:** `RESEARCH ONLY — ARCHITECTURE NOT DECIDED — IMPLEMENTATION NOT AUTHORIZED`

---

> [!WARNING]
> ### THIS DOCUMENT IS NOT AN IMPLEMENTATION SPECIFICATION
> It defines the epistemic and governance perimeter for Phase 23-I research.  
> No code in `src/core/` or `electron/` may be authored under this document.  
> No semantic representation architecture has been selected.

---

## 1. The P23-I Research Question

> **What, if anything, must exist between language-independent concept formation and the bounded reasoning substrate established by P23-H so that Lucia can form, maintain, manipulate, and communicate compositional meaning without natural-language token sequences as its cognitive substrate?**

The research must also explicitly answer:
- Does P23-I represent a distinct, necessary architectural layer?
- Should P23-I be merged into existing contracts (P23-C / P23-G)?
- Does the missing problem belong to Phase 24 (Temporal Embodiment & Social Feedback)?
- Should P23-I not exist at all?

---

## 2. Why the Question Exists

With the freezing of P23-H at commit `3eef803`, Lucia possesses:
1. An empirical front-end monograph demonstrating how speech prosody and syntactic dependencies are extracted on edge hardware (P23-C);
2. A formal language-independent contract projecting graphs into numeric terms (P23-G);
3. A bounded backward goal-directed reasoning kernel with Strong Kleene K3 evaluation and JTMS non-monotonic retraction (P23-H).

However, an operational gap remains between **perceptual concept prototypes** and **static formal deduction**:
- **P23-C** produces concept prototypes from incoming signals.
- **P23-H** requires static, pre-compiled Horn rules and pre-asserted facts.
- **The Gap:** In spontaneous, multi-turn interpersonal communication, concepts are not static textbook propositions; they are dynamically bound, context-dependent, and situationally modified. The architecture has not yet proven how dynamic compositional meaning is formed and manipulated across turns without natural-language token buffers.

---

## 3. What P23-H Enables vs. What It Does Not Establish

### What P23-H Enables (Proven & Frozen)
- Microsecond-scale backward goal resolution ($9.5\,\mu\text{s}$) over numeric terms;
- $O(1)$ rule lookup via static head-predicate indexing ($0.1\,\mu\text{s}$);
- Sound Strong Kleene evaluation upholding **UNKNOWN must never silently become certainty**;
- Non-monotonic cascade retraction ($P_1 \to P_2 \to P_3 \to P_4$) via JTMS;
- Subgoal generation (`InformationSubgoal`, `DisambiguationSubgoal`);
- 100% CPU edge execution ($0.0\text{ MB}$ GPU VRAM, 0 net persistent heap growth).

### What P23-H Does NOT Establish
- **Does NOT prove general language-independent semantic representation:** P23-H proves only that discrete integer deduction works over pre-defined rules.
- **Does NOT prove semantic equivalence across languages:** Parallel projection of canonical test sentences does not prove universal cross-lingual semantic capture.
- **Does NOT establish referential grounding:** Symbolic deduction over integer entities does not ground those entities in sensorimotor perception or episodic memory.
- **Does NOT establish continuous semantic communication:** Discrete backward chaining does not solve dynamic communicative intent or social-affective resonance.

---

## 4. Candidate Research Directions to Investigate

The following research avenues may be explored conceptually and in isolated simulation fixtures:
1. **Dynamic Relational Compositionality:** Can compositional relations be instantiated and modified at runtime without pre-compiled Horn rule indices?
2. **Dynamic Concept Binding & Scoping:** Mechanisms for tracking temporary situational variables and discourse referents across turns without natural language strings.
3. **Continuous-to-Discrete Semantic Transduction:** How continuous limbic vectors (PAD) and acoustic prosody dynamically influence which semantic structures are selected for communication.
4. **Subsumption / Elimination Analysis:** Rigorous testing of whether existing P23 components (P23-C, P23-D, P23-G, P23-H) already suffice when integrated, rendering P23-I redundant.

---

## 5. Falsification & Decision Criteria

Phase 23-I must be **formally rejected** or **merged** if:
1. **Redundancy:** Empirical testing shows that P23-C and P23-G directly interface to solve the communicative goal without any intermediate subsystem.
2. **Computational Infeasibility:** Proposed intermediate architectures exceed the 20W edge CPU budget ($>30\text{ ms}$ SLA or $>250\text{ MB}$ RAM).
3. **Epistemic Corruption:** Proposed mechanisms violate Strong Kleene separation or convert UNKNOWN into certainty.
4. **VRAM Violation:** Proposed models require GPU VRAM ($> 0.0\text{ MB}$), violating cognitive core edge isolation.

---

## 6. Prohibited Actions (Non-Implementation Mandate)

Until Phase 23-I research concludes, produces an authoritative research report, passes Ciah review, secures user approval, and clears an Architecture Gate:
- **DO NOT** author or modify any files in `src/core/`;
- **DO NOT** implement semantic graphs, HDC/VSA layers, or neural ontology models;
- **DO NOT** modify the frozen P23-H kernel (`src/core/cognition/kernel/`);
- **DO NOT** add new S1–S16 pipeline stages to `CognitiveOrchestrator`;
- **DO NOT** modify Genesis onboarding (`data/profile.json`);
- **DO NOT** activate Lucia.
