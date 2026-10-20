# Lucia — Experimental Harness: Endogenous Communication & Reason-to-Communicate

## Overview

This directory contains the documentation, formal specification, experimental results, and falsification analysis for the **Endogenous Communication & Reason-to-Communicate** experimental harness.

The investigation evaluates whether Lucia has a causal gap between continuous endogenous cognitive state and communicative action, and determines whether an explicit **Typed Candidate + Grounding + Authorization** architecture provides a principled, inspectable computational bridge over the existing user-driven CAPS pipeline.

> [!IMPORTANT]
> **RESEARCH HARNESS ONLY — STRICT PRODUCTION SAFETY**:
> This experiment is 100% offline and isolated. No changes have been made to production `src/core`, UI/Electron runtime, P23/P23-D frozen baselines, Genesis invariants, or live conversational behavior.

---

## Documents in this Package

1. [EXPERIMENT_SPEC.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/EXPERIMENT_SPEC.md) — Formal hypotheses (H1–H5), independent Oracle definitions, fixture specifications (Tests A–H), and metric definitions.
2. [ARCHITECTURE.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/ARCHITECTURE.md) — Detailed architecture of the evaluated bridge (`State` $\to$ `GroundedReason` $\to$ `CommunicativeCandidate` $\to$ `AuthorizationArbiter`), comparison against B0 and B2, and concurrency/safety models.
3. [RESULTS.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/RESULTS.md) — Comprehensive empirical results across Baselines B0, B1, B2, and all four ablations, including metric tables, Test C multi-turn traces, and performance benchmarks.
4. [FALSIFICATION.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/FALSIFICATION.md) — Stress testing, ablation breakdowns, failure traces, falsification verdict, and architectural recommendation.
5. [telemetry.json](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/telemetry.json) — Full machine-readable test run telemetry and decision traces.

---

## Quick Summary of Findings

| Metric | B0 (Current CAPS) | B1 (Candidate + Auth) | B2 (Candidate + Consequence) | B1 (No Grounding) | B1 (No Authorization) |
|---|---|---|---|---|---|
| **Endogenous Causal Sensitivity** | `0.000` | `1.000` | `1.000` | `0.333` | `1.000` |
| **Grounding Coverage** | `0.000` | `1.000` | `1.000` | `0.800` | `1.000` |
| **Unsupported Initiation Rate** | `0.000` | `0.000` | `0.000` | **`1.000` (FAIL)** | `0.000` |
| **Authorization Correctness** | `0.000` | `1.000` | `1.000` | `0.000` | **`0.333` (FAIL)** |
| **User-Task Fidelity** | `1.000` | `1.000` | `1.000` | `1.000` | **`0.500` (FAIL)** |
| **Self-Loop Rate** | `0.000` | `0.000` | `0.000` | `0.000` | **`1.000` (FAIL)** |
| **Average Latency** | `0.002 ms` | `0.024 ms` | `0.027 ms` | `0.011 ms` | `0.010 ms` |

### Key Experimental Discoveries
1. **Current CAPS is causally blind to internal state**: In B0, identical user inputs across vastly different cognitive states (warmth, resting baseline, epistemic contradiction, rupture tension) produce identical communicative intents (`GREET`). Internal state has zero causal impact on communicative planning.
2. **Grounding is non-negotiable**: Removing explicit grounds (`B1_NoGrounding`) causes the system to immediately over-trigger and invent communicative utterances from raw somatic tension/affect alone (failing Test G).
3. **Authorization cannot be skipped**: Bypassing authorization (`B1_NoAuthorization`) causes endogenous thoughts to hijack user query turns (violating user-task fidelity) and trigger runaway self-loops.
4. **Consequence Evaluator (B2) offers negligible marginal benefit**: B1's explicit typed candidate arbitration already satisfies 100% of the independent oracle criteria at lower conceptual complexity than B2.

---

## Reproducing the Experiment

To re-run the entire evaluation suite and generate fresh telemetry:

```bash
# Execute standalone experiment runner
.venv/Scripts/python.exe tests/evaluation/endogenous_communication/run_experiments.py

# Run automated pytest verification
.venv/Scripts/python.exe -m pytest tests/evaluation/test_endogenous_communication.py -v
```
