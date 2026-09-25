# Intent Formulation Report (XR-E6) — Phase 22-XR

## 1. Architectural Distinction
- **Prospective Intent Prediction:** Forecasting user intent prior to observation: P(intent_{t+1} | z_hat_t).
- **Post-Observation Intent Interpretation:** Classifying intent given observation and state: P(intent_t | y_t, z_hat_t).

## 2. Findings
- Real Laya emits next-action decision primitives over 6 conversational classes.
- Laya does NOT perform autonomous multi-turn intent reasoning.
- Laya's observation primitives provide raw evidence that downstream Lucia continuous state filters use to update the continuous user belief vector z_user(t) in R^6.
