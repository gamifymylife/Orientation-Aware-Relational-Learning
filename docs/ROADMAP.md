# Research Roadmap

## v0.5 — Certified Orientation Structure Discovery

### Decisive question

> Can equivalence and admissibility be inferred from finite noisy evidence with sufficiently high precision that end-to-end quotienting saves real computation while preserving mechanism identification on unseen systems?

### Required system

The next implementation must produce a three-way structural decision from raw evidence:

1. **certified equivalent/admissible** — quotient/transport is permitted;
2. **certified distinct/invalid** — keep separate or reject;
3. **unknown** — abstain and retain the raw experiment.

### Metrics

- equivalence precision and false-merge rate;
- equivalence recall and false-split rate;
- admissibility precision / invalid-as-valid rate;
- abstention/coverage;
- calibration of certificate confidence;
- final mechanism-identification correctness;
- false-high-confidence decisions;
- raw score evaluations;
- wall-clock runtime;
- **certificate-discovery cost**;
- total end-to-end cost relative to exhaustive generic OED.

### Baselines

- no quotient / generic OED;
- oracle exact structure;
- generic similarity clustering;
- canonicalization / duplicate-action elimination where applicable;
- learned classifier without abstention;
- precision-first classifier with abstention.

### Kill criterion

Do not call v0.5 successful merely because the classifier has high average accuracy. The practical gate is:

`cost(certification) + cost(quotient OED) < cost(exhaustive OED)`

**while preserving correctness and false-high-confidence risk on held-out systems.**

If this cannot be shown, v0.3 remains a valid conditional optimization result but not a deployable method.

## External escalation

1. Run the corrected DREAM4 Size100 confirmatory gate.
2. Add an external benchmark with genuine redundant admissible experimental views so quotient discovery can be tested, not just intervention-label value.
3. Add a dynamical-system benchmark with ground-truth structure.
4. Add an ABM equifinality benchmark.
5. Implement the original H5 held-out-orientation representation-generalization experiment.
6. Run a prospective/blinded mechanism-discrimination task.

## Novelty gate

Before claiming a major methodological contribution, benchmark against symmetry/group reduction, canonicalization, bisimulation/behavioral equivalence, causal abstraction and generic experimental-design compression. The novelty burden is the orientation-specific **discovery/certification/risk** layer, not the trivial fact that quotienting known duplicates saves search.

## Repository engineering

- Keep evidence immutable by version.
- Tag confirmatory releases.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
