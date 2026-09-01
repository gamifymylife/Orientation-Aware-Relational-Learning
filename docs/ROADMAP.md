# Research Roadmap

## v0.5 — Certified Orientation Structure Discovery

### Original decisive question

> Can equivalence and admissibility be inferred from finite noisy evidence with sufficiently high precision that end-to-end quotienting saves real computation while preserving mechanism identification on unseen systems?

That question has now split into distinct scientific gates rather than being treated as one monolithic classifier problem.

## Completed: v0.5A — exact structural discovery

v0.5A removed the assumption that equivalence classes and transports must be handed to the system as hidden metadata. In the exact synthetic candidate-model setting, the implementation can infer the exact quotient structure from the likelihood geometry.

Frozen results under `evidence/v05/` support:

- zero observed false merges in the exact discovery gate;
- oracle-equivalent structural recovery on the tested worlds;
- large score-evaluation reductions after quotienting;
- a real end-to-end break-even regime when experiment scoring is expensive (quadrature IG), while cheap proxy scoring does **not** amortize certificate overhead.

This is a conditional exact-model result, not a noisy-data or external-generalization claim.

## Completed: v0.5B.1 — finite-noise equivalence certification

The initial 500-sample pilot failed by false-merging a distinct pair and is preserved as a negative result. A separate post-pilot protocol was then frozen and tested on held-out seed ranges.

Preregistered v0.5B.1 result:

- 72,600 truly distinct pair challenges;
- 0 false equivalence certificates;
- pair precision 1.000;
- pair recall 0.2757;
- 17.9% mean discovered compression;
- 829 accepted direct certificates;
- 0 accepted intervention-mapping errors;
- maximum accepted scale error 3.92%;
- maximum accepted offset error 0.0212 sigma.

Interpretation: the **equivalence side** of finite-noise structural certification now has a viable precision-first proof of concept in the current affine/permutation synthetic family. Ambiguous cases are intentionally `UNKNOWN` rather than forced into a class.

See `evidence/v05b/V05B_CONFIRMATORY_REPORT.md`.

## Next: v0.5C — complete the practical gate

v0.5 is not finished merely because finite-noise equivalence certification passed. The remaining practical burden is:

### 1. Admissibility certification

The system must distinguish:

1. **certified admissible** — experiment may enter the acquisition set;
2. **certified invalid/inadmissible** — reject;
3. **unknown** — abstain / require external constraint.

The primary safety metric is **invalid-as-valid rate**, because v0.4 showed that admitting a semantically invalid high-information action can be catastrophic.

Do not infer admissibility by reusing the equivalence score. It is a different claim and requires its own ground truth, failure modes and preregistration.

### 2. End-to-end finite-noise economics

Measure:

`cost(acquiring certificate evidence) + cost(certification) + cost(quotient OED)`

against:

`cost(exhaustive Generic OED)`.

The comparison must include:

- predictive-sample / experiment acquisition cost;
- certificate computation;
- acquisition-score evaluations;
- wall-clock runtime;
- final mechanism correctness;
- false-high-confidence decisions;
- abstention coverage.

The current v0.5B.1 secondary result compares the discovered quotient to the **oracle quotient**, so it is not this economic gate.

### 3. Generic structural baselines

Before claiming OARL-specific advantage, compare the same task against:

- no quotient / Generic OED;
- oracle exact structure;
- generic similarity clustering;
- canonicalization / duplicate-action elimination;
- group/symmetry reduction where available;
- behavioral equivalence / bisimulation-style reduction;
- a non-abstaining classifier;
- the precision-first OARL certifier.

### v0.5 kill criterion

Do not call v0.5 deployable unless, on held-out systems:

`cost(certification evidence + certification + quotient OED) < cost(exhaustive OED)`

**while preserving correctness and false-high-confidence risk and keeping invalid-as-valid errors within a preregistered safety bound.**

If this cannot be shown, v0.5A/B remain useful structural-certification results but not an end-to-end method advantage.

## v0.6 — representation and domain generalization

After v0.5C, move beyond the construction family used to design the certifier.

Required escalation:

1. run the corrected DREAM4 Size100 confirmatory gate;
2. add a third-party executable benchmark with genuine redundant admissible experimental views;
3. implement the original H5 held-out-orientation representation-generalization experiment;
4. add a dynamical-system benchmark with ground-truth structure;
5. add an ABM equifinality benchmark;
6. test non-Gaussian predictive families;
7. test non-affine and approximate transports with calibrated abstention;
8. run a prospective/blinded mechanism-discrimination task.

## Novelty gate

Before claiming a major methodological contribution, benchmark against symmetry/group reduction, canonicalization, bisimulation/behavioral equivalence, causal abstraction and generic experimental-design compression. The novelty burden is the orientation-specific **discovery/certification/risk** layer, not the trivial fact that quotienting known duplicates saves search.

## Repository engineering

- Keep evidence immutable by version.
- Tag confirmatory releases.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Preserve failed pilots and negative confirmatory results.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
