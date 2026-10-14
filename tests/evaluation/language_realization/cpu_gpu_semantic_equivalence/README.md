# Lucia — Stage 3-B: CPU vs GPU Semantic Equivalence Study

> **Isolated Evaluation Suite**  
> **Target Subsystem**: Language Realization Substrate (`LLMBackend` on CPU vs CUDA GPU)  
> **Status**: COMPLETED / ISOLATED EVALUATION  

---

## Overview

This directory contains the study design, paired execution harness, raw paired observations, double-annotation sheets, contingency matrices, and practical equivalence analysis for **Stage 3-B: CPU vs GPU Semantic Equivalence Study**.

The study determines whether the **59.5% critical semantic error rate** observed in Stage 3-A is a hardware-specific artifact (CPU divergence / GPU degradation), backend variance, or an intrinsic, backend-neutral limitation of the `LFM2.5-1.2B` realizer model.

---

## Directory Structure

```text
tests/evaluation/language_realization/cpu_gpu_semantic_equivalence/
├── README.md                           # This navigation guide
├── protocol.md                         # Formal paired protocol & TOST equivalence criteria
├── run_study.py                        # Master paired CPU vs GPU execution driver
├── raw_observations.jsonl              # Raw paired completions & latency observations
├── paired_comparison.jsonl             # Fixture-by-fixture divergence, text similarity & diffs
├── annotation_sheet.jsonl              # Independent double-annotation records for CPU and GPU
├── metrics.json                        # Full paired metrics, McNemar matrix & TOST confidence intervals
└── FINAL_REPORT.md                     # Consolidated Stage 3-B Research Report
```

---

## Reproducing the Study

To re-run the entire paired CPU vs GPU evaluation:

```powershell
.\.venv\Scripts\python.exe tests/evaluation/language_realization/cpu_gpu_semantic_equivalence/run_study.py
```
