# Phase 22-XR — Real Laya Verification & Evidence Closure

## 1. Purpose & Boundary
This harness conducts the isolated verification pass for the **real Laya neural backbone** (`ModernBERT-large` 421M, `convaiinnovations/laya`) to address the remaining unresolved empirical question of Phase 22-XR:
- Was the previous `ECE = 0.3349` caused by fallback emulation or real Laya?
- Does real Laya provide calibrated categorical observation probabilities?

### Hard Governance
- **Research Only:** Production code (`src/core/**`, `electron/**`, `config/**`, `data/**`) is strictly isolated and unmodified.
- **Fail-Closed Principle:** If offline SafeTensors model weights are missing, the harness enters `BLOCKED_OFFLINE_WEIGHTS`. Zero emulator substitution is permitted.
- **Genesis Invariant:** `data/profile.json` remains bit-exact `{"is_onboarded": false}`.

---

## 2. Directory Structure

```text
tests/evaluation/phase22_xr_laya/
├── README.md
├── run_experiments.py
├── validate_results.py
├── laya/
│   ├── __init__.py
│   ├── provenance.py
│   └── adapter.py
└── probes/
    ├── __init__.py
    └── corpus.py

evaluation_artifacts/phase22_xr_laya/
├── raw_measurements.json    # Canonical numerical truth
├── provenance.json          # Audit records & hashes
├── gate_results.json        # Architecture gate evaluations
├── model_manifest.json      # Hardware & execution environment
├── calibration_report.md
├── latency_report.md
├── alignment_report.md
├── comparison_matrix.md
├── failure_analysis.md
└── final_report.md          # Comprehensive executive summary
```

---

## 3. Execution Commands

To execute the verification pass:
```powershell
python tests/evaluation/phase22_xr_laya/run_experiments.py
```

To run the independent validator:
```powershell
python tests/evaluation/phase22_xr_laya/validate_results.py evaluation_artifacts/phase22_xr_laya/raw_measurements.json
```

---

## 4. Weight Requirements & Blocked-Mode Behavior

The real Laya model requires:
1. `rl_agent_config.json`
2. `model.safetensors` (~1.6 GB for ModernBERT-large)
3. `tokenizer.json`

If these files are absent locally in `C:/Users/Lunafiah/Desktop/My_project/laya/models/` or in `~/.cache/huggingface/hub/`, the harness will:
1. Complete the physical filesystem audit.
2. Confirm the exact missing components.
3. Emit `BLOCKED_OFFLINE_WEIGHTS`.
4. Halt neural execution cleanly without fabricating synthetic outputs.
5. Record Gate `G-XR1 = BLOCKED_OFFLINE_WEIGHTS`.
