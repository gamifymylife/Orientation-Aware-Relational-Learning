# v0.7 supporting synthetic result — complementary orientation search

## Provenance

This is the frozen exact-model result originally produced on draft PR #12 (`v06-complementary-orientation-gate`, head `14526c941e5cb2bcd1317dbdb26a516e06928f8f`). It is ported onto current `main` without changing the algorithm or result. It is supporting mechanism evidence for v0.7, not the external headline claim.

## Frozen result

- 9/9 gate tests passed on the original PR head.
- 6,912 exact policy episodes.
- OARL accuracy on resolvable worlds: **100%**.
- Correct `UNKNOWN` on fundamental insufficiency: **100%**.
- Mean OARL probes on resolvable worlds: **1.6** versus **3.6** exhaustive (**55.6% reduction**).
- Pure XOR complementarity: OARL **2 probes**, one-step active decision **3**, generic two-step lookahead **2**.
- Exact redundancy: OARL **3** pair-planning evaluations versus **6** with transport/equivalence ablated.

## What survived

1. Decision-relevant information can be non-additive across perspectives in the exact candidate-model setting.
2. Explicit pair-synergy avoids the pure-XOR failure mode of one-step decision-value acquisition.
3. A fair generic two-step lookahead matches OARL's probe count on XOR, so there is **no independent observational-efficiency claim over sufficiently capable generic lookahead**.
4. Exact quotienting can reduce redundant planning work while preserving the selected evidence path.
5. Exact decision-completeness supports principled abstention when the available perspectives are insufficient.

## Claim boundary

This result does **not** establish noisy empirical complementarity discovery, real-world generalization, arbitrary-order synergy discovery, or superiority to arbitrary-horizon Bayesian/optimal experimental design.

The external v0.7 programme therefore tests the narrower surviving thesis:

> **Relational orientation structure may make interaction-aware experimental search cheaper by quotienting redundant perspectives before complementarity-aware planning, while preserving decision correctness and calibrated abstention.**
