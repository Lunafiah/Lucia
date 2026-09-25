# Results E4: Prospective Intent Prediction

> **Experiment**: E4 — Prospective Intent Prediction  
> **Evaluated Hypothesis**: Latent belief predicts prospective next-turn intent with Top-1 $\ge 70\%$ and Top-2 $\ge 90\%$.  

---

## 1. Quantitative Results ($N=50$ episodes, $T=40$ turns)

- **Prior Baseline (B0) Top-1 Accuracy**: $32.15\%$
- **Prospective Model Top-1 Accuracy**: **$34.15\%$** (Marginal $+2.0\%$ improvement)
- **Prospective Model Top-2 Recall**: **$52.51\%$**
- **Intent Probability Calibration Error (ECE)**: **$0.0235$** (Excellent probability calibration)
- **Intent Brier Score**: $0.7871$

---

## 2. Findings & Architectural Implications

1. **Information Horizon Bottleneck**:
   - Predicting user communicative intent *strictly before* the user speaks is inherently stochastic across an 8-class intent space.
   - The prospective intent accuracy ($34.15\%$) barely exceeded the marginal prior ($32.15\%$), failing the $\ge 70\%$ pre-registered target.
2. **Calibration vs. Discrimination**:
   - While calibration was strong ($\text{ECE} = 0.0235$), discriminative sharpness was insufficient without lexical context from the current turn.
3. **Gate G4 Assessment**:
   - Top-1 ($34.15\% \ll 70.0\%$) and Top-2 ($52.51\% \ll 90.0\%$) criteria failed.
   - Status: **FAIL**. A non-generative, state-conditioned Markov transition model cannot reliably predict fine-grained intent prior to turn revelation.
