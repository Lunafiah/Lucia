# Phase 22-MR — Context Compression & Token Budget Report

| Candidate | Compression (mean) | Tokens P95 | Injection Rate |
|---|---|---|---|
| M0_RawDump | 0.3008 | 513 | 0.6641 |
| M1_TopKCosine | 0.0817 | 100 | 0.8812 |
| M2_TemporalRelational | 0.3555 | 128 | 0.0368 |
| M3_GraphAware | 0.5152 | 254 | 0.2423 |
| M4_HybridFull | 0.4115 | 472 | 0.3999 |
| Oracle | 0.5313 | 381 | 0.0000 |
