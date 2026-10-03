# OBSERVATION LAYER EVALUATION PLAN: BENCHMARK PROTOCOL & TEST SUITE

> **Document Type:** Experimental Evaluation Protocol  
> **Status:** PRE-REGISTERED & FROZEN  
> **Target:** Observation Layer Replacement Study  
> **Harness Reuse:** `SimUserEnv-v2` Evaluation Environment  

---

## 1. Experimental Methodology & Non-Negotiable Governance

To guarantee scientific rigor, prevent p-hacking, and eliminate retroactive threshold manipulation, this evaluation plan is **frozen prior to candidate evaluation**.

### Core Experimental Rules:
1. **Protocol Frozen Before Execution:** No metric thresholds or scenario parameters may be altered after viewing candidate results.
2. **Reuse Existing Synthetic Simulator:** All trials will utilize the deterministic, validated `SimUserEnv-v2` environment established in Phase 22-XR. No synthetic generator may be customized to favor any candidate.
3. **CPU Execution on Reference Baseline:** All latency and throughput measurements must be taken under single-process CPU execution (matching Lucia's 20-Watt edge constraint).
4. **Disentangled Evaluation:** Calibration, Alignment, Temporal Stability, Latency, and Multilingual Robustness must be evaluated independently.

---

## 2. Benchmark Scenarios (`SimUserEnv-v2`)

Each candidate architecture will be evaluated across six standardized conversational stress scenarios:

```text
+-------------------+-------------------------------------------------------------+
| Scenario          | Operational Stress Condition                                |
+-------------------+-------------------------------------------------------------+
| ID                | Standard in-distribution dialogue turns; steady dynamics   |
| NoiseSurge        | Sudden injection of lexical noise, typos, and acoustic jitter|
| LexicalSparsity   | Ultra-short turns ("yes", "...", "maybe", single tokens)   |
| ContradictionShock| Sharp 180-degree polarity reversal in user intent/valence   |
| TemporalDrift     | Long multi-turn conversation with gradual parameter drift  |
| CombinedStress    | Simultaneous noise, sparsity, and rapid shifts              |
+-------------------+-------------------------------------------------------------+
```

### Scenario Specifications:
1. **ID (In-Distribution):**
   - 50 conversational sessions, 20 turns each.
   - Ground truth user state evolves via Ornstein-Uhlenbeck (OU) process with mean reversion $\theta = 0.15$ and process noise $\sigma = 0.10$.
2. **NoiseSurge:**
   - 20 sessions, 20 turns each.
   - Observation noise $\mathbf{R}$ artificially inflated by $5.0\times$ between turns 8 and 14.
   - Evaluates filter rejection of unreliable observations.
3. **LexicalSparsity:**
   - 20 sessions. Utterance length truncated to $1-3$ tokens.
   - Evaluates whether candidate encoders extract meaningful semantic signal from minimal surface text.
4. **ContradictionShock:**
   - 20 sessions. At turn 10, true user state flips sign ($\mathbf{z}^* \to -\mathbf{z}^*$).
   - Evaluates contradiction recovery speed (turns to re-align).
5. **TemporalDrift:**
   - 10 long sessions (100 turns each).
   - Slow sinusoidal drift of relational parameters.
   - Evaluates accumulation of filter error or drift instability over time.
6. **CombinedStress:**
   - 20 sessions subjecting the model to simultaneous noise surges, sparsity, and polarity shocks.

---

## 3. Evaluation Dimensions & Mathematical Metrics

For every candidate, the harness will log:

### 3.1 Calibration Evaluation
- **Expected Calibration Error ($ECE$):**
  $$ECE = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$
  using $M=10$ bins.
- **Brier Score:**
  $$\text{Brier} = \frac{1}{N} \sum_{i=1}^N \|\mathbf{y}_i - \mathbf{y}^*_i\|_2^2$$
- **NLL (Negative Log-Likelihood):** Monitored across all validation turns.

### 3.2 Alignment Evaluation
- **Coefficient of Determination ($R^2$):**
  $$R^2 = 1 - \frac{\sum_i \|\mathbf{z}_i^* - \hat{\mathbf{z}}_i\|^2}{\sum_i \|\mathbf{z}_i^* - \bar{\mathbf{z}}^*\|^2}$$
- **Mean Absolute Error ($MAE$):**
  $$MAE = \frac{1}{6N} \sum_{i=1}^N \sum_{d=1}^6 |z_{i,d}^* - \hat{z}_{i,d}|$$
- **Mean Squared Error ($MSE$):**
  $$MSE = \frac{1}{6N} \sum_{i=1}^N \sum_{d=1}^6 (z_{i,d}^* - \hat{z}_{i,d})^2$$

### 3.3 Temporal Stability & Dynamics
- **Continuous Belief Flapping Rate:**
  Fraction of consecutive turns ($t, t+1, t+2$) where sign changes or direction reverses without corresponding ground truth change.
- **Contradiction Recovery Time:**
  Turns required for $\|\hat{\mathbf{z}}_t - \mathbf{z}_t^*\| \le 0.35$ following a shock.
- **Covariance Log-Determinant Ratio:**
  $$\rho_{\det} = \frac{\log \det \boldsymbol{\Sigma}_{\text{pred}}}{\log \det \boldsymbol{\Sigma}_{\text{prior}}}$$
  Verifies that uncertainty neither collapses to zero nor explodes to infinity.

### 3.4 Latency & Computational Cost
- **Encoder Inference Time ($T_{\text{obs}}$):** P50, P95, P99 on CPU (measured via high-resolution wall-clock timer).
- **Continuous Filter Update Time ($T_{\text{filter}}$):** Time spent in continuous prior integration and Kalman update.
- **Peak Memory Usage:** Working set RAM allocated during inference pass.

### 3.5 Multilingual Benchmark
- Test identical scenarios across parallel corpora in:
  1. English (EN)
  2. Vietnamese (VI)
  3. Japanese (JA)
- Measure cross-lingual transfer degradation:
  $$\Delta R^2_{\text{VI}} = R^2_{\text{EN}} - R^2_{\text{VI}}, \quad \Delta R^2_{\text{JA}} = R^2_{\text{EN}} - R^2_{\text{JA}}$$

---

## 4. Candidate Execution Pipeline in Harness

```text
For each Candidate C_k in {C1, C2, C3, C4, C5, C6}:
  1. Instantiate Candidate Adapter conforming to IObservationEncoder.
  2. Warm up model on CPU (5 dummy passes).
  3. For each Scenario S in {ID, NoiseSurge, LexicalSparsity, ContradictionShock, Drift, Combined}:
       - Run SimUserEnv-v2 for N sessions.
       - Measure per-turn:
           * y_raw, y_calibrated, R_matrix
           * Inference latency (high-res timer)
           * Filter update latency
           * Continuous state estimate z_hat and covariance Sigma
           * Ground truth z*
  4. Compute global aggregated metrics:
       * ECE, Brier, NLL
       * R^2, MAE, MSE
       * Flapping rate, Recovery turns
       * P50, P95, P99 CPU latency
       * Multilingual transfer ratios
  5. Emit standardized evaluation record:
       evaluation_artifacts/phase22_xr_replacement/candidate_eval_C{k}.json
```

---

## 5. Output Deliverables of the Study

Upon executing this evaluation plan, the study will produce:
1. `candidate_comparison_matrix.json` (Numerical ledger across all C1–C6 candidates).
2. `latency_profiling_report.md` (Detailed CPU flamegraphs and timing percentiles).
3. `multilingual_robustness_report.md` (Cross-lingual transfer validation).
4. `replacement_study_recommendation.md` (Formal evidence synthesis recommending whether any candidate warrants architecture approval).
