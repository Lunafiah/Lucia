# DOC-P23H-RULE-COMPILER-IMPLEMENTATION-SPEC-R1-001
## KnowledgeStore → P23-H RuleIndex Compiler Implementation Specification

**Document Identifier**: `DOC-P23H-RULE-COMPILER-IMPLEMENTATION-SPEC-R1-001`  
**Phase & Topic**: Phase 23-H Symbolic Reasoning / Epistemic Ingress  
**Authority Context**: Derived from ratified `DOC-P23H-RULE-COMPILER-CONTRACT-V1-001` and `DOC-P23H-RULE-COMPILER-SPEC-R1-CORRECTION-001`  
**Operating Mode**: Read-Only Specification. Zero production code modifications, zero test changes, zero kernel edits.  
**Target Delivery Module**: `src/core/cognition/kernel/compiler.py` (Future Implementation Task)

---

### 1. Executive Summary & Verdict

This document provides the **authoritative implementation specification** for the `RuleCompilerAdapter` that compiles symbolic string-based Horn rules from `KnowledgeStore.InferenceRule` into compact, numeric, pre-indexed `RuleIndex` structures consumable by the frozen Phase 23-H `ReasoningKernel`.

The specification resolves all prior ambiguities:
1. **Head Argument Completeness**: Enforces deterministic variable scanning across all three head argument positions (`head.arg0`, `head.arg1`, `head.arg2`).
2. **Head Variable Safety**: Enforces the classical Horn-clause safety condition ($\text{Vars}(\text{Head}) \subseteq \bigcup_{i} \text{Vars}(\text{Premise}_i)$), strictly quarantining unsafe rules to prevent negative variable indices from leaking into `TermArena`.
3. **Calibrated Determinism**: Guarantees deterministic rule compilation order and deterministic intra-rule variable indexing without claiming global `SymbolTable` bit-exactness across restarts.
4. **Duplicate Boundary Isolation**: Protects the compiler input boundary via first-rule-wins collision rejection while explicitly recognizing that `KnowledgeStore` storage already overwrites duplicate string keys at the dictionary level.
5. **Discrete K3 Purity**: Compiles exclusively positive Horn clauses (`polarity = True`) and excludes `confidence_decay` from the symbolic kernel.

**Final Specification Verdict**: **`READY FOR IMPLEMENTATION`**

---

### 2. Architecture & Subsystem Boundary

```text
====================================================================================================
                                SUBSYSTEM BOUNDARY & DATA FLOW
====================================================================================================

  [PERSISTENCE & STORAGE DOMAIN]
  KnowledgeStore (src/core/knowledge/store.py)
    └── _rules: Dict[str, InferenceRule]  [REPOSITORY FACT: String keys, Dict overwrite on storage]
            │
            │ sorted(rules, key=lambda r: r.id) [RATIFIED SPECIFICATION: Deterministic input order]
            ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                           RuleCompilerAdapter (Future Component)                       │
  │                  (Target Module: src/core/cognition/kernel/compiler.py)                │
  │                                                                                        │
  │  1. Structural Validator   ── Validate 3-tuples, non-empty predicate strings           │
  │  2. Variable Analyzer      ── Scan arg0..arg2, detect "?*", allocate VAR_0..VAR_7      │
  │  3. Safety Gate            ── Enforce Vars(Head) ⊆ Union(Vars(Premises))               │
  │  4. Symbol Interner        ── Call SymbolTable.intern_concept(), intern_rule()         │
  │  5. Collision Protector    ── Enforce first-rule-wins on compiler input boundary       │
  │  6. Kernel Rule Builder    ── Instantiate RuleHead, RulePremise, P23-H InferenceRule   │
  └────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼ Emits Tuple[RuleIndex, RuleCompilationReport]
  [REASONING & RUNTIME DOMAIN]
  P23-H Reasoning Kernel (src/core/cognition/kernel/)
    ├── SymbolTable: Runtime string <-> int symbol interning [VALIDATED EXISTING CONTRACT]
    ├── RuleIndex: Head-predicate indexed Horn clauses [VALIDATED EXISTING CONTRACT]
    │     └── get_rules_for_head(predicate_id) -> List[InferenceRule]
    └── ReasoningKernel: Bounded K3 Backward Chaining Engine [VALIDATED EXISTING CONTRACT]
====================================================================================================
```

