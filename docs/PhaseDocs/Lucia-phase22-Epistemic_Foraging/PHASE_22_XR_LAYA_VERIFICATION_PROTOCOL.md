# Phase 22-XR — Standalone Laya Neural Backbone Verification Protocol

> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_FOLLOWUP_RESEARCH_SPEC.md`  
> **Target Repository**: `C:\Users\Lunafiah\Desktop\My_project\laya` (v0.3.20)  
> **Status**: `[RESEARCH PROTOCOL — VERIFICATION STANDARD]`  
> **Date**: September 2026  

---

## 1. Purpose & Provenance Boundary

In Phase 22-XR, the evaluation harness recorded a distribution-shift calibration metric of $\text{ECE} = 0.3349$. As established in `post_evaluation_architectural_analysis.md`, this measurement was obtained under `LayaAdapter Emulation Mode (Fallback)` because model weights were offline.

The purpose of this protocol is to define an **auditable, fail-closed procedure** to verify the real Laya neural backbone on local hardware, ensuring that:
1. Emulation outputs are **never** reported as real Laya results.
2. Missing weights terminate execution as `BLOCKED_OFFLINE_WEIGHTS` rather than silently continuing.
3. Every executed forward pass is traceable to a specific checkpoint and SHA-256 weight hash.

---

## 2. Checkpoint Specifications & Requirements

### 2.1 Required Checkpoints
| Checkpoint Identifier | Backbone Architecture | Parameter Count | Context Length | Weight Format | Target Hardware Budget |
|---|---|---|---|---|---|
| `convaiinnovations/laya` | `ModernBERT-large` + 2-layer `TransformerEncoder` head | 421M | 8,192 tokens | PyTorch SafeTensors (`model.safetensors`) | 1.8 GB RAM / VRAM |
| `convaiinnovations/laya-multilingual` | `mmBERT-base` + 2-layer `TransformerEncoder` head | 322M | 8,192 tokens | PyTorch SafeTensors (`model.safetensors`) | 1.4 GB RAM / VRAM |

### 2.2 Expected Local Directory Structure
```text
C:\Users\Lunafiah\Desktop\My_project\laya\
├── laya/
│   ├── common.py          # DecisionModel & proper_reward
│   ├── agent.py           # Agent inference wrapper
│   └── ...
└── models/                # Local offline weights directory
    ├── english/
    │   ├── config.json
    │   ├── tokenizer.json
    │   └── model.safetensors
    └── multilingual/
        ├── config.json
        ├── tokenizer.json
        └── model.safetensors
```

---

## 3. Fail-Closed Execution Logic

The verification runner must enforce the following strict branching logic prior to any evaluation:

```text
Check Local Weight Path (models/english/model.safetensors)
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
Weights Present?                 Weights Missing?
        │                               │
Verify SHA-256 Hash              Emit Provenance:
        │                        "BLOCKED_OFFLINE_WEIGHTS"
        ▼                               │
Execute PyTorch Forward Pass     Terminate Verification Task
        │                        (Zero Emulation Fallback)
        ▼
Emit Provenance:
"VERIFIED_BY_EXECUTION"
```

### Python Implementation Guardrail
```python
def verify_laya_neural_backbone(weights_dir: str) -> VerificationResult:
    weight_file = os.path.join(weights_dir, "model.safetensors")
    if not os.path.exists(weight_file):
        return VerificationResult(
            status="BLOCKED_OFFLINE_WEIGHTS",
            reason=f"SafeTensors weight file not found at {weight_file}",
            is_executable=False,
            metrics={}
        )
    # Validate file integrity
    sha256_hash = compute_sha256(weight_file)
    ...
```

---

## 4. Verification Test Battery

When weights are present, the verification protocol executes four automated tests:

### Test 1 — Probability Simplex & Marker Invariance
- Evaluates 100 diverse conversational turns across single and multi-question batches.
- **Invariant:** For every question $j$, $\sum_{i=1}^{k} p_{j,i} = 1.0 \pm 10^{-6}$ and $p_{j,i} \ge 0.0$.
- **Marker Check:** Option permutations must preserve invariant probability ranking (invariance to candidate order).

### Test 2 — Calibration Under In-Distribution vs Noise Surge
- Measures 15-bin ECE on:
  - Canonical conversational prompts ($\text{ECE}_{\text{ID}}$).
  - Noise-surged acoustic prompts ($\text{ECE}_{\text{noise}}$).
  - Lexically sparse prompts ($\text{ECE}_{\text{sparse}}$).
- **Gate G-XR1 Criterion:** $\text{ECE}_{\text{shift}} \le 0.10$.

### Test 3 — Non-Autoregressive SLA Benchmark
- 500 timed forward passes on local CPU (Ryzen 9, 8 threads pinned) and local GPU (CUDA, if available).
- Measures P50, P95, P99 latency and peak allocated RSS / VRAM.
- **SLA Criterion:** CPU P50 $\le 350.0\,\text{ms}$, GPU P50 $\le 35.0\,\text{ms}$.

### Test 4 — Memorylessness & Recurrence Audit
- Executes identical turns with and without state history clearing.
- **Invariant:** Output logits must be bit-exact across independent calls ($\max |\mathbf{z}^{(1)} - \mathbf{z}^{(2)}| = 0.0$).
- Confirms zero hidden state or KV cache leakage across turns.

---

## 5. Mandatory Provenance Header

Every experimental result generated under this protocol must include the following provenance record:

```markdown
### Laya Backbone Provenance Record
- **Execution Mode**: `VERIFIED_BY_EXECUTION` (or `BLOCKED_OFFLINE_WEIGHTS`)
- **Backbone**: `convaiinnovations/laya` (ModernBERT-large)
- **Weight Checksum (SHA-256)**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **Execution Device**: `CPU (8 threads)` / `CUDA:0 (RTX 4070)`
- **Inference Library**: `PyTorch 2.14.0+cpu`
- **Timestamp**: `2026-09-24T22:00:00Z`
```
No evaluation claim regarding Laya may be made without this complete record.
