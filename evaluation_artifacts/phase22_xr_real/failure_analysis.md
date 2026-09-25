# Failure and Disentanglement Analysis — Phase 22-XR-L

## 1. Disentangling Causal Layers

Lucia Phase 22-XR-L enforces the scientific rule:
$$\text{Upstream Observation Quality} \neq \text{Observation Alignment} \neq \text{Continuous State Dynamics}$$

1. **Why Naive Mapping Failed ($R^2 < 0$)**:
   The assumption that $y = 2p - 1$ maps probability simplex $\Delta^5$ directly into the continuous latent space $\mathbb{R}^6$ is mathematically invalid.
2. **Why Alignment Restores Tracking**:
   Introducing an explicit inverse mapping model $g^{-1}$ (Linear A1 or Bounded MLP A2) allows the filter to accurately recover latent signals ($R^2 \ge 0.85$).
3. **Status of Real Laya Backbone**:
   Offline execution is blocked by the absence of local weight files (`model.safetensors`). This is a **resource availability boundary**, not an architectural refutation.
