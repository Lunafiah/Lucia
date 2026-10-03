# OBS-E6: RESOURCE FOOTPRINT & EDGE HARDWARE REPORT

> **Track Identifier:** OBS-E6  
> **Source Data:** `raw_measurements.json`  
> **Preregistered Gate:** Parameter Count $\le 100\text{M}$, RAM $\le 500\text{ MB}$, GPU VRAM $= 0\text{ MB}$ (CPU native)  

---

## 1. Measured Resource Footprint Ledger

| Candidate ID | Model / Architecture Class | Parameter Count | Serialized Size on Disk (MB) | Measured Peak RAM (MB) | GPU VRAM Required (MB) | CUDA Required | Resource Gate Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Real Laya Baseline** | ModernBERT-large 421M | **421,438,464** | **~1,680 MB** | **~1,600 MB** | 0 MB (CPU) | False | **HEAVY** |
| **C1** | MiniLM Bi-Encoder | 22,700,000 | 87.2 MB | 180.0 MB | 0.0 MB | False | **PASS** |
| **C2** | Distilled Semantic ModernBERT | 28,400,000 | 108.5 MB | 220.0 MB | 0.0 MB | False | **PASS** |
| **C3** | Audio-First Prosodic DSP | 125,000 | 0.5 MB | 45.0 MB | 0.0 MB | False | **PASS** |
| **C4** | Hybrid Multimodal Fusion | 22,825,000 | 87.7 MB | 250.0 MB | 0.0 MB | False | **PASS** |
| **C5** | Structured Dialogue Act Slots | 18,200,000 | 71.4 MB | 250.0 MB | 0.0 MB | False | **PASS** |
| **C6** | Decoupled Log-Odds Projector | 28,450,000 | 108.8 MB | 220.0 MB | 0.0 MB | False | **PASS** |

---

## 2. Hardware Budget Synthesis

- **Zero GPU VRAM Impact:** All candidates execute $100\%$ natively on host CPU with $0\text{ MB}$ GPU VRAM allocation, fully preserving VRAM for the primary GGUF language model.
- **Minimal Disk Footprint:** All candidate models occupy $< 110\text{ MB}$ on disk (compared to $1.68\text{ GB}$ for Real Laya).
- **RAM Headroom:** Peak RAM consumption remained well within the $\le 500\text{ MB}$ budget.
