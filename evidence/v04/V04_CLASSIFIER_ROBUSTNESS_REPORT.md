# Orientation-Aware Benchmark v0.4 — Structural Classifier Robustness

## Executive result

v0.3 showed that exact orientation-equivalence classes can reduce acquisition search without changing mechanism-identification outcomes.

v0.4 attacks the hidden assumption behind that result: **what if the orientation classifier is wrong?**

The answer is strongly asymmetric.

> **False structural positives are dangerous; conservative false negatives are usually much safer.**

In this benchmark, incorrectly declaring two genuinely different orientations equivalent (`false merge`) or incorrectly declaring a structurally invalid orientation admissible can severely damage mechanism identification. By contrast, failing to recognize a real equivalence (`false split`) mostly sacrifices efficiency while preserving correctness.

This implies that an operational OARL classifier should be **precision-first and abstention-friendly**.

---

## 1. Error taxonomy

v0.4 separates five structural-classifier failure modes.

### False merge

Two genuinely different orientation classes are declared equivalent.

Consequence: the quotient removes a real distinction and evidence may be transported through the wrong representative.

### False split

Two truly equivalent orientations are treated as distinct.

Consequence: the method performs redundant search and loses opportunities to choose/transport across cheaper equivalents, but does not invent a false structural identity.

### Admissibility false positive

A truly invalid orientation is classified as admissible.

Consequence: active OED may preferentially select the invalid orientation precisely because it appears highly informative.

### Admissibility false negative

A valid orientation is conservatively rejected.

Consequence: some experiment options are lost, but remaining evidence retains valid semantics.

### Transport metadata error

The declared affine transport parameters differ from the true representation transform.

Consequence: raw evidence is mapped imperfectly into the canonical representation.

---

## 2. False merges are dangerous

Controlled sweep:

- 32 raw orientations;
- 8 true equivalence classes;
- 12 mechanisms;
- 12 interventions;
- 30-step budget.

100-seed shape sweep:

| False-merge rate | Declared classes | Correct | 95%-success | False high confidence |
|---:|---:|---:|---:|---:|
| 0 | 8 | 93% | 80% | 0% |
| 12.5% | 7 | 79% | 62% | 8% |
| 25% | 6 | 67% | 53% | 18% |
| 37.5% | 5 | 62% | 45% | 15% |
| 50% | 4 | 55% | 30% | 17% |

The first non-zero corruption level corresponds to incorrectly merging only **one of eight true classes**.

A separate 500-seed paired confirmation gives:

- clean correctness: **94.6%**;
- one-false-merge correctness: **86.0%**;
- paired difference: **−8.6 percentage points**;
- bootstrap 95% CI: **[−11.4, −5.8] pp**.

95%-identification success falls by **10.0 pp**, CI **[−13.2, −7.0] pp**.

False-high-confidence decisions increase by **3.2 pp**, CI approximately **[+1.6,+4.8] pp**.

### Interpretation

A false equivalence declaration is not merely a lost opportunity. It destroys a genuine experiment distinction and can cause invalid evidence transport.

Therefore equivalence classification should not be optimized primarily for recall.

---

## 3. False splits are comparatively safe

Equivalent-redundancy sweep:

- 24 raw orientations;
- 4 true classes.

As true equivalences are progressively split into separate declared classes:

| False-split rate | Declared classes | Correct | 95%-success | Mean score evaluations |
|---:|---:|---:|---:|---:|
| 0 | 4 | 72% | 42% | 1,130 |
| 25% | 9 | 72% | 42% | 2,543 |
| 50% | 14 | 72% | 42% | 3,956 |
| 75% | 19 | 72% | 42% | 5,369 |
| 100% | 24 | 72% | 42% | 6,782 |

Final correctness and success remain identical across the paired sweep. What disappears is the structural advantage:

- score evaluation rises toward exhaustive OED;
- experimental cost rises because the learner can no longer recognize and choose among cheaper equivalent physical orientations.

### Interpretation

A false split behaves like abstention:

> "I do not know that these two views are the same, so I will keep them separate."

That is computationally inefficient but epistemically conservative.

---

## 4. Admissibility has the same asymmetry

The `asymmetric_invalid` control contains four deliberately invalid, high-information-looking orientations among sixteen total orientations.

### False positive: reopening just one invalid orientation

500-seed paired result:

