# Comparison Results: Baseline vs. Context Architecture v1

> **Evaluation Suite:** `EVAL-CONTEXT-V1-20260924`  
> **Target Commit SHA:** `27cbbd7ad736a3c719ccb4ca4e72541f9190fab7`  
> **Classification:** Quantitative Side-by-Side Comparison Matrix across Predefined Traces T1–T4

---

## 1. Aggregated Metric Comparison Matrix (Predefined Evaluation Traces)

The table below summarizes the quantitative and qualitative outcomes across all evaluated tasks (T1, T2, T3, T4):

| Metric | Baseline (Pre-v1) | Context Architecture v1 | Difference (v1 vs Baseline) | Confidence / Method |
|---|---:|---:|---:|:---:|
| **Total Documents Accessed** | 18 | 13 | **-27.8%** (-5 docs) | Measured (File logs) |
| **Relevant Documents Accessed** | 9 | 13 | **+44.4%** (+4 docs) | Measured (Task trace) |
| **Irrelevant / Peripheral Documents** | 9 | 0 | **-100.0%** (-9 docs) | Measured (Task trace) |
| **Total Bytes Read** | 644,407 bytes | 240,998 bytes | **-62.6%** (-403,409 bytes) | Measured (UTF-8 bytes) |
| **Total Lines Read** | 6,972 lines | 2,867 lines | **-58.9%** (-4,105 lines) | Measured (Raw line count) |
| **Tool-Output Bytes (Est.)** | ~667,000 bytes | ~251,000 bytes | **-62.4%** (-416,000 bytes) | Observed (Tool responses) |
| **Total Retrieval Steps** | 18 steps | 13 steps | **-27.8%** (-5 steps) | Measured (Tool calls) |
| **Token Usage** | `UNAVAILABLE` | `UNAVAILABLE` | `UNAVAILABLE` | Platform Token API N/A |
| **Task Correctness** | 100% (4/4) | 100% (4/4) | **Parity (0.0% diff)** | Ground-truth verification |
| **Architectural Adherence** | 100% | 100% | **Parity (0.0% diff)** | Invariant audit (INV-1..8) |
| **Clarification Requests** | 0 | 0 | **Parity (0.0% diff)** | Observed |
| **Stale-Context Incidents** | 0 | 0 | **Parity (0.0% diff)** | Audit against canon |
| **Context Conflicts** | 0 | 0 | **Parity (0.0% diff)** | Audit against canon |

> [!NOTE]
> Across the predefined T1–T4 evaluation traces, Context Architecture v1 was associated with a measured 62.6% reduction in repository bytes read and a 58.9% reduction in lines read. Direct LLM token usage was unavailable, so these results should be interpreted as repository-context retrieval measurements rather than measured token savings.

---

## 2. Task-by-Task Granular Breakdown

### Task T1: Research (Phase 21 Follow-Up Study)
| Dimension | Baseline | Context v1 | Variance | Outcome |
|---|---:|---:|---:|:---:|
| Documents Accessed | 5 | 4 | -20.0% | Measured Retrieval Reduction |
| Bytes Read | 157,896 | 65,272 | **-58.7%** | Measured Retrieval Reduction |
| Lines Read | 1,623 | 822 | **-49.4%** | Measured Retrieval Reduction |
| Irrelevant Documents | 2 | 0 | -100.0% | Precision Gain |
| Correctness | 100% | 100% | 0.0% | Parity |
| Invariant Preservation | 100% | 100% | 0.0% | Parity |

### Task T2: Architecture Review (Relationship Feedback Proposal)
| Dimension | Baseline | Context v1 | Variance | Outcome |
|---|---:|---:|---:|:---:|
| Documents Accessed | 4 | 3 | -25.0% | Measured Retrieval Reduction |
| Bytes Read | 145,052 | 51,471 | **-64.5%** | Measured Retrieval Reduction |
| Lines Read | 1,557 | 672 | **-56.8%** | Measured Retrieval Reduction |
| Irrelevant Documents | 2 | 0 | -100.0% | Precision Gain |
| Correctness | 100% | 100% | 0.0% | Parity |
| Invariant Preservation | 100% | 100% | 0.0% | Parity |

### Task T3: Coding / Dry-Run (HomeostaticEngine Bounds Audit)
| Dimension | Baseline | Context v1 | Variance | Outcome |
|---|---:|---:|---:|:---:|
| Documents Accessed | 5 | 3 | -40.0% | Measured Retrieval Reduction |
| Bytes Read | 164,576 | 36,571 | **-77.8%** | Measured Retrieval Reduction |
| Lines Read | 2,258 | 623 | **-72.4%** | Measured Retrieval Reduction |
| Irrelevant Documents | 3 | 0 | -100.0% | Precision Gain |
| Correctness | 100% | 100% | 0.0% | Parity |
| Invariant Preservation | 100% | 100% | 0.0% | Parity |

### Task T4: Documentation Task (Navigation Alignment)
| Dimension | Baseline | Context v1 | Variance | Outcome |
|---|---:|---:|---:|:---:|
| Documents Accessed | 4 | 3 | -25.0% | Measured Retrieval Reduction |
| Bytes Read | 176,883 | 87,694 | **-50.4%** | Measured Retrieval Reduction |
| Lines Read | 1,534 | 750 | **-51.1%** | Measured Retrieval Reduction |
| Irrelevant Documents | 2 | 0 | -100.0% | Precision Gain |
| Correctness | 100% | 100% | 0.0% | Parity |
| Invariant Preservation | 100% | 100% | 0.0% | Parity |

---

## 3. Statistical Summary of Context Reduction

- **Mean Reduction in Bytes Read**: **-62.8%** (Standard Deviation: $11.3\%$) across evaluated traces.
- **Mean Reduction in Lines Read**: **-57.4%** (Standard Deviation: $10.6\%$) across evaluated traces.
- **Mean Irrelevant Context Reduction**: **-100.0%** (from an average of $2.25$ irrelevant files to $0$).
- **Correctness & Invariant Degradation**: **0.0%** across all tasks.
