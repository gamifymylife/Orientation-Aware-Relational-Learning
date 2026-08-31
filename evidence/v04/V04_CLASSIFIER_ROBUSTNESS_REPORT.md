# Orientation-Aware Benchmark v0.4 — Structural Classifier Robustness

## Purpose

v0.3 showed that exact, correct orientation equivalence classes can reduce redundant OED search without changing the mechanism-identification result. v0.4 asks the obvious next question:

> **How wrong can the structural classifier be before quotienting or admissibility gating becomes dangerous?**

The benchmark separates four error types:

- false merges — genuinely different orientations incorrectly declared equivalent;
- false splits — equivalent orientations kept separate;
- admissibility false positives — invalid orientations incorrectly allowed;
- admissibility false negatives — valid orientations conservatively rejected.

Transport-map noise is tested separately.

## False merges are dangerous

In the 500-seed paired confirmation, incorrectly merging only **one of eight true classes** changed:

- clean correctness: **94.6%**
- one-false-merge correctness: **86.0%**
- paired difference: **−8.6 percentage points**
- bootstrap 95% CI: **[−11.4, −5.8] pp**

95%-identification success fell by approximately **10 pp**, and false-high-confidence decisions increased.

A false equivalence declaration therefore destroys a genuine experiment distinction; it is not merely a lost efficiency opportunity.

## False splits are comparatively safe

With 24 raw orientations and four true equivalence classes, progressively splitting true classes produced:

| False-split rate | Declared classes | Correctness | 95%-success | Mean score evaluations |
|---:|---:|---:|---:|---:|
| 0% | 4 | 72% | 42% | 1,130 |
| 25% | 9 | 72% | 42% | 2,543 |
| 50% | 14 | 72% | 42% | 3,956 |
| 75% | 19 | 72% | 42% | 5,369 |
| 100% | 24 | 72% | 42% | 6,782 |

Accuracy remains unchanged; the computational advantage disappears.

A false split therefore behaves like conservative abstention: keep the views separate when equivalence is uncertain.

## Admissibility is similarly asymmetric

The adversarial `asymmetric_invalid` control contains four invalid, high-information-looking orientations among sixteen.

Reopening only **one of four invalid orientations** in the 500-seed paired test changed:

- clean gated correctness: **97.2%**
- corrupted correctness: **17.4%**
- paired difference: **−79.8 pp**
- bootstrap 95% CI: approximately **[−83.2, −76.4] pp**

This is deliberately a worst-case stress test; it demonstrates a failure mode rather than estimating its real-world frequency.

By contrast, conservatively rejecting **25% of valid orientations** changed correctness from **98.0% to 98.0%**, with the interval spanning zero.

## Approximate transport

Transport-parameter noise of 0.02–0.05 produced no reliable correctness loss in 500 paired seeds. At 0.10, correctness fell by about **4.0 pp** with a 95% CI of roughly **[−6.8, −1.2] pp**. Larger corruption produced progressively larger damage.

The synthetic noise amplitude is not a universal physical percentage; the result establishes that approximate transport requires explicit error bounds rather than silently treating near-equivalence as exact.

## Design principle

The loss structure is asymmetric:

`L_false_merge >> L_false_split`

and

`L_invalid_as_valid >> L_valid_as_unknown`.

The practical structural classifier should therefore support three states:

1. **certified equivalent/admissible** — safe to quotient or transport;
2. **certified distinct/invalid** — keep separate or reject;
3. **unknown** — abstain and retain the raw experiment.

This motivates **certified approximate quotienting** rather than heuristic clustering.

## Current verdict

Supported in controlled benchmarks:

- exact equivalence quotienting has computational value;
- exact evidence transport preserves posterior inference;
- conservative failure to quotient mainly loses efficiency;
- false structural positives are the critical failure mode;
- admissibility should be precision-first.

Still open:

- reliable certificates on real systems;
- sufficient discrepancy/stability bounds for approximate quotienting;
- comparison with established symmetry/quotient methods in experimental design;
- external computational advantage on third-party scientific benchmarks.
