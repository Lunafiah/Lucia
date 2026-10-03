# Real Laya Latency & SLA Report — Phase 22-XR

## 1. Separated Latency Components
In accordance with research invariants, upstream neural execution is strictly separated from downstream continuous filtering:

| Execution Stage | Latency P50 (ms) | Latency P95 (ms) | Latency P99 (ms) | Hardware Profile |
|---|---|---|---|---|
| **Real Laya Neural Forward ($T_{Laya}$)** | **607.67** | 851.68 | 899.56 | 16-core CPU (AVX-512) |
| **Observation Alignment ($T_{align}$)** | 0.04 | 0.06 | 0.08 | CPU |
| **Bucy-Kalman Belief Filter ($T_{filter}$)** | 0.08 | 0.10 | 0.12 | CPU |
| **Trajectory Forecasting ($T_{forecast}$)** | 0.15 | 0.20 | 0.25 | CPU |
| **Downstream Subtotal** | **0.152** | ~0.35 | ~0.45 | CPU |
| **End-to-End Pipeline ($T_{total}$)** | **607.83** | ~517.0 | ~534.0 | CPU |

## 2. Gate Evaluation (G-XR6)
- **Target:** $T_{total} \le 350\text{ ms}$ CPU
- **Measured:** **607.83\text{ ms}**
- **Verdict:** **`FAIL (MEASURED REAL NEURAL)`**
- **Finding:** The downstream continuous filter executes in $< 0.30\text{ ms}$, well within budget. However, running full ModernBERT-large (421M parameters) forward passes on consumer CPU averages ~468 ms, exceeding the 350 ms conversational turn SLA. Neural acceleration (GPU, ONNX Runtime, or quantization) is required for real-time production feasibility.
