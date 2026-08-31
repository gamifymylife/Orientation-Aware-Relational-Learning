# Orientation-Aware Relational Learning (OARL)

> **Mechanism identifiability can depend on the boundary from which a system is interrogated.**

Orientation-Aware Relational Learning is a research programme for representing, comparing, and actively selecting different admissible input/output orientations of the same underlying relation.

The current project asks three increasingly strong questions:

1. **Exposure:** can a mechanism distinction be invisible from one observational boundary and visible from another?
2. **Compression:** can equivalent orientations be quotient-ed so experimental design searches fewer redundant candidates without changing the inference result?
3. **Certification:** how accurately must equivalence/admissibility structure be known before that compression becomes unsafe?

## Current evidence

The evidence is deliberately mixed rather than uniformly positive.

- **v0.1:** orientation search clearly beat fixed-boundary acquisition on controlled worlds, but the proposed stability-aware scoring rule did not beat generic OED.
- **v0.2:** frozen calibration selected `lambda = 0, gamma = 0`; the static stability/cost penalty therefore added no defensible value over generic OED on the same action space.
- **v0.3:** exact orientation quotienting preserved identification outcomes while cutting experiment-score evaluations by 83.3% in a 24→4 equivalence-class setting, and by 98.4% in a 256→4 scaling condition.
- **v0.4:** false splits were mainly an efficiency loss, while false merges and false admissibility positives could materially damage correctness. This motivates conservative, abstention-friendly structural certification.
- **Historical external replay:** Meselson–Stahl and Luria–Delbrück both exhibit boundary-dependent mechanism identifiability.
- **DREAM4 external gate:** preregistered and ready to run on the official third-party benchmark. No DREAM4 result is claimed until the official data are executed through the frozen runner.

## Core formal move

For an orientation set `O` and intervention set `A`, generic exhaustive experimental design searches

```text
O × A
```

If a certified equivalence relation partitions orientations into classes, OARL can instead search

```text
(O / ~) × A
```

while transporting evidence through valid representation maps. Under exact bijective observation transformations, mutual information is invariant, so scoring every raw representative is redundant.

## Repository map

```text
src/oarl_bench/           benchmark and inference code
scripts/                  frozen benchmark runners
tests/                    automated tests
evidence/v02/             negative confirmatory result for static penalties
evidence/v03/             quotient-search Gate-2 result
evidence/v04/             structural-classifier robustness result
external/historical/      historical external replay
external/dream4/          preregistered DREAM4 external gate
```

## Scientific claim boundary

The strongest currently supported claim is:

> **A fixed observational boundary can make distinct mechanisms observationally equivalent; changing to another legitimate boundary can expose the distinction. When multiple orientations are exactly equivalent, certified quotienting can remove redundant acquisition computation without changing the inference result.**

The project does **not** yet claim that:

- OARL is a new state-of-the-art active causal discovery algorithm;
- the current structural classifier is externally validated;
- approximate quotienting is safe in arbitrary real systems;
- OARL beats generic OED on an established third-party executable benchmark;
- a static stability penalty improves Bayesian experimental design.

## Current external milestone

The next confirmatory gate is the official **DREAM4 In Silico Network Challenge**. The preregistration compares the same knockout/knockdown response matrices with intervention identity preserved versus erased. This directly tests whether the intervention→response relation carries directed mechanism information beyond the unlabeled numerical measurements.

See [`external/dream4/PREREGISTRATION.md`](external/dream4/PREREGISTRATION.md).

## Reproducibility

Python 3.11+ is recommended.

```bash
python -m pip install -e '.[dev]'
pytest -q
```

The repository intentionally keeps frozen reports and compact result summaries, while excluding caches and very large raw Monte Carlo outputs.

## Status

Research prototype. The programme is intentionally falsification-oriented: failed hypotheses and negative benchmark results are retained as first-class evidence rather than removed after method changes.
