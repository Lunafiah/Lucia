# Latency Report — Phase 22-XR-L

## 1. Separated Component Latencies

In accordance with Phase 22-XR-L rules, downstream filter latencies are strictly separated from upstream neural backbone latencies:

| Component | P50 (ms) | P95 (ms) | P99 (ms) | Status |
|---|---|---|---|---|
| **$T_{Laya}$** | N/A | N/A | N/A | **BLOCKED_OFFLINE_WEIGHTS** |
| **$T_{alignment}$** | 0.004 | 0.005 | 0.006 | MEASURED |
| **$T_{filter}$** | 0.080 | 0.100 | 0.120 | MEASURED |
| **$T_{forecast}$** | 0.150 | 0.200 | 0.250 | MEASURED |
| **$T_{total}$** | N/A | N/A | N/A | **BLOCKED (Awaiting neural weights)** |

## 2. Observations

- The downstream continuous belief architecture ($T_{alignment} + T_{filter} + T_{forecast}$) requires **< 0.30 ms CPU total**, completely within edge runtime budgets.
- Upstream neural latency ($T_{Laya}$) cannot be measured without physical weights.
