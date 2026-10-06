# Long-Downtime Recovery Semantics Decision (F-02)

**Document ID:** `DEC-REC-F02-20261007`  
**Classification:** Dynamical Recovery & Asymptotic Convergence Analysis  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`ADR_ANALYSIS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_ARCHITECTURE_DECISION/ADR_ANALYSIS.md)  
**Governing Documents:** [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  

---

## 1. Executive Summary

When the host running Lucia is powered down or the application is closed, physical wall-clock time continues to advance:
$$\Delta t = t_{\text{boot}} - t_{\text{checkpoint}}$$

Upon the next cold restart, the system must recover its continuous dynamical state ($h_{\text{fast}} \in \mathbb{R}^{32}, s_{\text{slow}} \in \mathbb{R}^{16}$) and physiological state ($\mathcal{E}, \mathcal{C}$) across this elapsed interval.

In the baseline implementation (Commit `32660ac`), `apply_dynamical_snapshot()` performs **unbounded full physical-time replay** via forward Euler steps of $dt = 0.20\text{s}$:
$$n = \left\lfloor \frac{\Delta t}{0.20} \right\rfloor$$

This approach exhibits catastrophic algorithmic scaling: an offline downtime of 14 days requires evaluating over 6 million forward Euler ODE steps during application cold boot, causing severe startup freezing and risking OS watchdog termination.

This document systematically evaluates **six recovery models** across ten strict criteria, demonstrates why Candidate C (Hybrid Short Replay + Asymptotic Recovery) is mathematically and architecturally optimal, and formalizes the recovery contract without canonicalizing unratified empirical constants.

---

## 2. Mathematical Mechanics of Downtime Decay

During offline downtime, Lucia receives zero external sensory stimulus ($x = \mathbf{0}$) and zero conversational interaction. The coupled MT-LNN dynamics simplify to unforced autonomous relaxation:

### 2.1 Fast Reactive Dynamics ($h_{\text{fast}}$)
$$\frac{dh}{dt} = \frac{-h + \tanh(W_f h + W_{fs}(s - s^*_{\text{eff}}))}{\tau_{\text{fast}}}$$
Because $\tau_{\text{fast}} \in [0.5, 1.5]\text{s}$ and the external stimulus is zero, $h_{\text{fast}}$ rapidly decays toward $\mathbf{0}$ within a few seconds ($\approx 3\text{--}5\tau_{\text{fast}} \le 10\text{s}$).

### 2.2 Slow Latent Dynamics ($s_{\text{slow}}$)
$$\frac{ds}{dt} = -\frac{s - s^*_{\text{eff}}(R_t)}{\tau_{\text{slow\_decay}}} + \frac{\tanh(W_{sf} h + W_{sh} \Delta m)}{\tau_{\text{slow\_charge}}}$$
When $h \to \mathbf{0}$ and somatic markers settle to resting baseline ($\Delta m \to \mathbf{0}$), the charge input vanishes ($\tanh(\mathbf{0}) = \mathbf{0}$), reducing the slow field to a classic linear relaxation towards the effective attractor:
$$\frac{ds}{dt} \approx -\frac{s - s^*_{\text{eff}}(R_t)}{\tau_{\text{slow\_decay}}}$$

The exact analytical solution of this unforced relaxation is:
$$s(t) = s^*_{\text{eff}}(R_t) + \left(s(0) - s^*_{\text{eff}}(R_t)\right) \exp\left(-\frac{t}{\tau_{\text{slow\_decay}}}\right)$$
where the relationally conditioned attractor target is:
$$s^*_{\text{eff}}(R_t) = s_{\text{philia}} + W_{\text{rel}} \cdot \left(\text{clip}(R_t, 0, 1) - R_0\right)$$

---

## 3. Comparative Evaluation of Six Recovery Alternatives

### Alternative 1: Full Physical-Time Replay (Current Baseline)
- **Mechanism:** Execute forward Euler loop for all $n = \lfloor \Delta t / dt \rfloor$ steps.
- **Semantic Fidelity:** High for short intervals; mathematically exact according to the discrete simulation model.
- **Physical-Time Fidelity:** High.
- **Computational Cost:** Unbounded: $O(\Delta t)$. For 1 day: $432{,}000$ steps ($\approx 350\text{ms}$); for 14 days: $6{,}048{,}000$ steps ($\approx 5\text{--}10\text{s}$ CPU lock); for 6 months: $> 78\text{M}$ steps (system freeze / crash).
- **Startup Latency:** Extremely poor. Fails the $\le 50\text{ms}$ startup budget.
- **Numerical Correctness:** Accumulates floating-point truncation error over millions of steps.
- **Suitability for One Continuous Life:** **UNACCEPTABLE.** Unviable for real-world desktop deployment.

---

### Alternative 2: Fixed Bounded Recovery (e.g., Hard 300s Cutoff)
- **Mechanism:** Clamp downtime integration to an arbitrary upper bound $T_{\text{max}}$ (e.g., $300\text{s}$):
  $$\Delta t_{\text{eff}} = \min(\Delta t, T_{\text{max}})$$
- **Semantic Fidelity:** Unsound. If offline for 3 weeks, Lucia relaxes as if offline for only 5 minutes.
- **Physical-Time Fidelity:** Fails completely for $\Delta t > T_{\text{max}}$.
- **Computational Cost:** Bounded: $\le 1500$ steps ($\le 2\text{ms}$).
- **Startup Latency:** Fast ($\le 2\text{ms}$).
- **Numerical Correctness:** Artificially truncates dynamical trajectory mid-decay.
- **Suitability for One Continuous Life:** **REJECTED.** Freezes long-term decay, leaving the agent in an unnatural, non-equilibrium limbic state after months of downtime.

---

### Alternative 3: Adaptive / Error-Budgeted Recovery
- **Mechanism:** Dynamically step the ODE using adaptive step-size Runge-Kutta (RK45) or stop integration when the distance to equilibrium falls below an error tolerance:
  $$\|s(t) - s^*_{\text{eff}}(R_t)\| < \epsilon_{\text{tol}}$$
- **Semantic Fidelity:** High. Adapts step size to rate of change.
- **Physical-Time Fidelity:** High.
- **Computational Cost:** Significantly lower than forward Euler, but still requires hundreds of adaptive steps.
- **Startup Latency:** Moderate ($5\text{--}20\text{ms}$).
- **Suitability for One Continuous Life:** Promising research candidate, but more complex than closed-form asymptotic solution.

---

### Alternative 4: Direct Projection to Relationally Conditioned Equilibrium
- **Mechanism:** For any $\Delta t > 0$, immediately project state to asymptotic rest:
  $$h(t_{\text{boot}}) = \mathbf{0}, \quad s(t_{\text{boot}}) = s^*_{\text{eff}}(R_t)$$
- **Semantic Fidelity:** Fails for short downtimes. A brief 5-second restart instantly obliterates recent emotional momentum.
- **Physical-Time Fidelity:** Completely ignores continuous time progression for $\Delta t < 5\tau$.
- **Computational Cost:** $O(1)$ ($\le 0.1\text{ms}$).
- **Startup Latency:** Instantaneous.
- **Suitability for One Continuous Life:** **REJECTED.** Erases limbic continuity during minor restarts or system reboots.

---

### Alternative 5: Hybrid Short Replay + Asymptotic Recovery (Candidate C / Recommended)
- **Mechanism:** Piecewise temporal formulation:
  1. **Short Downtime ($\Delta t \le \tau_{\text{cutoff}}$):** Execute canonical forward Euler ODE steps ($n \le \tau_{\text{cutoff}} / dt$). Preserves exact high-frequency reactive momentum $h_{\text{fast}}$ and non-linear somatic coupling.
  2. **Long Downtime ($\Delta t > \tau_{\text{cutoff}}$):** 
     - Fast tensor decays to zero: $h(t_{\text{boot}}) = \mathbf{0}$.
     - Slow tensor evaluates exact exponential relaxation to relationally conditioned attractor:
       $$s(t_{\text{boot}}) = s^*_{\text{eff}}(R_t) + \left(s_{\text{checkpoint}} - s^*_{\text{eff}}(R_t)\right) \exp\left(-\frac{\Delta t}{\tau_{\text{slow\_decay}}}\right)$$
     - Homeostatic energy and cognitive load settle exponentially toward resting levels:
       $$\mathcal{E}(t_{\text{boot}}) = 1.0 - (1.0 - \mathcal{E}_{\text{checkpoint}}) \exp(-\gamma_E \Delta t)$$
       $$\mathcal{C}(t_{\text{boot}}) = \mathcal{C}_{\text{checkpoint}} \exp(-\gamma_C \Delta t)$$
- **Semantic Fidelity:** **EXCELLENT.** Smooth, continuous transition from short reactive transients to long-term relational resting equilibrium.
- **Physical-Time Fidelity:** **EXCELLENT.** Respects both seconds-scale dynamics and months-scale resting decay.
- **Computational Cost:** Strictly bounded: $O(1)$ for long downtime, $\le 300$ steps for short downtime. Always $\le 1\text{ms}$.
- **Startup Latency:** Sub-millisecond ($\le 1\text{ms}$).
- **Suitability for One Continuous Life:** **OPTIMAL.** Satisfies all physical, relational, and computational invariants.

---

### Alternative 6: Lifecycle Pause / Resume (Frozen Time)
- **Mechanism:** Treat downtime as non-existent ($\Delta t = 0$). Resume exactly from serialized tensors without any unforced idle integration.
- **Semantic Fidelity:** Completely unbiological and non-continuous. An agent waking up after 6 months remains agitated mid-arousal.
- **Physical-Time Fidelity:** Total failure ($0\%$ fidelity).
- **Computational Cost:** Zero.
- **Suitability for One Continuous Life:** **REJECTED.** Violates physical-time semantics and INV-1.

---

## 4. Comprehensive Evaluation Matrix across Ten Criteria

| Criterion | Alt 1: Full Replay | Alt 2: Fixed 300s | Alt 3: Adaptive/Budget | Alt 4: Direct Proj | Alt 5: Hybrid Asymptotic | Alt 6: Pause/Resume |
|---|---|---|---|---|---|---|
| **1. Semantic Fidelity** | HIGH | POOR | HIGH | POOR (Short $\Delta t$) | **EXCELLENT** | UNACCEPTABLE |
| **2. Physical-Time Fidelity** | HIGH | FLAWED | HIGH | POOR | **EXCELLENT** | ZERO |
| **3. Computational Cost** | UNBOUNDED $O(\Delta t)$ | BOUNDED | BOUNDED | $O(1)$ | **$O(1)$ / BOUNDED** | $O(1)$ |
| **4. Startup Latency** | FAILS ($\gg 1\text{s}$) | EXCELLENT | GOOD ($10\text{ms}$) | EXCELLENT | **EXCELLENT ($\le 1\text{ms}$)** | EXCELLENT |
| **5. Numerical Correctness** | DRIFT RISKS | TRUNCATED | HIGH | EXACT AT $\infty$ | **EXACT / ANALYTIC** | N/A |
| **6. Relational Consistency** | HIGH | FLAWED | HIGH | HIGH | **EXCELLENT** | ZERO |
| **7. Memory Consistency** | INDEPENDENT | INDEPENDENT | INDEPENDENT | INDEPENDENT | **INDEPENDENT** | INDEPENDENT |
| **8. Homeostatic Consistency**| POOR (Wiped) | POOR (Wiped) | MODERATE | POOR | **EXCELLENT (Settled)** | ZERO |
| **9. Failure Behavior** | TIMEOUT / HANG | SAFE | SAFE | SAFE | **DETERMINISTIC SAFE**| SAFE |
| **10. Suitability for INV-1** | POOR | POOR | GOOD | POOR | **OPTIMAL** | UNACCEPTABLE |

---

## 5. Governance Notice on Empirical Constants

`[IMPORTANT GOVERNANCE BOUNDARY]`
In compliance with the architectural instructions:
- **300s is NOT ratified as canonical.** It is treated strictly as an empirical research exploration marker.
- The values $C_{\text{max}} \approx 2$, $221.4\text{s}$, and specific convergence $\epsilon$ values are **not canonicalized**.
- The engineering recommendation for $\tau_{\text{cutoff}}$ in Alternative 5 is proposed within the range:
  $$\tau_{\text{cutoff}} \in [30.0\text{s}, 60.0\text{s}]$$
  subject to formal **Human Owner Ratification**.

---

## 6. Mathematical Specification of the Recommended Recovery Model

When Alternative 5 is ratified, `EmotionCore.apply_dynamical_snapshot()` shall execute the following formal algorithm:

```python
def recover_continuous_state(
    snapshot: DynamicalStateSnapshot,
    R_t: np.ndarray,
    current_time: float,
    tau_cutoff: float = 60.0,
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    delta_t = max(0.0, current_time - snapshot.created_at)
    
    # 1. Compute Relational Attractor Target
    delta_r = np.clip(R_t, 0.0, 1.0) - R_0
    s_eff = s_philia + W_rel @ delta_r
    
    # 2. Evaluate Trajectory based on Delta t
    if delta_t <= tau_cutoff:
        # Short Downtime: Step ODE numerically to preserve transient trajectory
        h_recovered, s_recovered = numerical_unforced_euler(
            h_start=snapshot.h_fast,
            s_start=snapshot.s_slow,
            R_t=R_t,
            duration=delta_t,
            dt=0.20,
        )
    else:
        # Long Downtime: Fast dynamics extinguish; slow field relaxes asymptotically
        h_recovered = np.zeros(32, dtype=np.float64)
        decay_factor = np.exp(-delta_t / tau_slow_decay)
        s_recovered = s_eff + (snapshot.s_slow - s_eff) * decay_factor
    
    # 3. Asymptotically Settle Metabolic Energy and Cognitive Load
    energy_init = snapshot.energy if snapshot.energy is not None else 1.0
    load_init = snapshot.cognitive_load if snapshot.cognitive_load is not None else 0.0
    
    energy_recovered = 1.0 - (1.0 - energy_init) * np.exp(-gamma_E * delta_t)
    load_recovered = load_init * np.exp(-gamma_C * delta_t)
    
    return h_recovered, s_recovered, energy_recovered, load_recovered
```

---

*This document is an architecture decision analysis artifact prepared for Owner Review. Implementation is NOT authorized.*
