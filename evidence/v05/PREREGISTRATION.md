# OARL v0.5A — Exact Structure Discovery Gate

## Status

**Protocol frozen before the v0.5A confirmatory grid is interpreted.**

v0.5A addresses the first missing link left by v0.3/v0.4: can exact orientation equivalence and its transport be **discovered from the candidate likelihood geometry**, rather than supplied as oracle metadata?

This phase is deliberately narrower than the eventual empirical-certification problem. It does **not** infer whether an orientation is physically or semantically admissible. Admissibility remains an external declared constraint in v0.5A. A future v0.5B must address finite/noisy approximate certificates.

## Hidden information

The discovery algorithm may use:

- candidate mechanism predictive means `p(y | H, orientation, intervention)` as represented by the benchmark mean tensor;
- predictive observation scales;
- the externally declared admissibility mask.

It must not use:

- `true_orientation_class`;
- `true_class_representative`;
- `true_to_canonical_intervention`;
- `true_transform_scale` or `true_transform_offset`.

Those fields are evaluation-only oracle truth.

## Compared policies

1. **Generic OED** — searches all declared-admissible raw orientation/intervention actions.
2. **Oracle Quotient OED** — receives the true exact equivalence classes/transports.
3. **Discovered Quotient OED** — receives only structure inferred by the v0.5A certifier.

## Primary structural metrics

- pairwise equivalence precision;
- pairwise equivalence recall;
- false merges;
- false splits;
- recovered number of equivalence classes;
- recovered intervention transport.

False merges are treated as the primary safety failure because v0.4 showed they can damage correctness, whereas false splits mainly sacrifice efficiency.

## Primary end-to-end metrics

- mechanism-identification correctness;
- 0.95-posterior success rate;
- acquisition score evaluations;
- certificate comparisons;
- certificate runtime;
- policy runtime;
- end-to-end wall-clock runtime.

Certificate comparisons are reported separately from information-gain score evaluations rather than pretending the two operations have equal cost.

## v0.5A pass criteria

On exact `equivalent_redundancy` worlds:

1. **Safety:** pairwise equivalence precision = 100% on the confirmatory grid; no false merges.
2. **Recovery:** pairwise recall >= 99%.
3. **Inference preservation:** Discovered Quotient and Oracle Quotient have identical paired correctness and success outcomes.
4. **Compression:** Discovered Quotient materially reduces acquisition score evaluations relative to Generic OED in redundant regimes.
5. **Negative control:** on unique-orientation worlds, the certifier creates no false merges.

Runtime savings are exploratory in v0.5A because exact certificate construction itself has computational cost. The stronger practical claim requires a demonstrated end-to-end break-even regime.

## Kill conditions

v0.5A fails if any of the following occurs on the frozen confirmatory grid:

- a false merge;
- discovered structure changes a paired mechanism-identification outcome relative to oracle structure;
- the apparent quotient saving exists only because hidden truth metadata leaked into discovery.

## What a pass would mean

A pass would establish only that the v0.3 quotient can be reconstructed algorithmically in the exact model-family setting. It would **not** establish safe approximate equivalence from finite real measurements. That becomes the next gate.
