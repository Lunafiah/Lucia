# Formal Architectural Ratification: Discourse Referent Retention Contract (Phase 23)

> **Document Type**: Formal Architectural Ratification Record  
> **Status**: `[ARCHITECTURALLY RATIFIED]`  
> **Target Document**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md)  
> **Phase**: Phase 23 — Semantic Substrate & Non-Generative Communication  
> **Date**: 2026-10-14  
> **Authority**: Architectural Governance (Lucia Architectural Copilot & System Governance)  

---

## 1. Executive Ratification Statement

$$\mathbf{DISCOURSE\ REFERENT\ RETENTION\ CONTRACT\ \text{—}\ ARCHITECTURALLY\ RATIFIED}$$

The architectural specification for cross-turn **Discourse Referent Retention** defined in [`DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md) has successfully completed all research gates, isolated benchmark evaluations, and finalization/integrity audits. 

It is hereby formally recorded as **ARCHITECTURALLY RATIFIED** within the Phase 23 research baseline.

---

## 2. Seven Core Ratified Architectural Decisions

### 2.1 Ownership
- Discourse referent retention is owned strictly by the turn-coordination layer ([`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)).
- **CAPS does NOT own discourse memory.** (Discourse state must be accessible read-only during turn ingress for user mention resolution before cognitive processing or CAPS executes).

### 2.2 Purpose Boundary
- The cache exists solely to maintain a bounded active referent set for resolving cross-turn anaphora and ellipses.
- It is strictly forbidden from functioning as a conversation transcript store, world model, user model, or long-term episodic memory.

### 2.3 Orthogonality & Non-Equivalence Invariants
Reference resolution status and epistemic truth status are two strictly independent, orthogonal dimensions:
- **Reference Resolution Status**: `RESOLVED`, `AMBIGUOUS`, `UNKNOWN / UNRESOLVED`, `TYPE_MISMATCH`.
- **Epistemic State**: `FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`.

Explicit non-negotiable invariants ratified:
$$\mathbf{RESOLVED \neq FACT}$$
$$\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$$
Successfully resolving a referent (e.g. knowing who *"he"* is) has no bearing on whether the proposition is factual. User statements remain `ASSERTED` or `HYPOTHETICAL` ($C \le 0.70$) and are never automatically promoted to `FACT`.

### 2.4 Boundedness
- The architectural requirement that discourse state MUST be a **bounded active referent set** with decay and threshold eviction is formally ratified.
- Specific configuration values ($N_{\text{max}} = 16$, $\gamma = 0.60$, $\theta_{\text{evict}} = 0.15$) remain **PROVISIONAL CONFIGURATION PARAMETERS** pending human conversational dataset tuning.
- The memory observation ($\le 2\text{ KB}$ heap) remains an empirical benchmark observation, NOT an unalterable production invariant.

### 2.5 Determinism Scope
- Determinism is verified and claimed strictly for the **isolated reference resolution algorithm given a frozen, fully specified input snapshot and fixed contract version**.
- Global runtime determinism is NOT claimed.

### 2.6 Failure Semantics
- Ambiguity is preserved: `AMBIGUOUS` is never heuristically or probabilistically resolved into certainty.
- Fail-closed behavior: `UNKNOWN / UNRESOLVED` and `TYPE_MISMATCH` fail closed to interrogative communicative acts (`INQUIRE`/`DECLINE`).
- Resolution failure NEVER generates epistemic facts.

### 2.7 CAPS Precondition Relationship
- This ratification formally resolves Research Gate **R3** (Turn-level discourse entity retention) from the CAPS Implementation Readiness Gate.
- It constitutes a necessary prerequisite for a future CAPS implementation contract, **NOT an authorization for CAPS production implementation**.

---

## 3. Strict Governance Boundaries

$$\mathbf{CAPS\ IMPLEMENTATION\ REMAINS\ GATED}$$

| Milestone / Component | Architectural Status | Implementation Authorization |
|---|---|---|
| **Discourse Referent Retention Contract** | `[ARCHITECTURALLY RATIFIED]` | `[PRE-IMPLEMENTATION SPECIFICATION]` |
| **CAPS Boundary Contract** ([`P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md)) | `[ARCHITECTURALLY RATIFIED]` | `[BOUNDARY ONLY / NOT AUTHORIZED]` |
| **CAPS Implementation Contract** | `[NOT YET RATIFIED]` | `[NOT AUTHORIZED]` |
| **CAPS Production Implementation** (`src/core/**`) | `[LOCKED / NOT AUTHORIZED]` | `[ZERO PRODUCTION MUTATION]` |

---

## 4. Verification Check
- Production code diff (`src/core/**`): **0**
- Electron diff (`electron/**`): **0**
- Data state diff (`data/**`): **0**
- Genesis Invariant: [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact `{"is_onboarded": false}`
- Boundary decisions S1–S16 in [`P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md): **Unchanged**
- Canonical documents ([`ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), [`PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md)): **Unchanged**
