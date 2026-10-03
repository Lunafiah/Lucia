# Real Laya Calibration Report — Phase 22-XR

## 1. Provenance & Execution Mode
- **Execution Mode:** `READY_REAL_MODEL`
- **Model Checkpoint:** `convaiinnovations/laya` (ModernBERT-large 421M params)
- **Checkpoint SHA-256:** `891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c`
- **Device:** `cpu`

## 2. Empirical Calibration Findings
- **Evaluated Test Corpus Items:** 8
- **Empirical Accuracy:** 100.00%
- **Mean Predicted Confidence:** 0.7768
- **Expected Calibration Error (ECE):** **0.2232**
- **Brier Score:** 0.0842

## 3. Analysis & Gate Result (G-XR1)
- **Target:** $ECE \le 0.10$ (Falsification boundary: $> 0.15$)
- **Measured:** **0.2232**
- **Verdict:** **`FAIL (MEASURED REAL MODEL)`**
- **Scientific Finding:** While real Laya demonstrates high zero-shot categorical accuracy (100%), its raw softmax probability distribution displays overconfidence (0.78 vs accuracy), resulting in $ECE = 0.2232$. Downstream integration requires temperature re-scaling or isotonic calibration.
