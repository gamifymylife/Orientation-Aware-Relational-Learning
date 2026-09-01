# Claims and Evidence Ledger

This file is the authoritative claim boundary for the repository. It intentionally separates conceptual propositions, demonstrated benchmark results, falsified method claims and open hypotheses.

| Claim | Status | Evidence | What would change the status? |
|---|---|---|---|
| A mechanism distinction can be hidden by one observational boundary and exposed by another. | **Supported** in controlled, historical and external executable cases | `evidence/v01/`, `evidence/v02/`, `external/historical/`, `evidence/v061/`, `evidence/v062/` | Broader external failures would narrow domain scope. |
| Orientation/boundary is a legitimate experimental-design variable when multiple admissible views exist. | **Supported conditionally** | synthetic orientation controls; historical replay; pyGSTi shallow-vs-deep boundary case; v0.6.2 rank audit | Additional third-party domains would strengthen scope. |
| `IG - lambda log(1+K) - gamma C` improves generic OED. | **Falsified on the tested benchmark** | `evidence/v02/V02_CONFIRMATORY_REPORT.md` | A materially different formulation must be treated as a new hypothesis, not a rescue of v0.2. |
| Exact orientation equivalence can be quotiented without changing Bayesian mechanism identification. | **Supported in the exact synthetic construction** | `evidence/v03/` and `test_transport_update_matches_raw_update` | Formal generalization and independent reproduction would strengthen it. |
| Exact quotienting can reduce acquisition-score computation. | **Supported** | v0.3: 83.3% at 24→4; 98.4% at 256→4 | End-to-end accounting must include certificate-discovery cost. |
| Exact quotient structure can be discovered from candidate-model likelihood geometry without hidden class labels. | **Supported in the exact synthetic construction** | `evidence/v05/`, `src/oarl_bench/certification.py` | External and less structured model families would strengthen it. |
| Incorrect equivalence declarations are riskier than conservative missed equivalences. | **Supported in controlled stress tests and reinforced externally** | `evidence/v04/`; v0.6.1 sealed false-merge gate | External downstream inference studies should quantify consequence, not just count merges. |
| Incorrectly admitting semantically invalid high-information orientations can be catastrophic. | **Supported as an adversarial failure mode** | v0.4 false-admissibility-positive control | Do not interpret the synthetic magnitude as a universal real-world percentage. |
| A precision-first certifier can infer a useful subset of exact orientation equivalences from finite noisy predictive evidence. | **Supported in the preregistered affine/permutation synthetic gate** | `evidence/v05b/`: 72,600 distinct-pair challenges, 0 false equivalences, precision 1.000, recall 0.2757 | External replication with the same safety level is still missing. |
| Accepted finite-noise transports can be recovered accurately enough for the current synthetic quotient. | **Supported in v0.5B.1** | 829 accepted direct certificates; 0 mapping errors; max scale error 3.92%; max offset error 0.0212 sigma | Stress under approximate/non-affine transport and external systems. |
| Gauge-equivalent internal representations can be substantially different while remaining observationally identical. | **Externally confirmed, but not novel to OARL** | `evidence/v061/` pyGSTi smoke; established GST gauge theory | This is a domain fact used as external ground truth, not an OARL discovery claim. |
| Direct shallow probability equivalence can fail when a deeper observational boundary amplifies a mechanism difference. | **Supported in v0.6.1 pyGSTi gate** | `op_noise=0.010`: sealed max difference 0.02926 > epsilon 0.020 while shallow classifiers often merge | Replicate in other dynamical/iterated systems and with other boundary families. |
| The frozen v0.6.1 OARL cross-fit + depth-stability certificate safely extrapolates equivalence to unseen deeper circuits. | **Falsified on the preregistered external gate** | 522 operational false merges; primary zero-false-merge check failed | A new method must be preregistered and tested on fresh seeds as v0.6.2 or later. |
| The v0.6.1 OARL certificate improves the shallow safety/precision tradeoff over direct probability equivalence. | **Supported descriptively, not sufficient for the strong gate** | aggregate precision 0.8355 vs 0.7497; false merges 522 vs 1,191; at 100k shots precision 0.9362 vs 0.7500 | Compare against stronger generic structural/trend baselines on fresh data. |
| More finite samples are sufficient to repair an insufficient observational boundary. | **Falsified in the v0.6.1 boundary case** | OARL false merges on `op_noise=0.010` rose from 0/300 at 50k to 282/300 at 500k as shallow uncertainty vanished | A richer boundary or justified extrapolation model is required. |
| Repeating a fixed rank-deficient observation boundary increases local information span. | **Falsified / structurally impossible in the frozen local audit** | v0.6.2: depth-1 Fisher rank stayed 2 and nullity 1 under repetition factors 1, 10, 100 and 1000 | A different boundary can change span; repetition of the same fixed local information operator cannot. |
| A new admissible boundary can expose a local mechanism direction absent from a repeated fixed boundary. | **Supported in v0.6.2 pyGSTi audit** | one depth-2 circuit increased Fisher rank from 2 to 3; all 126 probes jointly had full rank | Replicate on fresh mechanism families and non-quantum systems. |
| OARL's null-space selector is superior to classical optimal experimental design for filling missing information directions. | **Not demonstrated; v0.6.2 tied D-optimality** | null-space coverage and greedy D-optimality both reached rank 3 with one depth-2 circuit at added depth cost 2 | A fresh held-out benchmark must show lower cost or higher safety than D/E-optimal and generic rank methods. |
| OARL can infer semantic/physical admissibility reliably from raw finite noisy evidence. | **Not demonstrated** | v0.5B.1 treats admissibility as external; v0.6.1 separates physical from operational truth | Requires a separate admissibility-certification programme with invalid-as-valid safety gates. |
| Approximate quotienting is safe with useful coverage. | **Not demonstrated generally** | v0.4 downstream sensitivity; v0.6.1 external epsilon-equivalence safety failure | Requires calibrated approximation + boundary-extrapolation bounds and abstention. |
| Finite-noise certification is end-to-end cheaper than exhaustive Generic OED. | **Not demonstrated** | v0.5B.1 safety/coverage only; v0.5A break-even only for exact discovery with expensive quadrature scoring | Full certification-acquisition + OED cost comparison against exhaustive Generic OED on held-out and external systems. |
| OARL beats generic structural equivalence methods on a third-party executable benchmark. | **Not demonstrated** | v0.6.1 beats a direct shallow probability comparator on precision but fails its own safety gate; v0.6.2 ties D-optimality on local rank completion | Fresh external gate against generic trend, envelope, canonicalization, symmetry, behavioral-equivalence and optimal-design baselines. |
| OARL is state of the art in causal discovery / active inference. | **Not claimed** | — | Would require specialist baselines and external benchmarks. |

