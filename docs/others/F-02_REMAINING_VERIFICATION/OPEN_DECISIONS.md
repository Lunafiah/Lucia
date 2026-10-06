# Open Architecture Decisions Requiring Owner Ratification (F-02 Verification)

**Document ID:** `VERIF-OPEN-20261007`  
**Classification:** Post-Verification Governance & Ratification Ledger  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Date:** 2026-10-07  
**Parent Document:** [`REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_REMAINING_VERIFICATION/REPORT.md)  

---

## 1. Governance Status

Following the completion of the numerical simulations and code archaeology across V1–V9, the remaining open decisions have been refined and consolidated. Only the following **three explicit governance decisions** require Owner Ratification before implementation can proceed.

---

## 2. Refined Decision Ledger

### Decision OD-01: Ratification of Two-Stage Hybrid Recovery Parameters
- **Context:** Numerical verification proved that uncoupled exponential decay at $60\text{s}$ produces significant PAD error ($\approx 0.18$) if Lucia was stressed or fatigued at shutdown. However, running canonical forward Euler integration up to $180\text{s}$ takes only **$1.5\,\text{ms}$** of CPU time, guaranteeing $0.0\%$ approximation error during homeostatic transients. For $\Delta t \ge 300\text{s}$, direct projection to $s^*_{\text{eff}}(R_t)$ is accurate to $\le 0.0014$ in PAD space.
- **Options for Owner Ratification:**
  - **Option A (Recommended):** Ratify the **Two-Stage Hybrid Recovery Model**:
    - Stage 1 ($0 \le \Delta t \le 180\text{s}$): Forward Euler ODE integration ($dt=0.20\text{s}$, max 900 steps, latency $\le 1.5\,\text{ms}$).
    - Stage 2 ($180\text{s} < \Delta t < 300\text{s}$): Exponential decay to $s^*_{\text{eff}}(R_t)$.
    - Stage 3 ($\Delta t \ge 300\text{s}$): Direct $O(1)$ projection to $s^*_{\text{eff}}(R_t)$ and $h = \mathbf{0}$.
  - **Option B:** Ratify a shorter cutoff $\tau_{\text{cutoff}} = 120\text{s}$ (600 steps, latency $\le 1.0\,\text{ms}$, max transient PAD error $\le 0.053$).
  - **Option C:** Pure Error-Budgeted Adaptive Runge-Kutta stepping.
- **Agent Recommendation:** **Option A.**

---

### Decision OD-02: Working Dialogue Memory Reseeding Policy
- **Context:** Verification revealed that `data/chat_history.json` is purely archival and never read by `CognitiveOrchestrator`. On startup, `CognitiveOrchestrator._history` initializes to `[]`. This causes the LLM prompt assembler to receive zero prior conversational turns on the first post-restart turn, even though the user sees previous turns on the UI screen.
- **Options for Owner Ratification:**
  - **Option A (Recommended):** Reseed `CognitiveOrchestrator._history` on startup with the trailing $K=10$ turn pairs from `data/chat_history.json`.
  - **Option B (Maintain Status Quo):** Keep `_history` strictly ephemeral starting from `[]` on every cold restart (fresh conversation session context).
- **Agent Recommendation:** **Option A.**

---

### Decision OD-03: Authorization for F-02 Remediation Implementation
- **Context:** With mathematical validity confirmed, numerical cutoffs established, and restore ordering verified, is the implementation of the F-02 remediation plan authorized to begin?
- **Scope of Proposed Remediation:**
  1. Invert startup dependency in `src/core/orchestrator/cognitive_orchestrator.py` (`RelationshipUpdater` $\to$ `EmotionCore`).
  2. Implement Two-Stage Hybrid Recovery in `src/core/emotion/emotion_core.py` (replacing unbounded Euler loop).
  3. Implement `data/epoch_manifest.json` multi-store commit barrier in `CognitiveOrchestrator` Stage 16.
  4. Reseed `_history` on startup from `chat_history.json`.
- **Options for Owner Ratification:**
  - **YES:** Authorize implementation under Pair Programming protocol.
  - **NO:** Defer implementation; retain current architecture analysis status.
- **Current Status:** **NO (BLOCKED PENDING OWNER RATIFICATION).**

---

*This document is a governance ledger artifact prepared for Owner Review. Implementation is NOT authorized.*
