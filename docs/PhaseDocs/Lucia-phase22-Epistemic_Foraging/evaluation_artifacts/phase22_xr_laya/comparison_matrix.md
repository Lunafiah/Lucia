# Real Laya Verification Comparison Matrix

| Dimension | Previous P22-XR Baseline | Follow-Up Synthetic Surrogate | Real Laya Neural Backbone | Provenance Status |
|---|---|---|---|---|
| **Backbone Identity** | Fallback Emulation | Synthetic Calibrated Probes | ModernBERT-large (421M) | `BLOCKED_OFFLINE_WEIGHTS` |
| **Observation ECE** | 0.3349 (Degraded) | 0.0450 (Calibrated) | `BLOCKED` | `BLOCKED_OFFLINE_WEIGHTS` |
| **Latent Alignment ($R^2$)** | -34.88 (Coordinate Mismatch) | +0.4026 (M2 Aligned) | `BLOCKED` | `BLOCKED_OFFLINE_WEIGHTS` |
| **H=2 Trajectory Coverage** | 44.8% (Under-dispersed) | 100.0% (Lyapunov Diffusion) | `BLOCKED` (Real) / 100% (Surrogate) | Downstream Validated |
| **Inference Latency P50** | 0.12 ms (Emulator) | 0.03 ms (Mapping) | `BLOCKED` | `BLOCKED_OFFLINE_WEIGHTS` |
