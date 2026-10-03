# Raw Measurements: Lucia Context Architecture v1 Evaluation

> **Evaluation Suite:** `EVAL-CONTEXT-V1-20260924`  
> **Environment:** Windows PowerShell, Python 3.12 (.venv)  
> **Target Commit SHA:** `27cbbd7ad736a3c719ccb4ca4e72541f9190fab7`  
> **Measurement Status:** Physical metrics OBSERVED/MEASURED across predefined traces; Token counts UNAVAILABLE.

---

## 1. Document Inventory & Byte/Line Accounting

| Document Key | File Path | Measured Bytes | Measured Lines | Logical Tier |
|---|---|---:|---:|:---:|
| `AGENTS.md` | `AGENTS.md` | 29,986 | 466 | L2 |
| `00_PROJECT_OVERVIEW.md` | `docs/00_PROJECT_OVERVIEW.md` | 25,306 | 244 | L2 |
| `ARCHITECTURE.md` | `docs/ARCHITECTURE.md` | 72,039 | 620 | L3 |
| `DOCUMENTATION_INDEX.md` | `docs/DOCUMENTATION_INDEX.md` | 49,552 | 204 | L4 |
| `L1_INVARIANTS.md` | `docs/L1_INVARIANTS.md` | 13,329 | 126 | L1 |
| `CONTEXT_INDEX.md` | `docs/CONTEXT_INDEX.md` | 8,156 | 80 | L4 |
| `PHASE_21_RESEARCH_SPEC.md` | `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md` | 13,801 | 150 | L5 |
| `PHASE_21_EVALUATION.md` | `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_EVALUATION_REPORT.md` | 16,764 | 143 | L5 |
| `PHASE_16_ARCHITECTURE.md` | `docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md` | 17,721 | 227 | L5 |
| `homeostatic_engine.py` | `src/core/emotion/homeostatic_engine.py` | 15,086 | 417 | L6 |
| `test_phase21_production.py`| `tests/unit/test_phase21_production.py` | 22,159 | 511 | Tests |

---

## 2. Task-by-Task Raw Measurement Traces

### Task T1: Research (Phase 21 Follow-Up Study Planning)
*Goal: Identify minimal context and pre-registered controls for a Phase 21 follow-up study on multi-timescale synaptic plasticity.*

#### Baseline (Pre-Context v1)
- **Documents Accessed (5)**:
  1. `AGENTS.md` (29,986 bytes, 466 lines)
  2. `docs/00_PROJECT_OVERVIEW.md` (25,306 bytes, 244 lines)
  3. `docs/ARCHITECTURE.md` (72,039 bytes, 620 lines)
  4. `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md` (13,801 bytes, 150 lines)
  5. `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_EVALUATION_REPORT.md` (16,764 bytes, 143 lines)
- **Total Bytes Read**: 157,896 bytes
- **Total Lines Read**: 1,623 lines
- **Relevant Documents**: 3 (`AGENTS.md` §0 & §6, `PHASE_21_RESEARCH_SPEC.md`, `PHASE_21_RESEARCH_EVALUATION_REPORT.md`)
- **Irrelevant / Peripheral Documents**: 2 (`docs/00_PROJECT_OVERVIEW.md`, `docs/ARCHITECTURE.md` full file ingested to find Tier 3 rules)
- **Retrieval Steps**: 5
- **Tool-Output Bytes**: ~165,000 bytes
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Identified H1–H6, AdamW, $\lambda_{\text{homeo}}=0.05, \lambda_{\text{philia}}=0.10$, spectral norm $\le 0.08$)
- **Architectural Adherence**: 100%

#### Context Architecture v1
- **Context Routing Strategy**: Consult `docs/CONTEXT_INDEX.md` (Research Task) $\to$ load L1 (`docs/L1_INVARIANTS.md`) + L2 (`AGENTS.md` §0, §6) + L5 (`PHASE_21_RESEARCH_SPEC.md`).
- **Documents Accessed (4)**:
  1. `docs/CONTEXT_INDEX.md` (8,156 bytes, 80 lines)
  2. `AGENTS.md` (29,986 bytes, 466 lines)
  3. `docs/L1_INVARIANTS.md` (13,329 bytes, 126 lines)
  4. `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md` (13,801 bytes, 150 lines)