- clean gated correctness: **97.2%**;
- with one of four invalid orientations reopened: **17.4%**;
- paired correctness change: **−79.8 pp**;
- 95% CI: **[−83.2, −76.4] pp**.

False-high-confidence decisions increase by **78.4 pp**, CI **[+74.8,+81.8] pp**.

This is intentionally a worst-case adversarial control: the invalid orientation is constructed to look highly informative, so OED is attracted to it.

The result does not claim that real systems will fail this dramatically. It demonstrates the failure mode that admissibility classification is meant to prevent.

### False negative: conservatively rejecting 25% of valid orientations

500-seed paired result:

- clean correctness: **98.0%**;
- 25%-false-negative correctness: **98.0%**;
- paired correctness difference: **0.0 pp**;
- 95% CI: approximately **[−1.0,+1.2] pp**.

95%-success changes by only **−1.0 pp**, with CI crossing zero.

Damage becomes substantial only when most valid orientations are removed: in the 100-seed shape sweep, rejecting 75% of valid orientations reduces correctness to 80%, and rejecting about 90% reduces it to 55%.

### Interpretation

For admissibility, too:

> **false positive > false negative in epistemic danger.**

A practical classifier should prefer `unknown / do not quotient / do not reverse` to an unsupported declaration of admissibility.

---

## 5. Approximate transport has a tolerance region

500-seed paired confirmations show no reliable correctness degradation at transport-noise amplitudes 0.02 or 0.05.

At 0.10:

- correctness decreases by **4.0 pp**;
- 95% CI: **[−6.8, −1.2] pp**;
- 95%-success decreases by **3.6 pp**;
- 95% CI: **[−6.4, −0.8] pp**.

At 0.20:

- correctness decreases by **9.8 pp**;
- false-high-confidence increases by about **2.8 pp**.

At 0.40:

- correctness decreases by **28.2 pp**;
- false-high-confidence increases by **13.6 pp**.

The numerical noise parameter is a synthetic metadata-error amplitude, not a universal physical percentage. The important finding is qualitative: approximate transport can be useful, but it requires explicit error bounds rather than treating a near-equivalence as exact.

---

## 6. New design principle: asymmetric structural classification

The empirical loss structure suggests that orientation classification should use an asymmetric objective.

For equivalence classification, define losses:

`L_merge >> L_split`.

For admissibility:

`L_invalid_as_valid >> L_valid_as_unknown`.

That leads naturally to a three-way decision:

1. **certified equivalent/admissible** — safe to quotient/transport;
2. **certified distinct/invalid** — keep separate or reject;
3. **unknown** — abstain and retain the raw experiment.

This is substantially safer than forcing every orientation pair into a binary same/different classification.

A deployment-oriented objective should therefore optimize something closer to:

`expected compute saving - risk_weighted structural error`.

The structural risk weight should be much larger for false merges and invalid-as-valid decisions than for conservative splits.

---

## 7. Consequence for the mathematics

v0.3 established the exact quotient theorem for certified equivalence.

v0.4 shows why **approximate equivalence cannot simply be treated as exact equivalence**.

The next mathematical object should therefore be a certified relation of the form:

`omega_i ~_(epsilon,delta) omega_j`

where the certificate includes:

- maximum intervention-aligned discrepancy `epsilon`;
- transport uncertainty / calibration error;
- stability or amplification bound;
- admissibility status;
- confidence or proof status.

Quotienting should occur only when the accumulated risk remains under a declared budget.

This turns approximate orientation classification into a **risk-bounded quotient** rather than a heuristic cluster.

---

## 8. Current verdict

### Stronger after v0.4

- Exact equivalence quotienting has real computational value.
- Evidence transport is exact under certified invertible representation transforms.
- Conservative failure to quotient mainly loses efficiency.
- Structural false positives are the critical failure mode.
- Admissibility should be precision-first.

### Still open

- Can real equivalence/admissibility certificates be inferred reliably?
- What discrepancy/stability bounds are sufficient for safe approximate quotienting?
- How does this compare with established symmetry reduction and quotient methods in Bayesian experimental design?
- Does the approach save meaningful cost on external AI, ABM, or scientific-model benchmarks?

## Next gate

Build **certified approximate quotienting**:

`exact quotient -> bounded approximate quotient -> external benchmark`.

The next benchmark should allow OARL to abstain from quotienting whenever the equivalence certificate is not strong enough, then measure whether risk-bounded compression preserves mechanism recovery while retaining useful computational savings.