## Current methodological interpretation

The strongest surviving architecture is not a replacement for ordinary Bayesian or Fisher-optimal experimental design. It is a structural safety/compression layer around it:

```text
finite evidence / candidate predictive family
    ↓
boundary-information + structural certification
    ├── certified equivalent -> quotient/transport permitted
    ├── certified distinct   -> keep separate
    └── unknown              -> abstain; keep separate
    ↓
risk-bounded quotient
    ↓
standard experimental design / inference
```

v0.5B.1 showed that structural certification can work in the synthetic affine/permutation family when the evidence boundary contains the relevant distinction. v0.6.1 exposed **boundary extrapolation uncertainty**: a finite-sample certificate can become very confident inside a shallow boundary while remaining wrong about an unseen deeper boundary.

v0.6.2 then separated information magnitude from information span in an external executable model. The initial depth-1 pyGSTi boundary had Fisher rank 2 of 3. Repetition by 1000 scaled the two visible eigenvalues by 1000 but left rank at 2 and the third eigenvalue at zero. One new depth-2 circuit raised rank to 3. This cleanly supports the boundary-vs-repetition distinction, but the OARL-motivated null-space selector tied greedy D-optimality at the same minimum added depth cost. Therefore the result is **conceptually supportive but algorithmically non-distinctive**.

The immediate burden is now v0.6.3: on fresh held-out systems with finite noise and explicit acquisition cost, decide between spending budget on repeated evidence and changing the observational boundary. OARL only earns an incremental utility claim if its equivalence/abstention/quotient layer improves safety or total cost beyond established optimal-design and rank-based methods.
