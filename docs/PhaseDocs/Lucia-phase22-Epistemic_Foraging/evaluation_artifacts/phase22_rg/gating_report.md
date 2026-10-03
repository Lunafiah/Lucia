# Phase 22-RG -- Gating Summary Report

## Held-Out Seeds, All Regimes, All Languages

| Gate | Mand.Recall | Precision | Inj.Rate | Hall.Risk | Rel.Cons | Compression | Token P95 | Lat.P50 (ms) |
|---|---|---|---|---|---|---|---|---|
| G0_NoGate | 0.9905 | 0.3640 | 0.2820 | 0.0000 | 0.9877 | 0.4349 | 293 | 0.0262 |
| G1_StaticThreshold | 0.9905 | 0.5282 | 0.0000 | 0.0000 | 0.9856 | 0.5223 | 287 | 0.0228 |
| G2_EvidenceStrength | 0.9905 | 0.5282 | 0.0000 | 0.0000 | 0.9856 | 0.5223 | 287 | 0.0193 |
| G3_TemporalDecay | 0.9905 | 0.5170 | 0.0000 | 0.0000 | 0.9855 | 0.5118 | 287 | 0.0456 |
| G4_SafetyFirstHybrid | 0.9905 | 0.5089 | 0.0151 | 0.0000 | 0.9860 | 0.5080 | 289 | 0.0626 |
| Oracle | 0.9905 | 0.5282 | 0.0000 | 0.0000 | 0.9856 | 0.5223 | 287 | 0.0196 |