- **Total Bytes Read**: 65,272 bytes (-58.7% vs Baseline)
- **Total Lines Read**: 822 lines (-49.4% vs Baseline)
- **Relevant Documents**: 4 (all directly contributed to task)
- **Irrelevant Documents**: 0
- **Retrieval Steps**: 4
- **Tool-Output Bytes**: ~68,000 bytes (-58.8% vs Baseline)
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Identified H1–H6, CPU BPTT, spectral norm $\le 0.08$, invariant controls)
- **Architectural Adherence**: 100%

---

### Task T2: Architecture Review (Intra-Turn Relationship Feedback)
*Goal: Review a proposed architectural change to add intra-turn feedback from $R_t$ to Stage 10 prompt assembly.*

#### Baseline (Pre-Context v1)
- **Documents Accessed (4)**:
  1. `AGENTS.md` (29,986 bytes, 466 lines)
  2. `docs/00_PROJECT_OVERVIEW.md` (25,306 bytes, 244 lines)
  3. `docs/ARCHITECTURE.md` (72,039 bytes, 620 lines)
  4. `docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md` (17,721 bytes, 227 lines)
- **Total Bytes Read**: 145,052 bytes
- **Total Lines Read**: 1,557 lines
- **Relevant Documents**: 2 (`docs/ARCHITECTURE.md` ADR-022, `PHASE_16_ARCHITECTURE.md`)
- **Irrelevant / Peripheral Documents**: 2 (`AGENTS.md`, `docs/00_PROJECT_OVERVIEW.md`)
- **Retrieval Steps**: 4
- **Tool-Output Bytes**: ~150,000 bytes
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Proposal REJECTED: violates ADR-022 two-phase lifecycle and introduces within-turn feedback loop).
- **Architectural Adherence**: 100%

#### Context Architecture v1
- **Context Routing Strategy**: Consult `docs/CONTEXT_INDEX.md` (Architecture Gate Task) $\to$ load L1 (`docs/L1_INVARIANTS.md` §5.2) + L2 (`AGENTS.md` §7).
- **Documents Accessed (3)**:
  1. `docs/CONTEXT_INDEX.md` (8,156 bytes, 80 lines)
  2. `docs/L1_INVARIANTS.md` (13,329 bytes, 126 lines)
  3. `AGENTS.md` (29,986 bytes, 466 lines)
- **Total Bytes Read**: 51,471 bytes (-64.5% vs Baseline)
- **Total Lines Read**: 672 lines (-56.8% vs Baseline)
- **Relevant Documents**: 3 (all directly contributed; `docs/L1_INVARIANTS.md` §5 explicitly records ADR-022 two-phase invariant: Stage 9 read $R_{t-1}$, Stage 16 update $R_t$).
- **Irrelevant Documents**: 0
- **Retrieval Steps**: 3
- **Tool-Output Bytes**: ~54,000 bytes (-64.0% vs Baseline)
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Proposal REJECTED: violates `L1_INVARIANTS.md` §5.2 and ADR-022 two-phase lifecycle).
- **Architectural Adherence**: 100%

---

### Task T3: Coding / Dry-Run Maintenance (HomeostaticEngine Audit)
*Goal: Audit `HomeostaticEngine` calculation of acute Tension ($\mathcal{T}$) and Cognitive Load ($\mathcal{C}$) against ADR-015 and state taxonomy.*

#### Baseline (Pre-Context v1)
- **Documents Accessed (5)**:
  1. `AGENTS.md` (29,986 bytes, 466 lines)
  2. `docs/00_PROJECT_OVERVIEW.md` (25,306 bytes, 244 lines)
  3. `docs/ARCHITECTURE.md` (72,039 bytes, 620 lines)
  4. `src/core/emotion/homeostatic_engine.py` (15,086 bytes, 417 lines)
  5. `tests/unit/test_phase21_production.py` (22,159 bytes, 511 lines)
