# Orientation-Aware Benchmark v0.3 — Structural Gate-2 Report

## Executive result

v0.2 falsified the additive scoring rule `IG - lambda*log(1+K) - gamma*C` as an advantage over generic OED.

v0.3 tests a different claim: **can known relational orientation structure remove redundant search or block structurally invalid interrogations without sacrificing mechanism identification?**

In the controlled benchmark, the answer is **yes** for exact equivalence quotienting and exact admissibility metadata.

## Exact orientation quotienting

The `equivalent_redundancy` regime groups raw orientations into exact equivalence classes. Members differ only by a bijective intervention permutation and an invertible affine observation transform with the corresponding noise transform.

For equivalent experiments linked by a bijection `Y' = phi(Y)` independent of the hidden mechanism `H`, mutual information is invariant:

`I(H;Y'|e') = I(H;Y|e)`.

Therefore exhaustive OED over raw orientations can factor through the quotient space:

`O × A  ->  (O / ~) × A`.

If there are `O` raw orientations, `C` equivalence classes and `A` interventions, acquisition scoring falls from `O*A` to `C*A`; the ideal reduction is `1 - C/O`.

## Confirmatory result — 100 held-out seeds

Configuration:

- 12 mechanisms
- 24 raw orientations
- 4 exact equivalence classes
- 12 interventions
- budget 30

Structured OARL and the fair exhaustive Generic-OED baseline produced:

- identical final correctness on **100/100 paired worlds**
- identical `N95` on **100/100**
- identical penalized `C95` on **100/100**
- **83.3% median score-evaluation reduction**
- mean score evaluations approximately **6537.6 -> 1089.6**

This is a **computational advantage**, not a sample-efficiency advantage: the same inference result is obtained with less redundant acquisition scoring.

## Evidence transport

Posterior evidence transport is exact for the certified invertible transforms because the likelihood Jacobian is independent of `H` and cancels during Bayesian normalization.

A canonical-representative-only policy had higher physical experimental cost, while structured OARL could execute the cheapest equivalent raw orientation and transport its evidence back canonically. This matched the exhaustive cost-aware OED result while avoiding exhaustive scoring.

## Scaling

With four equivalence classes held fixed, ideal/observed score-evaluation reduction was:

| Raw orientations | Reduction |
|---:|---:|
| 8 | 50.0% |
| 16 | 75.0% |
| 32 | 87.5% |
| 64 | 93.75% |
| 128 | 96.875% |
| 256 | 98.4375% |

With expensive numerical mutual-information quadrature, wall-clock savings approached the quotient reduction; with the cheap vectorized proxy, runtime savings were smaller because bulk scoring itself is inexpensive.

## Negative controls

- When every orientation is structurally unique, quotienting gives **no compression advantage**.
- In an adversarial invalid-reverse control, admissibility gating prevents the learner from selecting a mathematically tempting but structurally invalid boundary.

## Claim boundary

v0.3 demonstrates downstream value **assuming the equivalence classes and admissibility metadata are correct**. It does not show that such structure can yet be inferred reliably from real systems.

That assumption becomes the explicit v0.4 falsification target.