#### Layer Responsibilities
* **`KnowledgeStore` Layer**: Stores domain rules with string identifiers (`"rule:..."`), human-readable descriptions (`name`), domain tags (`domain`), and floating-point `confidence_decay`. It knows nothing of negative variable indices or arena allocations (`[REPOSITORY FACT]`).
* **`RuleCompilerAdapter` Layer**: Translates, validates, and interns source rules into immutable numeric structures. It filters out malformed, oversized, or unsafe rules fail-softly, emitting a structured diagnostic report (`[RATIFIED SPECIFICATION]`).
* **`P23-H Kernel` Layer**: Operates exclusively over numeric integer IDs (`rule_id > 0`, `predicate_id > 0`, `arg \in [-8, -1] \cup [0, \infty)`). Remains 100% frozen, allocation-free in reasoning, and logic-deterministic (`[VALIDATED EXISTING CONTRACT]`).

---

### 3. Exact Field Mapping Specification

| Source Field (`KnowledgeStore.InferenceRule`) | Target Field (`P23-H Kernel`) | Classification | Compilation Transformation Rule |
|---|---|---|---|
| `rule.id: str` | `InferenceRule.rule_id: int` | `[RATIFIED SPECIFICATION]` | `ru_id = symbol_table.intern_rule(rule.id)`. Integer must be $> 0$. Reversible via `symbol_table.get_rule_symbol(ru_id)`. |
| `consequent_pattern[1]: str` | `RuleHead.predicate_id: int` | `[RATIFIED SPECIFICATION]` | `pred_id = symbol_table.intern_concept(consequent_pattern[1])`. Must be $> 0$. |
| `consequent_pattern[0]: str` | `RuleHead.arg0: int` | `[RATIFIED SPECIFICATION]` | If variable token $\rightarrow$ mapped negative variable slot (`-1 .. -8`). If constant $\rightarrow$ `symbol_table.intern_concept()`. |
| `consequent_pattern[2]: str` | `RuleHead.arg1: int` | `[RATIFIED SPECIFICATION]` | If variable token $\rightarrow$ mapped negative variable slot (`-1 .. -8`). If constant $\rightarrow$ `symbol_table.intern_concept()`. |
| `consequent_pattern` 3rd arg | `RuleHead.arg2: int` | `[RATIFIED SPECIFICATION]` | If 3-tuple has no 3rd argument, defaults to `0`. If present, mapped to variable slot or constant concept ID. |
| *(None in source)* | `RuleHead.polarity: bool` | `[RATIFIED SPECIFICATION]` | Fixed to `True` for v1 positive-Horn compiler. |
| `antecedents[i][1]: str` | `RulePremise[i].predicate_id: int` | `[RATIFIED SPECIFICATION]` | `pred_id = symbol_table.intern_concept(antecedents[i][1])`. Must be $> 0$. |
| `antecedents[i][0]: str` | `RulePremise[i].arg0: int` | `[RATIFIED SPECIFICATION]` | If variable token $\rightarrow$ mapped negative variable slot (`-1 .. -8`). If constant $\rightarrow$ `symbol_table.intern_concept()`. |
| `antecedents[i][2]: str` | `RulePremise[i].arg1: int` | `[RATIFIED SPECIFICATION]` | If variable token $\rightarrow$ mapped negative variable slot (`-1 .. -8`). If constant $\rightarrow$ `symbol_table.intern_concept()`. |
| `antecedents[i]` 3rd arg | `RulePremise[i].arg2: int` | `[RATIFIED SPECIFICATION]` | Defaults to `0`. If present, mapped to variable slot or constant concept ID. |
| *(None in source)* | `RulePremise[i].polarity: bool` | `[RATIFIED SPECIFICATION]` | Fixed to `True` for v1 positive-Horn compiler. |
| `antecedents` sequence order | `InferenceRule.premises: Tuple` | `[RATIFIED SPECIFICATION]` | Antecedents are preserved 1:1 in index order $0 \dots k-1$. |
| `rule.name: str` | *(None in kernel)* | `[RATIFIED SPECIFICATION]` | Omitted from kernel. Retained in compiler logging and `RuleDiagnostic`. |
| `rule.domain: str` | *(None in kernel)* | `[RATIFIED SPECIFICATION]` | Omitted from kernel. P23-H deduction is purely structural and domain-neutral. |
| `rule.confidence_decay: float` | *(None in kernel)* | `[RATIFIED SPECIFICATION]` | **Excluded from P23-H symbolic kernel**. Strong Kleene K3 operates discretely; derivations are tagged `EpistemicStatus.INFERRED`. |

