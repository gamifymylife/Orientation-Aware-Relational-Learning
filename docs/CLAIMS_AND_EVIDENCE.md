# Claims and Evidence Ledger

This file is the authoritative claim boundary for the repository. It intentionally separates conceptual propositions, demonstrated benchmark results, falsified method claims and open hypotheses.

| Claim | Status | Evidence | What would change the status? |
|---|---|---|---|
| A mechanism distinction can be hidden by one observational boundary and exposed by another. | **Supported** in controlled and historical cases | `evidence/v01/`, `evidence/v02/`, `external/historical/` | Broader external failures would narrow domain scope. |
| Orientation is a legitimate experimental-design variable when multiple admissible boundaries exist. | **Supported conditionally** | v0.1/v0.2 orientation-exclusive controls; historical replay | Third-party prospective confirmation would strengthen it. |
| `IG - lambda log(1+K) - gamma C` improves generic OED. | **Falsified on the tested benchmark** | `evidence/v02/V02_CONFIRMATORY_REPORT.md` | A materially different formulation must be treated as a new hypothesis, not a rescue of v0.2. |
| Exact orientation equivalence can be quotiented without changing Bayesian mechanism identification. | **Supported in the exact synthetic construction** | `evidence/v03/` and `test_transport_update_matches_raw_update` | Formal generalization and independent reproduction would strengthen it. |
| Exact quotienting can reduce acquisition-score computation. | **Supported** | v0.3: 83.3% at 24→4; 98.4% at 256→4 | End-to-end accounting must include certificate-discovery cost. |
| Incorrect equivalence declarations are riskier than conservative missed equivalences. | **Supported in controlled stress tests** | `evidence/v04/` | External classifier studies must test the same asymmetry. |
| Incorrectly admitting semantically invalid high-information orientations can be catastrophic. | **Supported as an adversarial failure mode** | v0.4 false-admissibility-positive control | Do not interpret the synthetic magnitude as a universal real-world percentage. |
| OARL can infer equivalence/admissibility reliably from raw finite noisy evidence. | **Not demonstrated** | No classifier/certifier exists yet. | v0.5 is designed to test this. |
| Approximate quotienting is safe with useful coverage. | **Not demonstrated** | v0.4 only maps downstream sensitivity to injected transport error. | Requires calibrated risk bounds and abstention. |
| OARL beats generic OED end-to-end on a third-party executable benchmark. | **Not demonstrated** | DREAM4 Size100 pending; DREAM4 is primarily a boundary-value gate. | External confirmatory run plus a benchmark that measures quotient-discovery/search cost. |
| OARL is state of the art in causal discovery / active inference. | **Not claimed** | — | Would require specialist baselines and external benchmarks. |

## Current methodological interpretation

The strongest surviving architecture is not a new replacement for ordinary Bayesian experimental design. It is a structural layer around it:

```text
raw evidence
    ↓
structural certification
    ├── certified equivalent / admissible
    ├── certified distinct / invalid
    └── unknown → abstain
    ↓
risk-bounded quotient
    ↓
generic experimental design
```

The unresolved scientific burden sits in **structural certification**, not in showing yet again that a known quotient contains fewer elements than the raw action space.
