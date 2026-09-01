# Claims and Evidence Ledger

This file is the authoritative claim boundary for the repository. It intentionally separates conceptual propositions, demonstrated benchmark results, falsified method claims and open hypotheses.

| Claim | Status | Evidence | What would change the status? |
|---|---|---|---|
| A mechanism distinction can be hidden by one observational boundary and exposed by another. | **Supported** in controlled and historical cases | `evidence/v01/`, `evidence/v02/`, `external/historical/` | Broader external failures would narrow domain scope. |
| Orientation is a legitimate experimental-design variable when multiple admissible boundaries exist. | **Supported conditionally** | v0.1/v0.2 orientation-exclusive controls; historical replay | Third-party prospective confirmation would strengthen it. |
| `IG - lambda log(1+K) - gamma C` improves generic OED. | **Falsified on the tested benchmark** | `evidence/v02/V02_CONFIRMATORY_REPORT.md` | A materially different formulation must be treated as a new hypothesis, not a rescue of v0.2. |
| Exact orientation equivalence can be quotiented without changing Bayesian mechanism identification. | **Supported in the exact synthetic construction** | `evidence/v03/` and `test_transport_update_matches_raw_update` | Formal generalization and independent reproduction would strengthen it. |
| Exact quotienting can reduce acquisition-score computation. | **Supported** | v0.3: 83.3% at 24→4; 98.4% at 256→4 | End-to-end accounting must include certificate-discovery cost. |
| Exact quotient structure can be discovered from the candidate-model likelihood geometry without hidden class labels. | **Supported in the exact synthetic construction** | `evidence/v05/`, `src/oarl_bench/certification.py` | External and less structured model families would strengthen it. |
| Incorrect equivalence declarations are riskier than conservative missed equivalences. | **Supported in controlled stress tests** | `evidence/v04/` | External classifier studies must test the same asymmetry. |
| Incorrectly admitting semantically invalid high-information orientations can be catastrophic. | **Supported as an adversarial failure mode** | v0.4 false-admissibility-positive control | Do not interpret the synthetic magnitude as a universal real-world percentage. |
| A precision-first certifier can infer a useful subset of exact orientation equivalences from finite noisy predictive evidence. | **Supported in the preregistered affine/permutation synthetic gate** | `evidence/v05b/`: 72,600 distinct-pair challenges, 0 false equivalences, precision 1.000, recall 0.2757, mean compression 0.1787 | Replication across new structural families and real/external systems is required for broader scope. |
| Accepted finite-noise transports can be recovered accurately enough for the current synthetic quotient. | **Supported in v0.5B.1** | 829 accepted direct certificates; 0 mapping errors; max scale error 3.92%; max offset error 0.0212 sigma | Stress under approximate/non-affine transport and external systems. |
| OARL can infer semantic/physical admissibility reliably from raw finite noisy evidence. | **Not demonstrated** | v0.5B.1 treats admissibility as an external constraint. | Requires a separate admissibility-certification programme with invalid-as-valid safety gates. |
| Approximate quotienting is safe with useful coverage. | **Not demonstrated generally** | v0.4 maps downstream sensitivity to injected transport error; v0.5B.1 certifies exact-family equivalences under sampling noise | Requires calibrated approximation bounds and abstention across non-exact systems. |
| Finite-noise certification is end-to-end cheaper than exhaustive Generic OED. | **Not demonstrated** | v0.5B.1 is a safety/coverage gate; the conservative quotient uses more score evaluations than the oracle quotient. v0.5A found break-even only for exact discovery with expensive quadrature scoring. | Full certification-acquisition + OED cost comparison against exhaustive Generic OED on held-out and external systems. |
| OARL beats generic OED end-to-end on a third-party executable benchmark. | **Not demonstrated** | DREAM4 Size100 pending; DREAM4 is primarily a boundary-value gate. | External confirmatory run plus a benchmark that measures quotient-discovery/search cost. |
| OARL is state of the art in causal discovery / active inference. | **Not claimed** | — | Would require specialist baselines and external benchmarks. |

## Current methodological interpretation

The strongest surviving architecture is not a replacement for ordinary Bayesian experimental design. It is a structural safety/compression layer around it:

```text
finite evidence / candidate predictive family
    ↓
structural certification
    ├── certified equivalent -> quotient/transport permitted
    ├── certified distinct   -> keep separate
    └── unknown              -> abstain; keep separate
    ↓
risk-bounded quotient
    ↓
generic experimental design
```

v0.5B.1 materially advances the unresolved certification burden, but only in the current exact affine/permutation synthetic family. The remaining burden is **generalization**: admissibility, approximate equivalence, learned representations, third-party executable systems, and end-to-end economics.
