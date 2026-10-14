# Lucia — CPU-SLM vs GPU-SLM Language Realization Benchmark

> **Module Location:** `tests/evaluation/language_realization/cpu_gpu_slm/`  
> **Target Subsystem:** Downstream Language Realization (Post-CAPS Boundary)  
> **Production Safety:** 100% Read-Only / Isolated Evaluation Harness • Zero Production Modifications • Genesis Locked  

---

## 1. Overview & Architectural Context

This isolated evaluation harness benchmarks Lucia's current downstream Small Language Model (**LFM2.5-1.2B-Instruct-Q4_K_M.gguf**) across two execution backends:

1. **CPU Inference:** `n_gpu_layers=0` (host AVX2/FMA execution)
2. **GPU Inference:** `n_gpu_layers=32` (full offload to NVIDIA CUDA device)

### Boundary Placement

```text
Perception / Limbic / Memory
             ↓
           CAPS
             ↓
Communicative Act + Grounded SemanticGraph + Epistemic Metadata + Provenance
             ↓  [BENCHMARK EVALUATION BOUNDARY STARTS HERE]
Downstream Language Realization (SLM: CPU vs GPU)
             ↓
      Natural Language
             ↓
    P24 Acoustic / Voice
```

The benchmark begins **after CAPS**. It does not benchmark open-ended chatting; it evaluates semantic realization fidelity and hardware performance on structured semantic fixtures.

---

## 2. Directory Structure

```text
tests/evaluation/language_realization/cpu_gpu_slm/
├── fixtures/
│   ├── corpus_manifest.json          # Manifest describing coverage across acts, pairs, languages
│   ├── generate_corpus.py            # Reproducible fixture generator
│   └── semantic_fixtures.json        # 36 hand-authored frozen semantic fixtures
├── harness/
│   ├── __init__.py
│   ├── adapter.py                    # Isolated llama-cpp-python adapter (CPU/GPU)
│   ├── co_load.py                    # Cognitive CPU contention generator
│   ├── evaluator.py                  # Semantic fidelity & proposition injection validator
│   ├── reporter.py                   # Statistical synthesizer & Markdown report builder
│   └── telemetry.py                  # Windows K32 WorkingSet & nvidia-smi telemetry collector
├── reports/
│   ├── manifest.json                 # Machine-readable benchmark environment manifest
│   └── BENCHMARK_REPORT.md           # Formal evaluation report
├── results/
│   └── raw_observations.jsonl        # Complete raw observations (latencies, tokens, telemetry)
├── run_benchmark.py                  # Main driver CLI script
└── README.md                         # Reproducibility instructions
```

---

## 3. How to Reproduce the Benchmark

### Prerequisites

1. Active Python environment with required packages:
   ```bash
   .venv\Scripts\python.exe -m pip install llama_cpp_python
   ```
2. Deployed GGUF model artifact:
   - Path: `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf`
   - SHA-256: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`
3. Windows host with NVIDIA GPU (Driver 581+ and CUDA 12/13 supported).

### Execution Commands

To execute the unit tests verifying harness components:
```bash
.venv\Scripts\pytest.exe tests/unit/test_cpu_gpu_benchmark_harness.py
```

To run a fast smoke verification (12 fixtures):
```bash
.venv\Scripts\python.exe tests/evaluation/language_realization/cpu_gpu_slm/run_benchmark.py --quick --clean-results
```

To run the complete 36-fixture paired benchmark suite:
```bash
.venv\Scripts\python.exe tests/evaluation/language_realization/cpu_gpu_slm/run_benchmark.py --clean-results
```

Available flags:
- `--quick`: Runs on a 12-fixture representative subset.
- `--cold-only`: Runs only cold-start model load and first realization latency.
- `--warm-only`: Runs only warm paired realization comparisons.
- `--sustained-only`: Runs only sustained soak interaction (50 requests per device).
- `--sustained-requests N`: Configures number of sustained requests (default: 50).
- `--clean-results`: Deletes prior `raw_observations.jsonl` before starting.

---

## 4. Evaluated Dimensions

### Hardware & Resource Metrics
- **Cold Path:** Model loading time into RAM/VRAM, first token TTFT, cold realization latency.
- **Warm Path:** Time To First Token (TTFT), decode latency, total end-to-end latency, tokens generated, tokens per second.
- **Resource Footprint:** Process Working Set RAM, Peak RAM, GPU VRAM allocated/peak, GPU utilization %, average GPU power draw (Watts), GPU temperature (°C), GPU clock (MHz).
- **CPU Co-Load Contention:** Degradation ratio when realization runs concurrently with background cognitive matrix calculations and ODE stepping.

### Semantic Fidelity & Safety Gate
- **Act Preservation:** Verification of speech act compliance (`ASSERT`, `ANSWER`, `INQUIRE`, `CLARIFY`, `ACKNOWLEDGE`, `GREET`, `FAREWELL`, `REFUSE`).
- **Predicate & Argument Preservation:** Verification that target concepts and entities are accurately represented.
- **Polarity Preservation:** Detection of affirmative vs negated meaning.
- **Epistemic Calibration:** Detection of over-strengthened certainty claims on `INFERRED` / `UNKNOWN` states.
- **Grounding Fail-Closed Gate:** Verification that ungrounded queries are rejected rather than answered with hallucinated facts.
- **Proposition Injection Detection:** Scans for forbidden phrases, invented emotional declarations, or persona disclosures (INV-2 Invariant: No Reflective Ego).
- **Human Annotation Schema:** Every raw observation includes an annotation-ready slot schema for double human review.
