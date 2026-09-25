# Results E1: Observation Calibration

> **Experiment**: E1 — Observation Calibration & Uncertainty under Distribution Shift  
> **Evaluated Hypothesis**: Non-generative decision primitive achieves $\text{ECE} \le 0.05$ on in-distribution test and $\le 0.12$ on distribution shift.  

---

## 1. Quantitative Results

### 1.1 In-Distribution Benchmark ($N=5,000$)
- **B0 (Majority Prior)**: $\text{ECE} = 0.0284$, $\text{Brier} = 0.7760$, $\text{NLL} = 1.5407$, Accuracy = $29.12\%$
- **B1 (Calibrated MLP)**: $\text{ECE} = 0.2219$, $\text{Brier} = 0.4611$, $\text{NLL} = 2.7187$, Accuracy = $75.08\%$
- **B4 (Jev/Laya Surrogate)**: $\text{ECE} = \mathbf{0.0149}$, $\text{Brier} = \mathbf{0.2789}$, $\text{NLL} = \mathbf{0.4873}$, Accuracy = $\mathbf{80.36\%}$

### 1.2 Distribution Shift Regimes ($N=3,000$ each)
- **DS-1 (Noise Surge $\sigma=0.50$)**:
  - B1: $\text{ECE} = 0.4729$, Accuracy = $50.50\%$
  - B4: $\text{ECE} = 0.3077$, Accuracy = $46.97\%$ (Degraded due to extreme observation variance)
- **DS-2 (Dynamics Shift)**:
  - B1: $\text{ECE} = 0.2754$, Accuracy = $69.60\%$
  - B4: $\text{ECE} = \mathbf{0.0176}$, Accuracy = $\mathbf{77.80\%}$
- **DS-3 (Contradiction Shift)**:
  - B1: $\text{ECE} = 0.2205$, Accuracy = $75.23\%$
  - B4: $\text{ECE} = \mathbf{0.0196}$, Accuracy = $\mathbf{79.87\%}$
- **DS-4 (Sparse/Silent Input)**:
  - B1: $\text{ECE} = 0.7672$, Accuracy = $19.40\%$
  - B4: $\text{ECE} = 0.5994$, Accuracy = $20.40\%$
- **DS-5 (Intent Co-occurrence)**:
  - B1: $\text{ECE} = 0.2290$, Accuracy = $74.60\%$
  - B4: $\text{ECE} = \mathbf{0.0203}$, Accuracy = $\mathbf{79.57\%}$

---

## 2. Findings & Architectural Implications

1. **Jev/Laya Surrogate Superiority in In-Distribution & Structured Shift**:
   - The dual-head GELU-norm architecture in B4 preserved calibration ($\text{ECE} < 0.021$) across DS-2, DS-3, and DS-5, significantly outperforming simple temperature-scaled linear heads (B1 $\text{ECE} \approx 0.22–0.27$).
2. **Failure under Extreme Noise & Lexical Sparsity (DS-1 & DS-4)**:
   - When inputs lacked informative lexical features (DS-4) or noise overwhelmed the feature distributions (DS-1), calibration broke down ($\text{ECE} > 0.30$).
3. **Gate G1 Assessment**:
   - In-distribution criterion ($\text{ECE} \le 0.05$) is **PASSED** by B4 ($\text{ECE} = 0.0149$).
   - Distribution shift criterion ($\text{ECE} \le 0.12$) is **PARTIALLY PASSED** (passed on DS-2, DS-3, DS-5; failed on extreme out-of-distribution noise DS-1/DS-4).
