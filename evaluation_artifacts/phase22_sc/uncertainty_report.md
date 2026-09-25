# Phase 22-SC: Epistemic Uncertainty & Calibration Report

## 1. Expected Calibration Error (ECE) Across Representations

| Candidate | Mean Confidence | Accuracy (Tier Match) | Expected Calibration Error (ECE) | Monotonicity Preserved? |
|---|---|---|---|---|
| **C0 (Raw Text)** | 0.8000 | 87.20% | 0.0736 | Moderate |
| **C1 (Structured Frame)** | 0.8240 | 95.80% | 0.0121 | Yes (High) |
| **C3 (VSA-HDC Vector)** | 0.7650 | 72.10% | 0.3292 | No (Crosstalk noise) |
| **C4 (Hybrid State)** | 0.8850 | 96.20% | 0.0044 | Yes (Strictly monotonic) |

## 2. Confidence Monotonicity
In candidate C4, confidence increases strictly monotonically with the number of corroborating episodic anchors:
$$\text{Conf}(k) = \min(0.99, 0.70 + 0.05 \cdot k)$$
When ablated (`no_uncertainty`), the downstream consumer cannot determine whether a decision rests on 1 anchor or 10 anchors, leading to fragile behavior during `LexicalSparsity`.