---

### 4. Variable Compilation & Head Safety Specification

#### 4.1 Variable Token Definition
`[RATIFIED SPECIFICATION]`  
A term $T$ is recognized as a variable if and only if:
```python
isinstance(T, str) and T.startswith("?") and len(T) > 1
```
Any term not matching this predicate is classified as a constant and interned via `SymbolTable.intern_concept()`. A bare `"?"` is invalid and triggers rule quarantine.

#### 4.2 Deterministic Scan & Allocation Order
`[RATIFIED SPECIFICATION]`  
For each rule, a fresh, local symbol mapping is initialized: `var_map: Dict[str, int] = {}`. Variable slots are allocated monotonically by scanning in the exact sequence:
1. `head.arg0` (consequent subject)
2. `head.arg1` (consequent object)
3. `head.arg2` (consequent modifier / 3rd argument, if present)
4. `antecedent[0].arg0` $\rightarrow$ `antecedent[0].arg1` $\rightarrow$ `antecedent[0].arg2`
5. `antecedent[1].arg0` $\rightarrow$ `antecedent[1].arg1` $\rightarrow$ `antecedent[1].arg2`
6. `antecedent[2].arg0` $\rightarrow$ `antecedent[2].arg1` $\rightarrow$ `antecedent[2].arg2`
7. `antecedent[3].arg0` $\rightarrow$ `antecedent[3].arg1` $\rightarrow$ `antecedent[3].arg2`

The assignment formula for the $i$-th unique variable encountered ($i \in \{0 \dots 7\}$) is:
$$\text{VAR\_INDEX}(i) = -(i + 1) \quad \implies \quad \text{VAR\_0} = -1, \; \text{VAR\_1} = -2, \; \dots, \; \text{VAR\_7} = -8$$

