# Phase 22-SC: Critical Ablation Report

Measuring failure modes when stripping one semantic component at a time (Held-Out seeds):

| Ablation Removed | Target Candidate | D0 Fidelity | Over-Inf Rate | Contradiction Handled | Tier Match | Primary Failure Mode Observed |
|---|---|---|---|---|---|---|
| **no_provenance** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | Attribution loss; cannot trace memory to session/turn; fine-grained audit impossible. |
| **no_temporal** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | Temporal causality inversion; cannot distinguish recent repair from older rupture. |
| **no_strength** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | Equal salience given to weak noise and milestone events; subtle degradation. |
| **no_uncertainty** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | Over-confidence; inability to hedge stance on sparse history (LexicalSparsity). |
| **no_contradiction** | C4 (Hybrid) | 0.6904 | 0.00% | 22.61% | 100.00% | CRITICAL: Guarded stance lost; high over-inference (false intimacy during rupture). |
| **no_repair** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | CRITICAL: Relationship permanently locked in defensive stance; cannot reconcile. |
| **no_tier** | C4 (Hybrid) | 0.5533 | 1.92% | 100.00% | 26.82% | CRITICAL: Severe tier collapse; defaults to T1 stranger/acquaintance baseline. |
| **no_anchor_id** | C4 (Hybrid) | 1.0000 | 0.00% | 100.00% | 100.00% | Anchor identity lost; cannot verify specific relational milestones. |