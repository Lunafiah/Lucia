# Phase 23-G Evaluation Report — Semantic Substrate → Cognitive Core Contract

> **Authoritative Empirical Evaluation Report for Phase 23-G**<br/>
> *Status: [VALIDATED / CONTRACT IMPLEMENTED]*<br/>
> *Execution Date: 2026-09-26*

---

## 1. Executive Summary & Architectural Context

Phase 23-G establishes the formal, language-independent contract and boundary between the **Phase 23-F Semantic Substrate** (`SemanticGraph`) and the **Cognitive Core** reasoning engine in Project Lucia.

```text
Language Adapter (EN, VI, JA)
      ↓
P23-F Semantic Substrate (SemanticGraph)
      ↓
P23-G Projection Layer (ProjectGraphToTerms)
      ↓
Logical Flat Term Store (LogicalTerm, ScopeTerm, EntityTerm in preallocated TermArena)
      ↓
Cognitive Core Reasoning (Strong Kleene Conjunction, Non-monotonic JTMS, AMBIGUOUS Subgoals)
      ↓
Intent Substrate Graph (SynthesizeIntentGraph)
      ↓
Language Adapter (RealizeFromSubstrate)
```

### Key Architectural Invariants & Achievements
1. **Complete Language Independence**: The Cognitive Core contains zero natural language strings, zero lexical tokens, zero morphology, and zero language-code branching (`en`/`vi`/`ja`). All concepts, roles, scopes, entities, rules, and terms operate strictly on integer identifiers (`int`).
2. **Epistemic Safety**:
   - Supported epistemic states: `FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`.
   - `UNKNOWN` is never promoted to `FACT` or `INFERRED`.
   - `AMBIGUOUS` is never collapsed into one hypothesis without explicit interactive grounding.
   - `INFERRED` terms are strictly created by Cognitive Core assertions with mandatory `rule_id`, premise references, and provenance.
   - Bit-exact preservation of epistemic states through Graph → Term → Graph round trips.
3. **Strong Kleene Reasoning**:
   - Conjunction ($\land$): $\text{FALSE} \land \text{UNKNOWN} = \text{FALSE}$, $\text{TRUE} \land \text{UNKNOWN} = \text{UNKNOWN}$, $\text{UNKNOWN} \land \text{UNKNOWN} = \text{UNKNOWN}$.
   - $A \land \text{UNKNOWN}$ never produces certain truth.
4. **AMBIGUOUS Resolution Discipline**:
   - If all valid branches yield identical actions, action may proceed.
   - If branches produce incompatible actions, the Core produces a `DisambiguationSubgoal` rather than making an arbitrary or probabilistic choice.
5. **Non-Monotonic Inference (Cascade Invalidation)**:
   - Dependency tracking ($P_1 \to P_2 \to P_3 \to P_4$).
   - Retracting $P_1$ recursively invalidates all dependent inferred terms ($P_2, P_3, P_4$), while preserving independent facts and unrelated derivation branches untouched.
6. **Static Memory & Zero Dynamic Allocation**:
   - Inner query/reasoning loop executes with zero dynamic heap allocations using preallocated buffers (`QueryTermPatternIntoBuffer`).
   - `TermArena` enforces explicit capacity bounds; raises `ArenaCapacityExceededError` rather than silently truncating or overwriting.

---

## 2. Implemented Subsystems & Contracts

| Module | Location | Primary Responsibility |
|---|---|---|
| **`epistemic`** | `src/core/cognition/contract/epistemic.py` | `EpistemicStatus` (numeric IntEnum), `KleeneValue` (IntEnum), Strong Kleene logic operators (`kleene_and`, `kleene_or`, `kleene_not`, `kleene_all`). |
| **`provenance`**| `src/core/cognition/contract/provenance.py`| Numeric `ProvenanceRecord` (`rule_id: int`, `supporting_premise_ids: Tuple[int, ...]`) with bidirectional mapping to P23-E Knowledge ProvenanceRecord. |
| **`terms`** | `src/core/cognition/contract/terms.py` | `LogicalTerm`, `EntityTerm`, `ScopeTerm`, `TermQueryPattern`, and `BindingSet` data structures. |
| **`arena`** | `src/core/cognition/contract/arena.py` | `TermArena` preallocated fixed-capacity memory arena; indexed lookups; `ArenaCapacityExceededError`. |
| **`matcher`** | `src/core/cognition/contract/matcher.py` | `QueryTermPattern`, `QueryTermPatternIntoBuffer` (zero-alloc), and Kleene evaluation functions. |
| **`inference`**| `src/core/cognition/contract/inference.py`| `AssertInferredTerm` (epistemic safety), `RetractAndCascadeInvalidate` (JTMS), and `EvaluateAmbiguity` (`DisambiguationSubgoal`). |
| **`projection`**| `src/core/cognition/contract/projection.py`| `ProjectGraphToTerms` & `SymbolTable` converting `SemanticGraph` substrate to flat numeric terms. |
| **`synthesis`** | `src/core/cognition/contract/synthesis.py` | `SynthesizeIntentGraph` reconstructing `SemanticGraph` from active Core terms. |

