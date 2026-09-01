# v0.6.5 result — structural baseline and evaluator audit

## Outcome

**STRUCTURAL-BASELINE UTILITY GATE PASSED. LEARNED-DISCOVERY SUITABILITY GATE FAILED.**

On the held-out depth-8 family, deterministic outcome canonicalization first reduced 512 labelled views to 256 physical circuits. Generic analytic orientation transport then reduced the 256 physical circuits to **50 exact Fisher classes** with:

- zero exact false merges;
- **80.47% compression beyond view canonicalization**;
- 90.23% total view-level compression;
- exactly the RAW D-optimal logdet and selected depth cost;
- 400 rather than 4,096 downstream score evaluations;
- zero Bernoulli evidence shots.

The evaluator-only operational oracle also contained exactly **50 classes**. It added no compression beyond the generic structural baseline. The preregistered learned-discovery suitability gate therefore failed and the adaptive OARL stage was correctly not run.

This is not an OARL algorithm win. It is evidence that this pyGSTi family becomes trivial for a generic model-based canonicalizer once its known gate structure is admitted.

## Frozen held-out setting

- pyGSTi 0.10.2 / `smq1Q_XYI`;
- development evidence: all depth-1–7 results through v0.6.4;
- confirmatory family: all 256 `Gxpi2/Gypi2` words at exactly depth 8;
- 512 ordinary/complement view labels;
- analytic integer/half-integer `SO(3)` orientation transport;
- identical 8-step D-optimal optimizer for every valid partition;
- no finite-shot threshold tuning and no post-result method change.

## Main result

| Method | Classes | View-level compression | Compression beyond 256 physical circuits | Exact false merges | D-opt logdet | Score evaluations | Bernoulli shots |
|---|---:|---:|---:|---:|---:|---:|---:|
| RAW-VIEWS | 512 | 0.00% | — | — | 12.3273695 | 4,096 | 0 |
| VIEW-CANONICAL | 256 | 50.00% | 0.00% | 0 | 12.3273695 | 2,048 | 0 |
| STRUCTURAL-TRANSPORT | **50** | **90.23%** | **80.47%** | **0** | **12.3273695** | **400** | **0** |
| OPERATIONAL-ORACLE | **50** | **90.23%** | **80.47%** | **0** | **12.3273695** | **400** | 0 |

The exact and thresholded operational relations were identical on this held-out family: both contained 4,667 unordered equivalent pairs and 50 classes.

## Relation-integrity audit

Both the exact structural relation and the operational relation passed:

- reflexivity;
- symmetry;
- transitivity.

The order audit evaluated the original insertion order plus 256 deterministic shuffles. Every order produced:

- 50 classes;
- D-opt logdet 12.3273695;
- selected depth cost 64.

The term **equivalence classes** is therefore justified for this particular held-out relation. The code no longer assumes that an arbitrary thresholded compatibility relation is transitive.

## v0.6.4 evaluator correction

The retrospective development audit found that the v0.6.4 central finite-difference evaluator fragmented genuine zero-information equivalence classes.

Among the 254 physical depth-1–7 circuits:

| Evaluator | Physical classes | Equivalent physical pairs |
|---|---:|---:|
| Analytic orientation transport | **58** | **4,158** |
| Legacy `1e-4` finite difference | 91 | 897 |

The legacy evaluator missed **3,261 of 4,158** analytically exact equivalent physical pairs. It introduced no spurious equivalent pairs in this comparison, but it converted numerical noise around true zero Fisher matrices into apparent relative differences.

Consequently, the v0.6.4 `508 -> 91` figure remains the reproducible output of its frozen numerical evaluator, but it is not the correct exact structural quotient. After deterministic view canonicalization, the corrected analytic depth-1–7 result is:

```text
508 labelled views
    -> 254 physical circuits
    -> 58 exact structural Fisher classes
```

## Held-out numerical audit

The independent pyGSTi finite-difference matrices agreed extremely closely with analytic matrices for nonzero Fisher circuits, but the relative comparison remained unstable around exact zeros.

| FD step | Max absolute error | Max relative error on nonzero FIM | Analytic zero-FIM circuits | True pairs missed by FD operational relation |
|---:|---:|---:|---:|---:|
| `1e-3` | 3.725e-3 | 3.200e-5 | 94 | 4,007 |
| `1e-4` | 8.543e-6 | 3.200e-7 | 94 | 3,787 |
| `1e-5` | 8.534e-8 | 3.199e-9 | 94 | 3,595 |

Shrinking the finite-difference step reduces absolute error but does not repair a relative metric whose denominator is effectively zero. This was an evaluator-conditioning problem, not evidence that the underlying circuits were distinct.

## Evidence-cost correction

The frozen v0.6.4 procedure did simulate 1,930,400,000 independent **view-level** Bernoulli shot units:

```text
508 views × 19 probes × 2 splits × 100,000 shots.
```

However, ordinary and complement views are deterministic relabellings of the same binary physical observations. A physically shared accounting is therefore:

```text
254 physical circuits × 19 probes × 2 splits × 100,000 shots
= 965,200,000 physical shot units.
```

The original cost remains correct for the inefficient frozen implementation, but it overstated the physically necessary acquisition burden by exactly 2×.

## Scientific interpretation

v0.6.4 did not isolate finite-evidence certifiability as cleanly as previously stated. Its zero-compression result combined four effects:

1. deterministic outcome relabellings were sampled independently;
2. local derivatives were estimated from noisy finite probes;
3. the supposed exact oracle used numerically unstable finite differences near zero Fisher norm;
4. the benchmark's public gate structure already permits exact analytic transport.

Once the known structure is represented correctly, the redundancy is recovered with no Bernoulli evidence and no learned discovery. Therefore the proposed adaptive v0.6.5 learner would have been solving an artificial problem and could not establish OARL-specific utility against the proper generic baseline.

## Claim boundary

This result supports:

- exact orientation transport as a powerful canonicalization mechanism in this ideal Clifford family;
- the need to separate known relabelling, known model-based structure and genuinely learned equivalence;
- analytic or well-conditioned evaluators when zero-information candidates are present;
- mandatory transitivity and order-sensitivity audits before using quotient language.

This result does **not** establish:

- an OARL-specific algorithmic advantage;
- learned finite-noise equivalence discovery;
- a general solution outside known Clifford structure;
- superiority over established analytic sensitivity, symmetry reduction or canonicalization methods.

The next external benchmark must contain redundant admissible views whose safe transformations are not already given by metadata or exactly computable from the public model.