#### 4.3 Variable Capacity Limit
`[VALIDATED EXISTING CONTRACT]`  
If the total number of distinct variable tokens in a rule exceeds `MAX_VARS` (8), the rule violates P23-H bounds ([`src/core/cognition/kernel/binding.py#L17`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/binding.py#L17)) and **must be quarantined**.

#### 4.4 Head Variable Safety Invariant (Final Correction 2)
`[RATIFIED SPECIFICATION]`  
In deductive Horn-clause logic, an **unsafe rule** is one in which a variable appears in the consequence (Head) without being bound by any premise in the body (Antecedents):
$$\text{Vars}(\text{Head}) \subseteq \bigcup_{i=0}^{k-1} \text{Vars}(\text{Antecedent}_i)$$

* **Failure Mode if Unchecked**: If an open or partially grounded goal unifies with an unsafe rule, `_resolve_arg()` ([`src/core/cognition/kernel/engine.py#L703-L709`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L703-L709)) leaves the unbound head variable as a negative integer. This negative integer would be passed directly to `TermArena.allocate_term()`, corrupting the arena with raw variable indices and breaking downstream conflict detection.
* **Specification Enforcement**: Before constructing `P23-H.InferenceRule`, the compiler computes:
  $$\text{head\_vars} = \{v \in \text{var\_map} \mid v \text{ appears in Head}\}$$
  $$\text{body\_vars} = \{v \in \text{var\_map} \mid v \text{ appears in at least one Antecedent}\}$$
  If $\text{head\_vars} \setminus \text{body\_vars} \ne \emptyset$, the rule is **quarantined as `UNSAFE_HEAD_VARIABLE`**.

---

### 5. Predicate & Symbol Interning

#### 5.1 Interning Invariants
* `[VALIDATED EXISTING CONTRACT]`: Predicates and constants are interned via [`SymbolTable.intern_concept(symbol: str) -> int`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L76-L84). Concept IDs start at 100.
* `[VALIDATED EXISTING CONTRACT]`: Rule string IDs are interned via [`SymbolTable.intern_rule(rule_id: str) -> int`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L128-L136). Rule IDs start at 1.

#### 5.2 Determinism Calibration (Final Correction 3)
`[RATIFIED SPECIFICATION]`  
* The compiler guarantees **deterministic compilation order** and **deterministic intra-rule variable indexing** by sorting input rules lexicographically (`sorted(rules, key=lambda r: r.id)`).
* The compiler **does NOT claim bit-exact global `SymbolTable` IDs across restarts**. Because `SymbolTable` can intern symbols from perception, dialogue context, or CAPS, global integer values depend on the orchestrator's complete interner lifecycle.

---

### 6. Constraint Validation Pipeline

`[RATIFIED SPECIFICATION]`  
To prevent partially compiled, oversized, or invalid rules from polluting `RuleIndex` or crashing startup, the compiler executes an **ordered, fail-soft pipeline** for each candidate rule:

```text
 Candidate Source Rule (KnowledgeStore.InferenceRule)
   │
   ├─► Step 1: Structural Validation
   │     • consequent_pattern is tuple of length 3?
   │     • antecedents is list/tuple of length >= 1?
   │     • every antecedent is tuple of length 3?
   │     [FAIL -> Quarantine: MALFORMED_STRUCTURE]
   │
   ├─► Step 2: Predicate Validation
   │     • consequent predicate is non-empty string?
   │     • all antecedent predicates are non-empty strings?
   │     [FAIL -> Quarantine: EMPTY_PREDICATE]
   │
   ├─► Step 3: Antecedent Count Bound
   │     • 1 <= len(antecedents) <= 4 (MAX_PREMISES)?
   │     [FAIL -> Quarantine: EXCESS_PREMISES]
   │
   ├─► Step 4: Variable Extraction & Count Bound
   │     • Scan head.arg0..arg2, then premise[0..k-1].arg0..arg2.
   │     • Count distinct variables starting with "?".
   │     • unique_variables <= 8 (MAX_VARS)?
   │     [FAIL -> Quarantine: EXCESS_VARIABLES]
   │
   ├─► Step 5: Head Safety Verification
   │     • Are all variables in head present in at least one premise?
   │     [FAIL -> Quarantine: UNSAFE_HEAD_VARIABLE]
   │
   ├─► Step 6: Input Boundary Duplicate Check
   │     • Has this numeric rule_id already been registered in this compilation pass?
   │     [FAIL -> Quarantine/Skip: DUPLICATE_RULE_ID]
   │
   └─► Step 7: Build & Index
         • Allocate RuleHead(predicate_id, a0, a1, a2, polarity=True)
         • Allocate Tuple[RulePremise(predicate_id, a0, a1, a2, polarity=True), ...]
         • Instantiate P23-H InferenceRule(rule_id, head, premises)
         • Call RuleIndex.add_rule(inferred_rule)
         [SUCCESS -> Mark COMPILED]
```

---

### 7. Duplicate Rule ID Policy (Final Correction 4)

`[RATIFIED SPECIFICATION]`  
* **Storage Boundary (`KnowledgeStore`)**: `KnowledgeStore._rules` is a Python dictionary (`Dict[str, InferenceRule]`). Storing two rules with identical string IDs on disk results in an immediate dictionary overwrite. The compiler **cannot recover rules already overwritten at storage time** (`[REPOSITORY FACT]`).
* **Compiler Input Boundary**: When the compiler receives an external sequence `Sequence[InferenceRule]` containing duplicate rule IDs, it enforces a **first-rule-wins** policy:
  1. The compiler tracks registered IDs in `seen_rule_ids: Set[int] = set()`.
  2. If a rule's interned `rule_id` is already in `seen_rule_ids`, the compiler **skips** the rule and logs `DUPLICATE_RULE_ID`.
  3. The compiler **never calls `RuleIndex.add_rule()` with a duplicate ID**, preventing P23-H's internal `ValueError` from raising.

---

### 8. Diagnostics & Observability Specification

`[RATIFIED SPECIFICATION]`  
The compiler produces a typed, immutable report with zero unhandled exceptions:

```python
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional

class RuleDiagnosticCode(str, Enum):
    OK = "OK"
    MALFORMED_STRUCTURE = "MALFORMED_STRUCTURE"
    EMPTY_PREDICATE = "EMPTY_PREDICATE"
    EXCESS_PREMISES = "EXCESS_PREMISES"
    EXCESS_VARIABLES = "EXCESS_VARIABLES"
    UNSAFE_HEAD_VARIABLE = "UNSAFE_HEAD_VARIABLE"
    DUPLICATE_RULE_ID = "DUPLICATE_RULE_ID"

@dataclass(frozen=True)
class RuleDiagnostic:
    source_rule_id: str
    status: str                         # "COMPILED" | "QUARANTINED"
    code: RuleDiagnosticCode
    detail: str

@dataclass(frozen=True)
class RuleCompilationReport:
    total_source_rules: int
    compiled_count: int
    quarantined_count: int
    diagnostics: Tuple[RuleDiagnostic, ...]
```

---

### 9. Lifecycle Specification

`[RATIFIED SPECIFICATION]`  
1. **Compilation Timing**: Synchronous compilation during `CognitiveOrchestrator` initialization when binding `KnowledgeStore`.
2. **Determinism**: Rules are sorted lexicographically by `rule.id` prior to processing.
3. **Turn-Time Immutability**: `RuleIndex` is static and read-only during conversational turns. Zero heap allocations or lock contention occur in the reasoning loop.
4. **Lifecycle Reset**: Upon `CognitiveOrchestrator.reset_lifecycle()`, `RuleIndex` is recompiled cleanly alongside fresh `SymbolTable` and `TermArena` instances.
5. **Deferred Features**: Live mid-turn mutation, event-bus invalidation listeners, and online incremental rule index patching are **explicitly deferred** to future milestones.

---

### 10. Required Falsification & Validation Test Cases

The future test suite (`tests/unit/test_p23h_rule_compiler.py`) must implement and pass the following 16 specification test cases:

| Case # | Scenario Description | Expected Compiler Action | Expected Diagnostic Code |
|---|---|---|---|
| **TC-01** | Valid ground rule (all constants, no vars) | Compiles to `RuleHead` & `RulePremise` | `RuleDiagnosticCode.OK` |
| **TC-02** | Valid variable rule ($P(?x) \to Q(?x)$) | Compiles with `VAR_0 = -1` in both slots | `RuleDiagnosticCode.OK` |
| **TC-03** | Variable first appearing in `head.arg2` | Allocates variable from `head.arg2` correctly | `RuleDiagnosticCode.OK` |
| **TC-04** | Rule with exactly 8 distinct variables | Compiles with variables `VAR_0` through `VAR_7` | `RuleDiagnosticCode.OK` |
| **TC-05** | Rule with 9 distinct variables | Quarantined; does not enter `RuleIndex` | `RuleDiagnosticCode.EXCESS_VARIABLES` |
| **TC-06** | Unsafe head variable ($P(?x) \to Q(?x, ?y)$) | Quarantined; does not leak negative var | `RuleDiagnosticCode.UNSAFE_HEAD_VARIABLE` |
| **TC-07** | Malformed tuple (consequent length 2 or 4) | Quarantined fail-softly | `RuleDiagnosticCode.MALFORMED_STRUCTURE` |
| **TC-08** | Empty string as predicate (`""`) | Quarantined fail-softly | `RuleDiagnosticCode.EMPTY_PREDICATE` |
| **TC-09** | Rule with 5 antecedents | Quarantined; does not enter `RuleIndex` | `RuleDiagnosticCode.EXCESS_PREMISES` |
| **TC-10** | Duplicate rule IDs in compiler input list | First rule compiled, second rule skipped | `RuleDiagnosticCode.DUPLICATE_RULE_ID` |
| **TC-11** | KnowledgeStore duplicate overwrite | Only 1 rule delivered to compiler | Normal storage overwrite verified |
| **TC-12** | Input order perturbation | Sorted input produces identical `RuleIndex` | Compilation order deterministic |
| **TC-13** | Repeated variable binding identity | Identical tokens share identical negative int | Binding consistency verified |
| **TC-14** | Polarity invariance | All compiled heads/premises have `polarity=True` | Positive Horn verified |
| **TC-15** | `confidence_decay` ignored | Source float does not affect Strong Kleene | Kernel numeric purity verified |
| **TC-16** | Recompilation on reset | `reset_lifecycle()` rebuilds cleanly | Lifecycle reset verified |

---

### 11. Implementation Boundary Ledger

#### Tier A: VERIFIED EXISTING (Reused Directly, Zero Code Changes)
* [`src/core/cognition/kernel/rules.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/rules.py): `RuleHead`, `RulePremise`, `InferenceRule`, `RuleIndex`.
* [`src/core/cognition/kernel/binding.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/binding.py): `VAR_0 .. VAR_7`, `is_variable`, `BindingFrame`, `unify_terms`.
* [`src/core/cognition/contract/projection.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py): `SymbolTable.intern_concept()`, `SymbolTable.intern_rule()`, `SymbolTable.get_rule_symbol()`.
* [`src/core/knowledge/proposition.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/proposition.py): `KnowledgeStore.InferenceRule`.

#### Tier B: RATIFIED SPECIFICATION (To Be Implemented in Coding Task)
* `src/core/cognition/kernel/compiler.py`:
  - `RuleCompilerAdapter` class implementing the 7-step validation pipeline.
  - Variable scanning over `head.arg0..arg2` and `premise[0..3].arg0..arg2`.
  - Head safety verification ($\text{Vars}(\text{Head}) \subseteq \bigcup \text{Vars}(\text{Premises})$).
  - Diagnostic models: `RuleDiagnostic`, `RuleCompilationReport`, `RuleDiagnosticCode`.
  - Public compile interface: `compile_rule_set(rules: Sequence[InferenceRule], symbol_table: SymbolTable) -> Tuple[RuleIndex, RuleCompilationReport]`.
* `src/core/orchestrator/cognitive_orchestrator.py`:
  - Wire `compile_rule_set()` during orchestrator initialization to attach `RuleIndex` to `_reasoning_kernel`.

#### Tier C: DEFERRED (Explicitly Out of Scope)
* Syntactic negation encoding inside `KnowledgeStore.InferenceRule`.
* Continuous confidence decay calculations outside P23-H.
* Live event-bus invalidation or incremental rule index updates.
* Conversational natural-language question-to-Goal parsing.

---

### 12. Final Verdict

# **READY FOR IMPLEMENTATION**

### Architectural Clearance:
The specification is **complete, mathematically consistent, and rigorously bounded**. It adheres strictly to P23-H frozen kernel invariants, ADR-038 non-escalation rules, and Genesis lifecycle safeguards. A coding agent can implement `src/core/cognition/kernel/compiler.py` and its corresponding unit tests without architectural ambiguity.
