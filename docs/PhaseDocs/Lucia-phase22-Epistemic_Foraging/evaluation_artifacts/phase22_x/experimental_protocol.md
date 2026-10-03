# Experimental Protocol — Phase 22-X

> **Protocol Execution Record**: Phase 22-X Isolated Research Evaluation  
> **Target Subsystems**: Non-Generative Decision Primitive, User Belief Filter, Latent Dynamics, Intent Prediction Tree, Epistemic Selection  
> **Source Runner**: [`tests/evaluation/evaluation_phase22_x/run_experiments.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase22_x/run_experiments.py)  

---

## 1. Execution Pipeline

Experiments were executed sequentially using deterministic random seeds ($S=42$) across:
1. **E1 (Observation Calibration)**:
   - Data generation: 10,000 train turns, 2,500 validation turns, 5,000 in-distribution test turns, 3,000 turns per DS condition.
   - Temperature scaling optimized via L-BFGS on validation NLL.
   - Evaluated models: B0 (Majority Prior), B1 (Calibrated MLP), B4 (Jev/Laya Surrogate).
2. **E2 (Recursive Belief Filtering)**:
   - 100 independent dialogue episodes of length $T=50$ turns with $\sigma_{\text{obs}}=0.15$.
   - Contradiction recovery benchmark on DS-3 across 30 episodes.
3. **E3 (Temporal Latent Dynamics)**:
   - 80 dialogue episodes of length $T=50$ under transient observation noise spikes ($\sigma_{\text{obs}}=0.25$).
   - Measured state-flipping rate during stationary ground truth and 1-step lookahead accuracy.
4. **E4 (Intent Prediction)**:
   - 50 episodes of length $T=40$.
   - Temporal split strictly enforced: prospective intent $P(\text{intent}_{t+1})$ evaluated before turn $t+1$ observation is revealed.
5. **E5 (Bounded Prediction Tree)**:
   - 200 trials with $H=3, B=3$, pruning threshold $\tau=0.04$.
   - Wall-clock latency timed via `time.perf_counter()`.
6. **E6 (Epistemic Action Selection)**:
   - 100 episodes of length $T=30$ comparing EIG policy against reactive scalar surprise.
7. **E7 (Closed-Loop Multi-Turn Stability)**:
   - 500 complete closed-loop episodes ($T=30$, 15,000 total turns) under mixed canonical and shifted conditions.