- **Total Bytes Read**: 164,576 bytes
- **Total Lines Read**: 2,258 lines
- **Relevant Documents**: 2 (`docs/ARCHITECTURE.md` §3.3, `homeostatic_engine.py`)
- **Irrelevant / Peripheral Documents**: 3 (`AGENTS.md`, `00_PROJECT_OVERVIEW.md`, `test_phase21_production.py`)
- **Retrieval Steps**: 5
- **Tool-Output Bytes**: ~170,000 bytes
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Verified $\mathcal{T} = \text{clip}(|v-P_{01}| + 0.5\max(0, \mathcal{S}-0.4), 0, 1)$, zero inter-turn persistence, and $\mathcal{C}$ 60s window accumulation).
- **Architectural Adherence**: 100%

#### Context Architecture v1
- **Context Routing Strategy**: Consult `docs/CONTEXT_INDEX.md` (Bug Fix / Core Logic) $\to$ load L1 (`docs/L1_INVARIANTS.md` §3.5) + L6 (`homeostatic_engine.py`).
- **Documents Accessed (3)**:
  1. `docs/CONTEXT_INDEX.md` (8,156 bytes, 80 lines)
  2. `docs/L1_INVARIANTS.md` (13,329 bytes, 126 lines)
  3. `src/core/emotion/homeostatic_engine.py` (15,086 bytes, 417 lines)
- **Total Bytes Read**: 36,571 bytes (-77.8% vs Baseline)
- **Total Lines Read**: 623 lines (-72.4% vs Baseline)
- **Relevant Documents**: 3 (all directly contributed; `docs/L1_INVARIANTS.md` §3.5 provides exact taxonomy of Persistent vs Accumulated vs Instantaneous Derived Affect).
- **Irrelevant Documents**: 0
- **Retrieval Steps**: 3
- **Tool-Output Bytes**: ~38,500 bytes (-77.4% vs Baseline)
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Verified mathematical bounds and zero leaky persistence).
- **Architectural Adherence**: 100%

---

### Task T4: Documentation Task (Hierarchical Document Alignment)
*Goal: Maintain repository documentation structure and reading pathways when adding a new architecture specification.*

#### Baseline (Pre-Context v1)
- **Documents Accessed (4)**:
  1. `AGENTS.md` (29,986 bytes, 466 lines)
  2. `docs/DOCUMENTATION_INDEX.md` (49,552 bytes, 204 lines)
  3. `docs/00_PROJECT_OVERVIEW.md` (25,306 bytes, 244 lines)
  4. `docs/ARCHITECTURE.md` (72,039 bytes, 620 lines)
- **Total Bytes Read**: 176,883 bytes
- **Total Lines Read**: 1,534 lines
- **Relevant Documents**: 2 (`AGENTS.md` §3, `docs/DOCUMENTATION_INDEX.md`)
- **Irrelevant Documents**: 2 (`docs/00_PROJECT_OVERVIEW.md`, `docs/ARCHITECTURE.md`)
- **Retrieval Steps**: 4
- **Tool-Output Bytes**: ~182,000 bytes
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Updated classification matrix, directory map, and personas).
- **Architectural Adherence**: 100%

#### Context Architecture v1
- **Context Routing Strategy**: Consult `docs/CONTEXT_INDEX.md` (Governance / Documentation) $\to$ load L2 (`AGENTS.md` §3) + L4 (`docs/DOCUMENTATION_INDEX.md`).
- **Documents Accessed (3)**:
  1. `docs/CONTEXT_INDEX.md` (8,156 bytes, 80 lines)
  2. `AGENTS.md` (29,986 bytes, 466 lines)
  3. `docs/DOCUMENTATION_INDEX.md` (49,552 bytes, 204 lines)
- **Total Bytes Read**: 87,694 bytes (-50.4% vs Baseline)
- **Total Lines Read**: 750 lines (-51.1% vs Baseline)
- **Relevant Documents**: 3 (all directly relevant to documentation architecture)
- **Irrelevant Documents**: 0
- **Retrieval Steps**: 3
- **Tool-Output Bytes**: ~90,500 bytes (-50.3% vs Baseline)
- **Token Count**: TOKEN DATA UNAVAILABLE
- **Task Correctness**: Correct (Preserved single-source-of-truth invariants, no duplicate status docs created).
- **Architectural Adherence**: 100%

---

### Task T5: OpenCode Execution
- **Status**: **EXPLICITLY OUT OF SCOPE**. Not evaluated; no OpenCode experiments or benchmarks performed.
