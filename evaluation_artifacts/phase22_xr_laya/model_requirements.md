# Real Laya Neural Checkpoint Requirements & Specification

## 1. Executive Summary
This document establishes the exact checkpoint specification, architecture, tensor structures, file dependencies, and execution constraints required for genuine neural inference using the Laya neural backbone, derived directly from the audited source repository at `C:\Users\Lunafiah\Desktop\My_project\laya`.

---

## 2. Checkpoint Specifications

| Dimension | English Default Checkpoint | Multilingual Checkpoint |
|---|---|---|
| **Model Repository ID** | `convaiinnovations/laya` | `convaiinnovations/laya-multilingual` |
| **Model Variant / Subfolder** | Root (English Latin-script) | `subfolder="multilingual"` |
| **Base Neural Encoder** | `answerdotai/ModernBERT-large` | `mmBERT-base` |
| **Parameter Count** | **421,438,464** (~421M parameters) | **322,000,000** (~322M parameters) |
| **Supported Sequence Length** | 512 tokens (sliding window local attention) | 1024 tokens |
| **Vocabulary / Tokenizer** | 50,280 English BPE (`tokenizer.json`) | 100+ language BPE (`tokenizer.json`) |
| **Decision Head Architecture** | 2-layer MLP classifier over pooled encoder hidden states | 2-layer MLP classifier |
| **Action Primitives / Classes** | 6 discrete conversational actions | 6 discrete conversational actions |
| **Output Representation** | Raw logits $\mathbb{R}^6$ & Softmax probability simplex $\Delta^5$ | Raw logits $\mathbb{R}^6$ & Softmax probability simplex $\Delta^5$ |
| **Native Execution Precision** | bfloat16 (activations) / float32 (residual stream & logits) | bfloat16 / float32 |

---

## 3. Required Physical Checkpoint Files

To instantiate the genuine neural model without fallback emulation, the local repository or Hugging Face cache must contain:

```text
convaiinnovations/laya/
├── model.safetensors          (~1.60 GB; full ModernBERT-large + DecisionHead weights)
├── config.json                (Encoder configuration: hidden_size=1024, num_hidden_layers=28)
├── rl_agent_config.json       (RL agent hyperparameters, action costs, temperature)
├── tokenizer.json             (Fast BPE tokenizer data)
├── tokenizer_config.json      (Special tokens, padding, truncation rules)
└── vocab.json                 (Vocabulary mapping)
```

---

## 4. Distinction Between Source Code and Neural Weights

The repository audit at `C:\Users\Lunafiah\Desktop\My_project\laya` reveals:
- **Source Code Present:** Python engine modules (`laya/agent.py`, `laya/router.py`, `laya/common.py`, `laya/fast.py`, `laya/tl_kernels.py`) are fully present.
- **Model Configuration Present:** Packaging configuration (`pyproject.toml`, `zensical.toml`) exists.
- **Model Weights Missing:** Physical weight files (`*.safetensors`, `*.bin`, `*.pt` $> 100\text{ MB}$) are **not bundled** in the git repository and are not present in local Hugging Face caches.

---

## 5. Offline Weight Acquisition & Boundary Rules

1. **Authorized Acquisition Sources:**
   - Official Hugging Face Hub repository: `convaiinnovations/laya` (Revision `main`).
   - Official snapshot download mechanism: `huggingface-cli download convaiinnovations/laya --local-dir <path>`.
2. **Strict Prohibition on Surrogate / Unofficial Weights:**
   - Unofficial third-party checkpoints, arbitrary quantized GGUFs, or rule-based heuristics must NEVER be substituted.
3. **Fail-Closed Boundary:**
   - In environments where network access is restricted or offline transfer has not occurred, the execution harness MUST report `BLOCKED_OFFLINE_WEIGHTS` / `BLOCKED_CHECKPOINT_ACQUISITION` and exit cleanly without generating fabricated neural outputs.
