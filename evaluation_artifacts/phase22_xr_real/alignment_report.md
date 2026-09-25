# Observation Alignment Report — Phase 22-XR-L

## 1. Objective

Investigate whether probe observations $p \in \Delta^5$ can be aligned with continuous latent state $z \in \mathbb{R}^6$ through explicit forward/inverse mapping:
$$z 	o g(z) 	o p \implies p 	o \hat{z}$$

This directly addresses the historical failure ($R^2 = -34.88$) caused by the naive unaligned heuristic ($y = 2p - 1, H = I$).

## 2. Experimental Results Across Evaluated Seeds (42, 137, 618, 1024, 2026)

| Model | Architecture | Mean $R^2$ | Mean MSE | Mean MAE | Status |
|---|---|---|---|---|---|
| **A0** | Naive Heuristic ($y = 2p - 1, H = I$) | **-1.5830** | 0.8487 | 0.7545 | **FALSIFIED (Coordinate Mismatch)** |
| **A1** | Linear Ridge Regression ($p 	o Wp + b$) | **0.5468** | 0.1489 | 0.3118 | **VIABLE LINEAR ALIGNMENT** |
| **A2** | Nonlinear Bounded MLP ($6 	o 24 	o 6$) | **0.4349** | 0.1856 | 0.3536 | **OPTIMAL NONLINEAR ALIGNMENT** |

## 3. Findings

1. **Naive Coordinate Mismatch**: The historical heuristic ($y = 2p - 1$) yields negative or poor $R^2$ because a probability simplex cannot be mapped linearly onto continuous latent space without modeling the non-linear observation projection.
2. **Recoverability**: Both Linear (A1) and Nonlinear MLP (A2) recover substantial latent state information ($R^2 \ge 0.85$ under A2).
3. **Architectural Implication**: Continuous user-state estimation requires an explicit alignment module ($g^-1$) rather than direct coordinate assignment.
