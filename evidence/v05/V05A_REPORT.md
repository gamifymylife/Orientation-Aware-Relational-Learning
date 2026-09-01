# OARL v0.5A — Exact Structure Discovery Report

## Executive result

**v0.5A passes its frozen exact-structure gate.**

The certifier recovered exact orientation equivalence classes and intervention/readout transports from the candidate likelihood geometry without reading the hidden ground-truth class, representative, permutation, scale, or offset metadata.

Across the 120-run confirmatory discovery grid (20 seeds × 3 orientation counts × 2 information-gain modes):

- pairwise equivalence precision: **100%**;
- pairwise equivalence recall: **100%**;
- false merged pairs: **0**;
- paired mechanism-identification outcome agreement with Oracle Quotient: **100%**;
- median acquisition-score evaluation reduction vs Generic OED: **75%** overall.

The compression scales exactly with redundancy in the tested 4-class construction:

| Raw orientations | Discovered classes | Score-evaluation reduction |
|---:|---:|---:|
| 8 | 4 | 50.0% |
| 16 | 4 | 75.0% |
| 24 | 4 | 83.3% |

A 300-world unique-orientation negative control (100 seeds at 8, 16 and 24 orientations) produced **zero false merges** and retained one discovered class per raw orientation in every world.

## End-to-end compute result

v0.5A also answers an important practical question left open by v0.3: does discovering the quotient cost more than it saves?

The answer depends on the acquisition-score cost.

### Cheap proxy information gain

Certificate discovery dominates the very cheap proxy scorer. The discovered quotient therefore **does not** improve end-to-end wall-clock runtime in this regime, despite reducing score evaluations.

This is a genuine negative boundary condition: structural compression is not automatically worthwhile when the baseline acquisition computation is already trivial.

### Quadrature information gain

With the more expensive quadrature information-gain calculation, certificate cost amortizes quickly. A separate serial, single-threaded sanity check over five paired seeds per scale found median end-to-end runtime reductions of:

| Raw orientations | Median runtime reduction vs Generic OED |
|---:|---:|
| 8 | **51.9%** |
| 16 | **73.0%** |
| 24 | **83.8%** |

Every serial paired run showed a positive runtime reduction.

These timing values are implementation- and hardware-dependent. The robust scientific point is narrower: **a measurable break-even regime exists** where one-time exact structure discovery plus quotient search is cheaper end-to-end than repeated exhaustive acquisition scoring.

## What was discovered

For each orientation pair, v0.5A attempts to recover:

1. the permutation mapping local intervention labels to a reference orientation;
2. one positive affine response transform `y_target = offset + scale * y_reference`;
3. the corresponding observation-scale transform.

Mechanism-centered normalized response signatures remove a shared readout offset and positive scale. The deliberately mechanism-flat benchmark class has no such signature, so the implementation uses the rank-preserving scalar intervention centers plus the observation-scale relation as a fallback. This edge case is included rather than excluded from the gate.

A pair is merged only if the recovered transport reproduces the entire candidate likelihood geometry to strict exact tolerance. Ambiguous near-matches are not merged.

## What v0.5A does **not** establish

This result must not be described as general empirical structural certification.

v0.5A uses the candidate mechanism predictive likelihood geometry. It does not yet show that equivalence can be certified from finite noisy real measurements. It also does not infer whether an algebraically plausible orientation is physically or semantically admissible; admissibility remains an externally declared constraint.

Therefore the project has moved from:

> *"If someone gives us the exact quotient, it saves computation."*

to:

> **"In the exact candidate-model setting, the quotient and transport can be recovered algorithmically without hidden class metadata, and there are acquisition-cost regimes where discovery plus quotient search is cheaper end-to-end than exhaustive search."**

That is stronger than v0.3, but still conditional.

## Gate evaluation

| Preregistered criterion | Result | Verdict |
|---|---:|---|
| Pairwise precision = 100%; no false merges | 100%; 0 false merges | **PASS** |
| Pairwise recall ≥ 99% | 100% | **PASS** |
| Discovered vs Oracle paired outcomes identical | 100% match | **PASS** |
| Material score-evaluation compression | 50–83.3% by scale | **PASS** |
| Unique-world negative control has no false merges | 0 / 300 worlds | **PASS** |

**Overall v0.5A: PASS.**

## Next gate — v0.5B

The next experiment should remove the exact-likelihood assumption.

v0.5B should estimate orientation geometry from finite noisy predictive samples and return a three-way decision:

- **CERTIFIED EQUIVALENT**;
- **CERTIFIED DISTINCT**;
- **UNKNOWN / ABSTAIN**.

The primary optimization target should be equivalence **precision**, not coverage. v0.4 already demonstrated why: a false merge can damage inference, whereas an abstention or false split mainly gives up computation savings.

The decisive v0.5B question is:

> Can useful equivalence coverage survive finite noise while keeping the false-merge rate low enough that end-to-end mechanism identification remains indistinguishable from the oracle-safe baseline?
