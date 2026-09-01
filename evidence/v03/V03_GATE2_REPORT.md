# Orientation-Aware Benchmark v0.3 — Structural Gate-2 Report

## Executive result

v0.2 falsified the additive scoring rule

`IG - lambda*log(1+K) - gamma*C`.

v0.3 tests a different claim: **can known relational orientation structure remove redundant search or block structurally invalid interrogations without sacrificing mechanism identification?**

The answer in the controlled benchmark is **yes** for exact equivalence quotienting and exact admissibility metadata.

This is not yet evidence that a learned orientation classifier will recover those structures reliably in external systems. v0.3 assumes the structural metadata is correct and tests its downstream value.

---

## 1. Exact orientation quotienting

The `equivalent_redundancy` regime creates raw orientations grouped into exact equivalence classes. Members of a class differ by:

- a bijective intervention permutation;
- an invertible scalar observation transform `y_raw = s*y_canonical + b`;
- the corresponding noise-scale transform.

Thus they are different presentations of the same likelihood experiment.

### Proposition 1 — Information gain is invariant inside an exact orientation class

Let experiments `e` and `e'` satisfy

`Y' = phi(Y)`

for a bijection `phi` independent of the hidden mechanism `H`, with likelihoods related by the appropriate change of variables. Then

`I(H;Y' | e') = I(H;Y | e)`.

Therefore generic information-gain OED over all raw orientations factors through the quotient set of equivalence classes:

`argmax_(omega,a) I(H;Y|omega,a)`

can be replaced, without loss, by search over

`argmax_([omega],a) I(H;Y|[omega],a)`.

If there are `O` raw orientations, `C` equivalence classes, and `A` interventions, score evaluation falls from

`O*A`

to

`C*A`.

The ideal score-evaluation reduction is therefore

`1 - C/O`.

### Proposition 2 — Posterior evidence transport is exact

For equivalent experiments linked by an invertible observation transform, the likelihood Jacobian is independent of `H` and cancels during Bayesian normalization. Consequently, updating from the raw observation or transporting it to the canonical representative produces the same posterior over mechanisms.

This is tested directly in `test_transport_update_matches_raw_update`.

---

## 2. Confirmatory quotient result — 100 held-out seeds

Configuration:

- 12 mechanisms;
- 24 raw orientations;
- 4 exact equivalence classes;
- 12 interventions;
- budget 30.

The fair exhaustive baseline is `generic_cost_tiebreak`: it evaluates every admissible raw experiment, recognizes equal-information ties numerically, and chooses the cheapest tied experiment. `structured_oarl` obtains the same decision by scoring one canonical representative per equivalence class and then using structural transport to execute the cheapest equivalent raw experiment.

Results:

- paired final correctness identical: **100/100 worlds**;
- paired `N95` identical: **100/100 worlds**;
- paired penalized `C95` identical: **100/100 worlds**;
- median score-evaluation reduction: **83.3%**;
- mean score evaluations: **6537.6 -> 1089.6**.

This is a computational advantage, not a sample-efficiency advantage. The method returns the same mechanism-identification result while avoiding redundant acquisition scoring.

### Why evidence transport matters

`structured_rep_oed`, which searches the same quotient but is forced to execute only the canonical representative, has the same identification performance but substantially higher experimental cost. `structured_oarl` uses the equivalence map to select a cheaper equivalent physical orientation and transport its evidence canonically.

In this run, median penalized `C95` was:

- structured representative only: **43.20**;
- structured OARL with transport: **17.62**;
- exhaustive Generic-OED with cost tie-break: **17.62**.

Thus transport does not outperform an exhaustive baseline that checks every raw equivalent action and cost; it achieves the same cost while avoiding the exhaustive scoring work.

---

## 3. Scaling result

With four equivalence classes held fixed while the number of raw orientations increases:

