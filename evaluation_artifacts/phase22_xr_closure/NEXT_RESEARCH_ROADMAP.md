# NEXT RESEARCH ROADMAP: OBSERVATION LAYER REPLACEMENT STUDY

> **Document Type:** Research Execution Roadmap  
> **Status:** GOVERNANCE APPROVED RESEARCH PLAN  
> **Preceding Phase:** Phase 22-XR (Formally Closed)  
> **Successor Phase:** Observation Layer Replacement Study  
> **Execution Boundary:** Isolated Research Harness Only (`tests/evaluation/phase22_xr_replacement/`)  

---

## 1. Governance Principles & Progression Rules

1. **Strict Research Isolation:** All experimental code, models, adapters, and benchmark scripts remain strictly isolated under `tests/evaluation/` and `evaluation_artifacts/`.
2. **Zero Production Mutation:** No file in `src/core/**`, `electron/**`, `config/**`, or `data/**` may be touched during this study.
3. **Evidence Before Promotion:** No candidate may be proposed for production promotion until all pre-registered criteria in `OBSERVATION_LAYER_REQUIREMENTS.md` are empirically satisfied and reviewed.

---

## 2. Structured 12-Step Research Sequence

```text
Step 1: Freeze XR Evidence & Close Phase 22-XR
        │
        ▼
Step 2: Formalize Observation-Layer Requirements & Acceptance Gates
        │
        ▼
Step 3: Select & Specify Candidate Model Classes (C1–C6)
        │
        ▼
Step 4: Build Modular Candidate Adapters (IObservationEncoder Interface)
        │
        ▼
Step 5: Evaluate Zero-Shot & Fitted Calibration (ECE, Brier, NLL)
        │
        ▼
Step 6: Evaluate Observation-to-Latent Alignment (R², MAE, MSE on z in R^6)
        │
        ▼
Step 7: Evaluate Dynamic Temporal Stability (Flapping, Contradiction Recovery)
        │
        ▼
Step 8: Evaluate Multilingual Robustness (English, Vietnamese, Japanese)
        │
        ▼
Step 9: Measure Exact CPU Latency & Resource Footprint (P50, P95, RAM)
        │
        ▼
Step 10: Benchmark All Candidates Against Real Laya Reference Baseline
        │
        ▼
Step 11: Synthesize Evidence & Determine if Any Candidate Passes All Gates
        │
        ▼
Step 12: Architectural Decision: Production Promotion Design OR Further Research
```

---

## 3. Step-by-Step Task Breakdown

### Phase A: Setup & Adapter Construction (Steps 1–4)
- **Step 1: Freeze XR Evidence (COMPLETED)**
  - Formally seal Phase 22-XR historical records in `evaluation_artifacts/phase22_xr_closure/`.
  - Disentangle hypotheses H1, H2, and H3.
- **Step 2: Formalize Requirements (COMPLETED)**
  - Publish `OBSERVATION_LAYER_REQUIREMENTS.md` establishing frozen gates ($ECE \le 0.10$, $R^2 \ge 0.85$, CPU $P50 \le 50\text{ ms}$, RAM $\le 500\text{ MB}$).
- **Step 3: Select Candidate Classes (COMPLETED)**
  - Publish `OBSERVATION_LAYER_CANDIDATES.md` defining candidate classes C1 through C6.
- **Step 4: Build Modular Candidate Adapters (NEXT)**
  - Implement lightweight adapters conforming to `IObservationEncoder`:
    - C1 Adapter: Small sentence encoder (e.g. MiniLM / BGE).
    - C2 Adapter: Distilled conversational model.
    - C3 Adapter: Acoustic prosody extractor.
    - C4 Adapter: Multimodal text-audio fusion.
    - C5 Adapter: Structured semantic slot extractor.
    - C6 Adapter: Decoupled $g^{-1}$ projection wrapper.

### Phase B: Empirical Evaluation Harness Execution (Steps 5–9)
- **Step 5: Calibration Benchmarking**
  - Run reliability diagram sweeps across validation utterances.
  - Test temperature scaling and isotonic regression where necessary.
- **Step 6: Latent Alignment Evaluation**
  - Evaluate explanatory power against continuous ground truth $\mathbf{z}^* \in \mathbb{R}^6$ in `SimUserEnv-v2`.
  - Compare linear, log-odds, and MLP inverse measurement mappings.
- **Step 7: Temporal Stability Testing**
  - Subject filtered belief to `NoiseSurge`, `LexicalSparsity`, and `ContradictionShock`.
  - Verify belief flapping rate $\le 2.0\%$ and contradiction recovery $\le 1.0\text{ turn}$.
- **Step 8: Multilingual Validation**
  - Execute parallel evaluation across English, Vietnamese, and Japanese dialogue sets.
  - Measure cross-lingual transfer degradation ($\Delta R^2$).
- **Step 9: Resource & Latency Profiling**
  - Measure single-thread and multi-thread CPU latency (P50, P95, P99).
  - Profile peak resident set size (RSS) memory consumption.

### Phase C: Synthesis & Gate Resolution (Steps 10–12)
- **Step 10: Baseline Comparison**
  - Compile the cross-candidate matrix directly against the canonical Real Laya baseline ($ECE = 0.2232$, CPU $P50 = 607.67\text{ ms}$).
- **Step 11: Gate Decision Analysis**
  - Determine whether any candidate class simultaneously satisfies calibration, alignment, stability, latency, and multilingual criteria.
  - If multiple candidates pass, identify trade-offs (e.g., C1 latency vs C4 multimodal richness).
  - If no candidate passes, identify the exact mathematical bottleneck and iterate.
- **Step 12: Architectural Governance Action**
  - Author formal replacement recommendation report.
  - Only if a candidate satisfies 100% of pre-registered criteria, draft an Architecture Gate Proposal for potential future production integration.
  - Production code remains completely untouched until governance sign-off.
