# Stage 3-C: Compact Structured Realization Contract Evaluation

> **Status**: Completed Evaluation  
> **Target Subsystem**: S11 Realization Input Representation  
> **Model**: `LFM2.5-1.2B-Instruct-Q4_K_M.gguf`  
> **Governance Anchor**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) §0 (Research-First Governance)  
> **Production Code Changes**: NONE (Isolated Evaluation Only)  

---

## Overview

Stage 3-C evaluates whether replacing the current flattened prose-like realization directives (`Condition A`) with a **compact structured realization contract** (`Condition B`, targeting <80 tokens) improves the semantic fidelity of the `LFM2.5-1.2B` SLM realizer.

This study systematically isolates:
1. **Structural benefits** of preserving explicit communicative acts, semantic roles (`:ARG0`, `:ARG1`, `:ARG2`), polarity, epistemic status, and scope (addressing GAP-01 and GAP-05).
2. **Intrinsic realizer limitations** of the 1.2B SLM identified in Stage 3-B.

---

## Directory Structure

```text
tests/evaluation/language_realization/compact_structured_contract/
├── harness/
│   └── test_contract.py            # Token budget unit tests (<80 tokens verification)
├── protocol.md                     # Formal evaluation protocol and hypotheses
├── README.md                       # Study overview and execution guide
├── run_evaluation.py               # Master execution script (A/B paired runner)
├── raw_observations.jsonl          # Raw generation outputs and latencies per fixture
├── paired_comparison.jsonl         # Detailed fixture-by-fixture comparison of A vs B
├── annotation_sheet.jsonl          # Double annotation records for semantic violations
├── metrics.json                    # Aggregated metrics, contingency counts, and verdict
└── FINAL_REPORT.md                 # Complete evaluation report with findings & decision
```

---

## Reproduction Instructions

To reproduce the evaluation in an isolated environment:

```powershell
# Ensure virtual environment is activated with CUDA-enabled llama-cpp-python
.\.venv\Scripts\python.exe tests/evaluation/language_realization/compact_structured_contract/run_evaluation.py
```

Results and metrics will be updated deterministically in `metrics.json` and `FINAL_REPORT.md`.
