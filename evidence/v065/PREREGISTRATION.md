# v0.6.5 preregistration — structural baseline and evaluator audit

**Status:** frozen before inspecting any held-out depth-8 pyGSTi evaluator output.

## Why this correction is required

v0.6.4 mixed two different sources of compression:

1. every physical circuit was represented twice, once under the ordinary binary outcome convention and once under its deterministic complement;
2. different physical circuits could have the same or sufficiently similar Fisher contribution for the downstream D-optimal task.

The first source is known canonicalization, not learned equivalence discovery. It gives a `508 -> 254` reduction by construction and must not count toward an OARL utility gate.

The v0.6.4 evaluator also called central finite-difference Fisher matrices “exact.” That language was too strong. Relative distances can be numerically unstable when the true Fisher norm is zero or nearly zero. v0.6.5 therefore uses an analytic orientation-transport evaluator for the ideal Clifford gate family and treats pyGSTi finite differences as an independent numerical cross-check only.

## Decisive questions

1. After deterministic outcome-label canonicalization is removed from the claimed gain, how much exact task redundancy remains among physical circuits?
2. Can a generic, domain-known orientation-transport canonicalizer recover that redundancy without Bernoulli evidence?
3. Does a material residual oracle opportunity remain after this generic structural baseline, such that a learned adaptive OARL certificate would have a legitimate target?

If generic structural transport exhausts the opportunity, this benchmark is unsuitable for establishing an OARL-specific learned-discovery advantage. That is a valid suitability failure, not an OARL algorithm pass.

## Development / confirmation separation

- Depths 1–7 and all v0.6.4 outputs are development evidence.
- The confirmatory family is all 256 `Gxpi2/Gypi2` words at exactly depth 8.
- No held-out depth-8 pyGSTi probabilities, finite-difference Fisher matrices, class counts or D-optimal outputs may be inspected before this protocol is committed.
- The analytic transport rule is fixed from the public ideal gate semantics and the v0.6.4 mechanism parameterization, not fitted to held-out evaluator output.

## Candidate accounting

- physical circuits: 256;
- binary outcome conventions per circuit: 2;
- raw view-level candidates: 512;
- deterministic view canonicalization baseline: 256 physical candidates.

All headline compression beyond known canonicalization uses 256—not 512—as its denominator.

## Exact analytic evaluator

Use the Bloch-vector representation with initial and measured axis `z`. The ideal gates are the integer `SO(3)` quarter-turn matrices `A_x` and `A_y`. The uniform coherent perturbation is represented by the three infinitesimal rotation generators `L_a`.

For a circuit word with gates `A_k`, propagate

```text
v_0 = z
D_0,a = 0
v_k = A_k v_(k-1)
D_k,a = L_a v_k + A_k D_(k-1),a
```

and compute

```text
p_0 = (1 + z^T v_n) / 2
g_a = (z^T D_n,a) / 2
F = g g^T / max(p_0 (1-p_0), 1e-8).
```

For this ideal Clifford family the state, derivative and Fisher signatures are exactly representable with integers or half-integers. Exact structural equivalence is equality of the resulting analytic Fisher matrices. This relation must pass reflexivity, symmetry and transitivity checks before the term “equivalence classes” or “quotient” is used.

## Independent pyGSTi numerical audit

For every held-out circuit, compute pyGSTi central finite-difference Fisher matrices at steps `1e-3`, `1e-4` and `1e-5`. Report:

- maximum and median absolute matrix error against the analytic evaluator;
- maximum relative error restricted to analytic Fisher norm greater than `1e-9`;
- the number and maximum numerical norm of analytically zero-Fisher circuits;
- pair-relation disagreements caused by finite-difference evaluation.

The analytic evaluator is authoritative. The finite-difference audit cannot redefine the frozen exact relation.

## Methods

1. **RAW-VIEWS** — all 512 ordinary/complement views.
2. **VIEW-CANONICAL** — pair ordinary/complement views by known physical-circuit identity; no learned-discovery credit.
3. **STRUCTURAL-TRANSPORT** — generic analytic orientation transport from the public gate semantics, grouping physical circuits only when analytic Fisher signatures are exactly equal.
4. **OPERATIONAL-ORACLE** — evaluator-only relation using analytic Fisher distortion `d_F <= 0.20` and D-optimal anchor distortion `d_D <= 0.05`.

`STRUCTURAL-TRANSPORT` is a generic model-based baseline, not an OARL-specific method. Learned methods are not allowed to claim its known-structure gain.

## Operational-relation integrity

The thresholded operational relation is tested for reflexivity, symmetry and transitivity on the held-out family.

- If transitive, its connected components may be reported as operational equivalence classes.
- If non-transitive, it is reported only as a pairwise safe-substitution graph. No order-dependent greedy partition may be called an oracle quotient.

The script also evaluates 256 deterministic shuffled insertion orders as a regression check; any class-count or downstream variation is reported.

## Downstream task

Every valid partition uses the identical 8-step greedy D-optimal selector with replacement in the same three coherent-rotation coordinates, ridge `1e-9` and deterministic tie-breaking by circuit index.

Report:

- final analytic D-optimal log determinant;
- selected total depth cost;
- score evaluations;
- selected circuit words;
- wall-clock runtime.

## Frozen gates

### Structural-baseline utility gate

`STRUCTURAL-TRANSPORT` passes only if all are true:

1. zero exact false merges;
2. at least 20% compression beyond the 256-circuit `VIEW-CANONICAL` baseline;
3. final D-optimal logdet loss versus `VIEW-CANONICAL` no greater than `0.005`;
4. selected depth cost no greater than `VIEW-CANONICAL`;
5. zero Bernoulli evidence shots.

Passing this gate supports known structural canonicalization only.

### Learned-discovery suitability gate

A learned adaptive OARL stage is warranted on this family only if the valid `OPERATIONAL-ORACLE` contains at least 20% additional class compression beyond `STRUCTURAL-TRANSPORT` while preserving the downstream tolerance.

If this residual-opportunity gate fails, v0.6.5 stops after the structural audit. The repository must state that pyGSTi does not provide a nontrivial remaining target for learned OARL discovery once known structural transport is admitted.

### OARL-specific claim gate

No OARL-specific algorithmic advantage may be claimed from v0.6.5 unless a separately preregistered learned method strictly improves the zero-false-merge compression/cost frontier over `STRUCTURAL-TRANSPORT` and generic sequential baselines on a family that passes the learned-discovery suitability gate.

## Cost accounting

Report separately:

- raw view candidates;
- physical candidates after deterministic view canonicalization;
- structural transport updates;
- Bernoulli evidence shots;
- downstream score evaluations;
- wall-clock runtime.

The v0.6.4 reference burden remains 1,930,400,000 nominal Bernoulli shot units, but v0.6.5 also reports the corrected shared-physical-observation interpretation. Deterministic outcome relabelling cannot be charged as a second independent physical experiment.

## Integrity

A negative result, evaluator correction or benchmark-suitability failure is valid output and must not fail CI. CI failure is reserved for execution or artifact-integrity errors. No threshold or method rule may be changed after held-out output is inspected; any changed experiment becomes v0.6.6 or later.