---

## 3. Preregistered Falsification Test Results

All 11 preregistered falsification criteria in `tests/evaluation/phase23g/test_p23g_falsification.py` were executed and verified:

| Test ID | Hypothesis & Falsification Condition | Observed Outcome | Verdict |
|---|---|---|---|
| **FALSIFICATION-1** | **UNKNOWN Preservation**: $A \land \text{UNKNOWN}$ must never evaluate to TRUE. Attempting to infer a certain conclusion from UNKNOWN premise must be rejected. | Conjunctions evaluated strictly to UNKNOWN. Inference assertion rejected with `ASSERT_ERR_PREMISE_UNKNOWN`. | **PASS** |
| **FALSIFICATION-2** | **Kleene Conjunction Truth Table**: All 9 cells of Strong Kleene conjunction must be exact. | All 9/9 cells verified bit-exact against standard Strong Kleene truth table. | **PASS** |
| **FALSIFICATION-3** | **AMBIGUOUS Non-Collapse**: Conflicting branches must produce `DisambiguationSubgoal`; unanimous branches may proceed. | Disambiguation subgoal emitted for conflicting actions; unanimous action proceeded cleanly. | **PASS** |
| **FALSIFICATION-4** | **Cross-Lingual Invariance**: Parallel EN/VI/JA substrate graphs must project to isomorphic LogicalTerms with zero surface text in Core. | Identical predicate ID (`c:SOLVE_PROBLEM`), arg roles (`:ARG0`, `:ARG1`), entity relations across all 3 languages. | **PASS** |
| **FALSIFICATION-5** | **Provenance Retention**: Every INFERRED term must contain `rule_id` and premise references. Missing fields must fail assertion. | Missing rule ID (`ASSERT_ERR_MISSING_RULE`) and missing premises (`ASSERT_ERR_MISSING_PREMISES`) rejected. Valid assertions retain complete provenance. | **PASS** |
| **FALSIFICATION-6** | **Cascade Invalidation**: Retracting $P_1$ in $P_1 \to P_2 \to P_3 \to P_4$ must invalidate all dependent terms. | Retracting $P_1$ cleanly invalidated $P_1, P_2, P_3, P_4$ recursively. | **PASS** |
| **FALSIFICATION-7** | **Independent-State Preservation**: Retracting $P_1$ must not invalidate unrelated facts or parallel derivation branches. | Unrelated fact $F_{\text{ind}}$ and derivation $Q_1 \to Q_2$ remained active and unmodified. | **PASS** |
| **FALSIFICATION-8** | **Zero Dynamic Allocation**: Query execution in inner loop with preallocated buffer allocates 0 dynamic bytes on heap. | `tracemalloc` measured 0 non-tracemalloc heap allocations over 100 query cycles. | **PASS** |
| **FALSIFICATION-9** | **String-Independence Static Audit**: Core contract modules must contain zero language strings or language-specific branching. | AST and source scan confirmed zero `"en"`, `"vi"`, `"ja"` keywords or token regexes in Core reasoning logic. | **PASS** |
| **FALSIFICATION-10**| **Arena Exhaustion**: Allocations beyond capacity must return an explicit failure; never overwrite or truncate. | `ArenaCapacityExceededError` raised on capacity overflow; previous terms verified uncorrupted. | **PASS** |
| **FALSIFICATION-11**| **Round-Trip Preservation**: Substrate $\to$ Terms $\to$ Substrate must preserve concepts, entities, scopes, epistemic states, and provenance. | 100% round-trip fidelity: scopes, modal types, polarity, epistemic states, and provenance links preserved. | **PASS** |

---

## 4. Measured CPU Performance Benchmarks

All metrics were measured directly on local consumer edge hardware using `tests/evaluation/phase23g/benchmark_runner.py`:

### Hardware & Environment
- **CPU**: AMD Ryzen 7 5800H (8 Cores, 16 Threads)
- **OS**: Windows 11 (x64)
- **Python**: 3.12.10
- **GPU VRAM Impact**: **0.0 MB** (100% CPU edge execution)

### Operation Latencies Across Term Scales
| Scale | Projection Latency (Median) | Query Latency (Standard) | Query Latency (Zero-Alloc Fast) | Synthesis Latency (Median) | Round-Trip Latency (Median) | Peak RAM (Round-Trip) |
|---|---|---|---|---|---|---|
| **20 Terms** | **0.3021 ms** | **0.0006 ms** (0.6 µs) | **0.0010 ms** (1.0 µs) | **0.2245 ms** | **0.5513 ms** | **0.1393 MB** |
| **100 Terms** | **1.7197 ms** | **0.0006 ms** (0.6 µs) | **0.0006 ms** (0.6 µs) | **1.8802 ms** | **3.9414 ms** | **0.2666 MB** |
| **500 Terms** | **15.8638 ms** | **0.0008 ms** (0.8 µs) | **0.0006 ms** (0.6 µs) | **20.9371 ms** | **37.6462 ms** | **0.8755 MB** |
| **1,000 Terms**| **51.0924 ms** | **0.0008 ms** (0.8 µs) | **0.0006 ms** (0.6 µs) | **77.3909 ms** | **129.9382 ms**| **1.6603 MB** |