| Raw orientations | Ideal/observed score-evaluation reduction |
|---:|---:|
| 8 | 50.0% |
| 16 | 75.0% |
| 32 | 87.5% |
| 64 | 93.75% |
| 128 | 96.875% |
| 256 | 98.4375% |

Using the cheap vectorized IG proxy, runtime savings are smaller because NumPy can score many experiments cheaply; median runtime reduction reaches roughly **25% at 256 raw orientations**.

Using 12-point Gauss-Hermite mutual-information quadrature, computational savings track the quotient almost directly:

| Raw orientations | Score-eval reduction | Median runtime reduction |
|---:|---:|---:|
| 16 | 75.0% | ~74.9% |
| 32 | 87.5% | ~87.4% |
| 64 | 93.75% | ~93.7% |

This is the clearest current Gate-2 result: structural equivalence can reduce the computational cost of experiment selection when scoring experiments is expensive.

---

## 4. No-structure negative control

In `standard`, every orientation is its own equivalence class and every orientation is admissible.

Across 100 held-out seeds:

- Generic cost-tiebreak OED and Structured OARL have identical success and correctness;
- median `C95` is identical;
- score evaluations are identical;
- quotient reduction is exactly **0%**.

So the implementation does not create a computational advantage where no structural redundancy exists.

---

## 5. Admissibility/asymmetry stress test

The `asymmetric_invalid` regime is an intentionally adversarial control. A subset of orientations advertises very high nominal information gain but is declared structurally inadmissible; observations queried through those orientations follow incompatible semantics.

Across 100 held-out seeds:

- unrestricted Generic OED: **0% final correctness**;
- unrestricted Generic OED: **100% false-high-confidence rate**;
- Structured OARL with admissibility gate: **98% final correctness**;
- Structured OARL: **0% false-high-confidence rate**;
- mean inadmissible queries by Generic OED: **29.82**;
- mean inadmissible queries by Structured OARL: **0**.

A generic OED baseline supplied with the same admissibility mask performs equivalently to structured OARL in this regime. Therefore the result should be interpreted narrowly:

> **Correct admissibility information is valuable; the current benchmark does not show that OARL is uniquely capable of using an admissibility mask.**

The scientific burden moves upstream: can the relational orientation classifier infer admissibility accurately enough to make this metadata trustworthy?

---

## 6. Gate-2 verdict

### Demonstrated

1. Exact orientation equivalence creates redundant OED computations.
2. Mutual-information optimization can be performed over orientation equivalence classes without changing the optimum.
3. Exact evidence transport preserves the Bayesian posterior.
4. In controlled worlds, quotienting reduces acquisition-score evaluations by the predicted factor while preserving identification, experiment count, and fair cost.
5. The advantage grows with raw orientation redundancy and becomes substantial in wall-clock time when information-gain evaluation is expensive.
6. Correct admissibility gating prevents catastrophic use of deliberately invalid orientations.

### Not demonstrated

1. That the equivalence/admissibility classifier can be learned reliably from real systems.
2. That orientation quotienting is novel relative to existing symmetry-reduction or experimental-design methods.
3. That external AI, ABM, or scientific mechanism-discovery tasks contain enough exploitable orientation redundancy to generate large practical savings.
4. That approximate equivalence can be quotiented safely.
5. That incorrect structural metadata is harmless.

---

## 7. Next falsification target

v0.4 should attack the assumption that structural metadata is perfect.

Inject controlled errors into the orientation classifier:

- **false merges:** non-equivalent orientations classified as equivalent;
- **false splits:** equivalent orientations left separate;
- **false admissibility positives:** invalid orientations allowed;
- **false admissibility negatives:** useful orientations rejected;
- approximate rather than exact transport.

Then map the trade-off:

`computational saving vs mechanism-identification damage`.

The critical practical question becomes:

> **How accurate must orientation classification be before quotienting is worth using?**

That threshold is likely more important for deployment than another positive synthetic benchmark.
