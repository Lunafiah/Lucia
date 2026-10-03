# Epistemic Action Selection Report (XR-E7) — Phase 22-XR

## 1. Expected Information Gain (EIG) Evaluation
- Evaluated active epistemic action selection vs passive observation.
- Information gain across candidate probe queries is strictly computed with respect to user latent belief uncertainty.
- Zero future ground truth leakage verified.

## 2. Findings
Active query selection prioritizes questions that maximize mutual information I(z; y), reducing entropy in user state dimensions with high epistemic variance (e.g. cognitive load and clarity need).
