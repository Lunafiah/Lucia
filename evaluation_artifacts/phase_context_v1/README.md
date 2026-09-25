# Evaluation Plan & Specification: Lucia Context Architecture v1

> **Empirical Evaluation of Context Architecture v1 (Logical Tiers L0–L6)**  
> **Evaluation ID:** `EVAL-CONTEXT-V1-20260924`  
> **Target Baseline Commit:** `27cbbd7ad736a3c719ccb4ca4e72541f9190fab7`  
> **Evaluation Type:** Repository-Context Retrieval Efficiency, Task Correctness, and Invariant Preservation  
> **Date:** September 2026

---

## 1. Objective & Hypothesis

The goal of this evaluation is to determine whether **Context Architecture v1** (the introduction of `docs/L1_INVARIANTS.md`, `docs/CONTEXT_INDEX.md`, and tiered routing L0–L6) enables an AI coding agent to obtain the **minimum sufficient context** required to correctly execute tasks, reducing unnecessary context retrieval and cognitive overhead while strictly preserving architectural invariants.

### Hypotheses:
- **H1 (Volume & Step Reduction)**: Context Architecture v1 reduces total repository bytes and lines read by $\ge 40\%$ across representative task traces compared to the baseline monolithic context retrieval pattern.
- **H2 (Strict Correctness & Invariant Preservation)**: Context Architecture v1 preserves 100% of applicable architectural invariants (INV-1 through INV-8) and task correctness with zero regressions.
- **H3 (Failure Mode Resistance)**: Clear logical layering prevents RFC failure modes (specifically F1 Missing Architectural Constraint, F2 Wrong Document Retrieval, and F3 Stale Context).

---

## 2. Experimental Methodology

### Baseline Workflow (Pre-Context v1)
Under the historical pattern, coding agents relied on reading `AGENTS.md`, full canonical documents (`docs/00_PROJECT_OVERVIEW.md`, `docs/ARCHITECTURE.md`), and historical phase specifications to identify relevant rules and mechanisms. Because invariants and mechanisms were dispersed throughout 600+ line documents, agents had to ingest large canonical files in full or perform broad searches across `docs/specs/**`.

### Context Architecture v1 Workflow
Under Context Architecture v1, agents follow the tiered protocol:
```text
Task Specification
       │
       ▼
L4: docs/CONTEXT_INDEX.md (Identify minimal sufficient layers)
       │
       ▼
L1: docs/L1_INVARIANTS.md (Universal constraints & invariant checks)
       │
       ▼
L2 / L3: Targeted section of AGENTS.md / docs/ARCHITECTURE.md (Only if specific mechanism needed)
       │
       ▼
L5: Specific active research spec (Only for research tasks)
       │
       ▼
L6: Target implementation file (Directly to relevant code)
```

---

## 3. Representative Task Suite

Four primary representative task classes are evaluated:

1. **T1 — Research Scope & Context Identification**:
   - Task: Identify required context and verify prior experimental controls for designing a Phase 21 follow-up study on multi-timescale synaptic plasticity.
   - Requirement: Extract invariant constraints, relevant hypothesis definitions, and baseline controls without loading unrelated UI/mascot or prompt assembly documentation.

2. **T2 — Architectural Review**:
   - Task: Review a proposed change to add an intra-turn feedback loop from `RelationshipUpdater` ($R_t$) directly into `CognitiveOrchestrator` Stage 10 prompt assembly to make conversation instantly responsive.
   - Requirement: Determine architectural feasibility, identify governing ADRs, check invariant violations (ADR-022, ADR-028, INV-2).

3. **T3 — Coding / Dry-Run Maintenance**:
   - Task: Audit and inspect `HomeostaticEngine` calculation of acute Tension ($\mathcal{T}$) and Cognitive Load ($\mathcal{C}$) against ADR-015 and homeostatic state taxonomy.
   - Requirement: Verify parameter bounds and zero inter-turn leaky persistence without ingesting unrelated voice or avatar rendering pipelines.

4. **T4 — Documentation Maintenance**:
   - Task: Update system documentation navigation following the addition of a new architectural specification.
   - Requirement: Identify canonical navigation index, document hierarchy, reading pathways, and maintain single-source-of-truth invariants without creating duplicate status files.

5. **T5 — Execution-Oriented Tooling (OpenCode)**:
   - Evaluated status: **OUT OF SCOPE**. Not evaluated; no benchmarks or experiments performed.

---

## 4. Measurement & Accounting Protocol

In accordance with Section 5 of the evaluation specification, direct token counts are reported as `UNAVAILABLE` because raw platform tokenizer APIs are not directly exposed in the execution sandbox. Accurate and reproducible physical proxies are measured:
- **Documents Accessed**: Count of distinct files opened.
- **Relevant Documents**: Count of documents directly answering the task requirements.
- **Irrelevant Documents**: Count of documents opened that did not contribute to task resolution.
- **Bytes Read**: Exact byte length of content ingested.
- **Lines Read**: Exact line count of content ingested.
- **Tool-Output Bytes**: Volume of stdout / tool response bytes.
- **Retrieval Steps**: Count of read / grep / find operations.
- **Task Correctness**: Boolean verification against canonical ground truth.
- **Architectural Adherence**: Full compliance with INV-1 through INV-8 and ADR ledger.
