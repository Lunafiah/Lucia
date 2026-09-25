# EXP-05: Scaling & Hardware Feasibility Summary Table

> **Generated:** 2026-09-26 00:16:02  
> **Hardware Envelope:** 20-Watt CPU  
> **VRAM Impact:** 0.0 MB (Strict CPU Execution)  
> **TDP Status:** `UNVERIFIED (hardware power meter absent in environment)`  

---

## 1. 100k Horizon Scaling Overview

| Candidate | Verdict | Heap at 100k (MB) | WorkingSet at 100k (MB) | Bytes/Fact | Lookup p95 (ms) | Traversal p95 (ms) | Revision p95 (ms) |
|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | 43.0 MB | 189.2 MB | 450.8 B | 0.007 ms | 4.701 ms | 0.033 ms |
| **V-UMR** | **`FAIL`** | 167.2 MB | 660.3 MB | 1752.7 B | 0.019 ms | 6.563 ms | 0.124 ms |
| **DRS-Graph** | **`PASS`** | 51.0 MB | 210.3 MB | 534.7 B | 0.005 ms | 5.466 ms | 0.036 ms |

---

## 2. Scaling Progression by Fact Count (N)

| Fact Count (N) | Candidate | Heap (MB) | WorkingSet (MB) | 1-Hop Lookup p50 (ms) | 1-Hop Lookup p95 (ms) | Revision p95 (ms) |
|---|---|---|---|---|---|---|
| 1,000 | UMR-TPG | 0.4 MB | 19.4 MB | 0.0015 ms | 0.0029 ms | 0.0142 ms |
| 1,000 | V-UMR | 1.6 MB | 77.6 MB | 0.0197 ms | 0.0304 ms | 0.1755 ms |
| 1,000 | DRS-Graph | 0.5 MB | 80.2 MB | 0.0019 ms | 0.0034 ms | 0.0148 ms |
| 5,000 | UMR-TPG | 2.1 MB | 26.4 MB | 0.0021 ms | 0.0040 ms | 0.0247 ms |
| 5,000 | V-UMR | 8.1 MB | 68.8 MB | 0.0141 ms | 0.0217 ms | 0.0726 ms |
| 5,000 | DRS-Graph | 2.5 MB | 65.0 MB | 0.0026 ms | 0.0052 ms | 0.0322 ms |
| 10,000 | UMR-TPG | 4.2 MB | 35.0 MB | 0.0026 ms | 0.0045 ms | 0.0174 ms |
| 10,000 | V-UMR | 16.2 MB | 89.0 MB | 0.0198 ms | 0.0240 ms | 0.0535 ms |
| 10,000 | DRS-Graph | 5.0 MB | 69.1 MB | 0.0025 ms | 0.0041 ms | 0.0180 ms |
| 25,000 | UMR-TPG | 10.7 MB | 61.2 MB | 0.0033 ms | 0.0058 ms | 0.0349 ms |
| 25,000 | V-UMR | 41.7 MB | 178.9 MB | 0.0148 ms | 0.0227 ms | 0.0665 ms |
| 25,000 | DRS-Graph | 12.7 MB | 81.1 MB | 0.0026 ms | 0.0046 ms | 0.0344 ms |
| 50,000 | UMR-TPG | 21.4 MB | 103.9 MB | 0.0040 ms | 0.0127 ms | 0.0193 ms |
| 50,000 | V-UMR | 83.5 MB | 339.4 MB | 0.0214 ms | 0.0390 ms | 0.0978 ms |
| 50,000 | DRS-Graph | 25.4 MB | 116.4 MB | 0.0033 ms | 0.0057 ms | 0.0722 ms |
| 100,000 | UMR-TPG | 43.0 MB | 189.2 MB | 0.0037 ms | 0.0074 ms | 0.0325 ms |
| 100,000 | V-UMR | 167.2 MB | 660.3 MB | 0.0149 ms | 0.0188 ms | 0.1238 ms |
| 100,000 | DRS-Graph | 51.0 MB | 210.3 MB | 0.0030 ms | 0.0052 ms | 0.0364 ms |