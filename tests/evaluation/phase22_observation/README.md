# Phase 22 — Observation Layer Replacement Study: Isolated Benchmark

This directory contains the isolated, non-production research evaluation harness for benchmarking
Observation Layer candidate classes C1 through C6 against the canonical Phase 22-XR Real Laya baseline.

## Hard Governance Rules
- All code is research-only; zero production imports (`src/core`, `electron`, `config`, `data` are untouched).
- Genesis invariant (`data/profile.json`) is preserved bit-exact (`{"is_onboarded": false}`).
- All experiments run 100% locally on CPU with zero cloud dependencies.
