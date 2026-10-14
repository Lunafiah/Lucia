# Lucia — Stage 3-A: SemanticGraph Preservation Audit

> **Isolated Evaluation Suite**  
> **Target Subsystem**: Stage S10b (CAPS) $\longrightarrow$ Stage S11 (PromptAssembler) $\longrightarrow$ Stage S13 (LLMBackend Realization)  
> **Status**: COMPLETED / ISOLATED EVALUATION  

---

## Overview

This directory contains the complete specification, execution harness, raw observations, structural comparisons, double-annotation records, and adjudicated findings for the **Stage 3-A SemanticGraph Preservation Audit**.

The audit evaluates **GAP-01** (Lossy SemanticGraph serialization across the realization boundary) by measuring what structural semantic information survives serialization from `CAPSResult` into the prompt, what the realizer (`LFM2.5-1.2B`) emits, and whether true semantic loss occurs.

---

## Directory Structure

```text
tests/evaluation/language_realization/semantic_graph_preservation/
├── README.md                           # This navigation guide
├── protocol.md                         # Formal audit methodology, taxonomy & criteria
├── run_audit.py                        # Master reproducible execution script
├── fixtures/
│   └── audit_fixtures.json             # Authoritative 42-fixture corpus (EN, VI, JA)
├── harness/
│   ├── fixtures_generator.py           # Corpus generation & UMR-TPG graph builder
│   ├── evaluator.py                    # Level 1, 2, 3 structural & semantic evaluators
│   └── double_annotator.py             # Independent double annotation & adjudication
├── raw_observations.jsonl              # Raw realizer completions & timing observations
├── structural_comparison.jsonl         # Level 1 deterministic graph-to-prompt serialization trace
├── annotation_sheet.jsonl              # Independent Annotator A & Annotator B raw judgments
├── adjudicated_results.jsonl           # Consensus adjudicated findings with rationale
├── metrics.json                        # Comprehensive multi-dimensional cross-tabulated metrics
└── FINAL_REPORT.md                     # Consolidated Stage 3-A Evaluation Report
```

---

## Reproducing the Audit

To execute the entire audit from scratch under the isolated virtual environment:

```powershell
.\.venv\Scripts\python.exe tests/evaluation/language_realization/semantic_graph_preservation/run_audit.py
```

All observations, structural diffs, annotations, metrics, and reports will be recomputed and verified.
