# Calibration Report — Phase 22-XR-L

## 1. Status: BLOCKED_OFFLINE_WEIGHTS

Neural backbone evaluation for `convaiinnovations/laya` cannot be computed because **real neural weights (`model.safetensors`, 421M ModernBERT-large) are absent from local storage and HF cache**.

In accordance with strict Lucia research invariants:
- **No synthetic emulation** was substituted.
- **No cloud inference** was performed.
- Real Laya calibration (ECE, Brier, NLL) remains **BLOCKED** rather than fabricated.

## 2. Preregistered Calibration Gate (G-XRL1)

- **Target**: $ECE_{shift} \le 0.10$
- **Falsification Boundary**: $ECE_{shift} > 0.15$
- **Result**: `BLOCKED_OFFLINE_WEIGHTS`