### Benchmark Observations
1. **Query Performance**: Index-assisted query latency scales sub-linearly ($0.6\text{ µs}$ to $0.8\text{ µs}$), remaining under $1\text{ µs}$ even at 1,000 terms.
2. **Zero Dynamic Allocation**: `QueryTermPatternIntoBuffer` executes within preallocated buffers with zero heap allocation.
3. **RAM Footprint**: At 1,000 terms, round-trip peak RAM is **$1.66\text{ MB}$**, well below the $15\text{ MB}$ conservative operational budget.

---

## 5. Epistemological Claim Categorization

Per repository scientific guardrails, all findings are categorized into distinct epistemological tiers:

### 5.1 SUPPORTED Claims (Empirically Proven in Evaluated Harness)
- **Strong Kleene Truth Tables**: Verified bit-exact for all 9 conjunction combinations and operations.
- **UNKNOWN Non-Promotion**: Verified that $A \land \text{UNKNOWN}$ never produces TRUE, and asserting an inference from UNKNOWN premises is blocked.
- **Cascade Retraction Invalidation**: Verified that $P_1 \to P_2 \to P_3 \to P_4$ invalidation cleanly ripples through dependent terms while preserving independent facts.
- **Disambiguation Subgoal Generation**: Verified that incompatible ambiguous branches produce a `DisambiguationSubgoal` without arbitrary probabilistic guessing.
- **Static Arena Bounds**: Verified that capacity overflow raises `ArenaCapacityExceededError` without silent truncation.
- **Substrate $\leftrightarrow$ Core Round-Trip Fidelity**: Verified that concepts, entities, scopes, polarity, epistemic states, and provenance links survive projection and synthesis intact.

### 5.2 PLAUSIBLE Claims (Theoretically Grounded Architectural Design)
- **Numeric Core Generalization**: The use of numeric identifiers (`concept_id`, `role_id`, `entity_id`) provides an effective substrate-neutral representation that decouples language surface structure from reasoning logic.
- **Preallocated Arena Scalability**: Operating with static arenas in consumer companion software avoids garbage collector pauses during conversational turn cycles.

### 5.3 SPECULATIVE Claims (Open Hypotheses Requiring Future Longitudinal Research)
- **Complex Multi-Agent Epistemic Tracking**: Extending the 4-state epistemic model to multi-agent theory of mind (e.g., Lucia's beliefs about User's beliefs) may require modal partition indexing beyond flat scope trees.
- **Autonomous Disambiguation Cadence**: The optimal dialogue threshold for when to trigger clarification subgoals vs when to defer until further context arrives remains to be tuned in interactive studies.

### 5.4 UNVERIFIED Claims (Explicitly NOT Claimed / Guardrails Enforced)
- **Kleene Logic Alone Guarantees Absence of False Certainty**: NOT claimed. Strong Kleene logic ensures formal propagation of uncertainty; it cannot prevent factual errors in initial premises.
- **Flat Tuples Eliminate Graph Reasoning Complexity**: NOT claimed. While flat terms in an arena simplify linear scanning and simple rule matching, complex multi-hop graph isomorphism remains computationally non-trivial.
- **Fixed Ontology Represents All Open-Domain Semantics**: NOT claimed. Current evaluation covers canonical semantic frames; open-domain language requires ongoing lexical and transducer expansion.
- **Cross-Lingual Invariance is Proven Globally**: NOT claimed. Invariance is verified on canonical parallel triplets; full unconstrained multilingual invariance requires broader semantic testing.

---

## 6. Architectural Gaps & Known Limitations

1. **Closed Lexicon & Frame Coverage**:
   - Current drivers and symbol tables operate on canonical semantic frames (actions, relations, states, ambiguity, zero-anaphora).
   - Complex subordinate clauses and open-domain metaphors require upstream neural semantic parsing (future research horizon).
2. **Interactive Disambiguation Execution**:
   - Phase 23-G defines the data contract and emits `DisambiguationSubgoal`. The conversational dialogue strategy that verbally resolves this subgoal with the user belongs to the downstream Communicative Policy (Layer 6 / Phase 15).
3. **Inner Loop Allocation Boundary**:
   - Zero dynamic allocation is strictly enforced for queries (`QueryTermPatternIntoBuffer`) and pattern matches. Initial graph projection and synthesis unavoidably allocate container objects (`SemanticGraph`, `SemanticNode`) at the external boundary.

---

## 7. Governance & Invariant Compliance

- **Development != Activation**: Genesis Onboarding gate preserved bit-exact (`data/profile.json` remains `{"is_onboarded": false}`).
- **Substrate Neutrality**: Adheres strictly to ADR-027 and Phase 22-SC findings.
- **P23-E / P23-F Compatibility**: Conservative Semantic Fortification and Language Adapter subsystems remained 100% intact with zero regressions across all prior unit and property tests.
- **Hardware Constraints**: 100% CPU execution on consumer hardware; 0.0 MB GPU VRAM utilized.
