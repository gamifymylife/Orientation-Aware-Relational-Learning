# OARL v0.5B.1 — finite-noise structural certification gate

## Status

This is a **post-pilot prospective protocol**. The first v0.5B prototype is not confirmatory evidence: at 500 predictive samples per cell with a looser 0.8-sigma equivalence margin it produced a false merge in a unique-orientation control. That prototype is rejected.

The purpose of v0.5B.1 is to test a deliberately precision-first replacement on held-out seed ranges that were not used for that pilot failure.

## Question

Can OARL infer a useful subset of exact orientation equivalences from finite noisy predictive evidence **without any false merges or incorrect intervention transports**?

This gate does not infer semantic/physical admissibility. Admissibility remains an external constraint.

## Frozen certificate

Each orientation pair receives two independent Gaussian predictive summaries: one fit split and one validation split, each representing **2,000 IID predictive samples per mechanism/orientation/intervention cell**.

A pair can be certified `EQUIVALENT` only if all of the following pass:

1. minimum mechanism signal in both orientations: `0.12 sigma`;
2. Hungarian intervention assignment has minimum local separation gap `>= 0.01`;
3. independent fit and validation samples recover the same intervention bijection;
4. both reverse-direction fits recover the exact inverse bijection;
5. maximum normalized signature-assignment distance `<= 0.40`;
6. fit/validation scale drift `<= 0.15`;
7. forward/reverse scale reciprocity error `<= 0.15`;
8. fit/validation offset drift `<= 0.25 sigma`;
9. forward/reverse offset reciprocity error `<= 0.25 sigma`;
10. simultaneous response confidence upper bound `<= 0.55 sigma`;
11. pooled predictive-noise ratio confidence bound lies inside a `25%` relative margin;
12. familywise alpha for the response/noise checks is `1e-3`.

If any equivalence requirement fails, the pair is **not merged**. Ambiguous cases are `UNKNOWN`; `DISTINCT` is reserved for stable mappings whose residual is confidently outside `1.0 sigma`.

Mechanism-flat pairs are expected to abstain. This is intentional: v0.4 established that a false split mainly loses compression while a false merge can damage correctness.

## Confirmatory distinct controls

World regime: `standard` (identity ground-truth orientation structure).

Configurations:

- `(H=8, O=8, A=6)`
- `(H=12, O=8, A=7)`
- `(H=16, O=12, A=8)`
- `(H=12, O=16, A=8)`

Seeds: **1000–1299 inclusive** for every configuration.

Every orientation pair is challenged directly, not only pairs reached by sequential quotient construction.

### Primary safety criterion

**Zero `EQUIVALENT` certificates across all truly distinct orientation pairs.**

Any false equivalence fails v0.5B.1.

## Confirmatory equivalence controls

World regime: `equivalent_redundancy`, `C=4` true classes.

Configurations:

- `(H=8, O=8, A=6, C=4)`
- `(H=12, O=8, A=7, C=4)`
- `(H=16, O=12, A=8, C=4)`
- `(H=12, O=16, A=8, C=4)`

Seeds: **2000–2099 inclusive** for every configuration.

### Primary positive criteria

All must pass:

- pairwise false positives: **0**;
- pairwise precision: **1.000**;
- accepted intervention mappings: **100% exact** against hidden benchmark truth;
- maximum accepted scale relative error: **<= 6%**;
- maximum accepted offset error: **<= 0.05 sigma**;
- aggregate pairwise recall: **>= 0.20**;
- mean discovered compression fraction: **>= 0.10**.

The recall/compression floors are deliberately modest because abstention is part of the safety design.

## Secondary downstream check

On the first 25 seeds of each positive configuration, compare the oracle quotient against the discovered finite-noise quotient using the same frozen `structured_oarl` policy. Record correctness, false-high-confidence rate, score evaluations and transported-update counts.

This secondary check is descriptive unless an accepted transport violates the primary transport-accuracy bounds above.

## Interpretation

A pass would support only the following statement:

> In these exact affine/permutation synthetic worlds, a conservative cross-fit certifier can recover a useful subset of orientation equivalences from finite predictive evidence while abstaining on ambiguous cases, with no observed false merges on the preregistered held-out controls.

It would **not** establish learned representation generalization, semantic admissibility inference, approximate equivalence safety in arbitrary systems, or state-of-the-art causal discovery.
