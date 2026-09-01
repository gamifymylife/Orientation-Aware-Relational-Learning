# v0.6.1 Finite-Shot Competitive Gate — Confirmatory Report

Status: **COMPLETE — PRIMARY SAFETY GATE FAILED**

Frozen preregistration: `evidence/v061/FINITE_SHOT_PREREGISTRATION.md`.

Confirmatory runner: `scripts/run_v061_finite_shot_gate.py`.

Held-out seeds: **1000–1299**. Total classifications per method: **9,600**.

The first CI attempt stopped before producing scientific results because ideal pyGSTi probabilities contained floating-point roundoff a few ulps outside `[0,1]`, which NumPy correctly rejected as binomial parameters. The repair clips only values within `1e-10` of the probability boundary and raises on any material excursion. No scientific threshold, seed, pair construction, shot budget, equivalence margin or classifier rule was changed.

## Result

The preregistered strong gate **did not pass**.

| method | operational precision | operational recall | operational false merges | abstention |
|---|---:|---:|---:|---:|
| raw parameter distance | n/a | 0.0000 | 0 | 0.0000 |
| generic probability equivalence | 0.7497 | 0.9908 | 1,191 | 0.0044 |
| OARL cross-fit + depth stability | **0.8355** | 0.7364 | **522** | 0.1695 |

OARL substantially improved precision and reduced unsafe merges relative to the generic comparator, but it still accepted **522** pairs whose sealed-circuit maximum probability difference exceeded the frozen operational tolerance `epsilon = 0.020`. Therefore the primary zero-false-merge safety criterion failed.

This is a real negative result. It must not be converted into a pass by post-hoc threshold tuning.

## Where the failure occurs

The decisive boundary case is the `op_noise = 0.010` physical perturbation.

Its maximum sealed-circuit difference is:

`0.0292599253 > epsilon = 0.020`.

Yet the shallow discovery circuits do not expose that distinction strongly enough for the frozen certificate to reject it reliably.

Observed OARL false merges for this one boundary class:

| shots/model/circuit | OARL false merges / 300 | generic false merges / 300 |
|---:|---:|---:|
| 50,000 | 0 | 291 |
| 100,000 | 58 | 300 |
| 250,000 | 182 | 300 |
| 500,000 | 282 | 300 |

All OARL false operational merges in the confirmatory grid come from this `0.010` perturbation class. Larger perturbations (`0.020` and above) are correctly called distinct. Smaller physical perturbations (`0.002` and `0.005`) remain inside the frozen sealed epsilon band and are therefore operationally equivalent even though they are not physically identical.

## The important scientific pattern

More samples make the boundary failure **worse**, not better.

That is not a paradox. Sampling noise is not the limiting problem here. The limiting problem is the **observational boundary**.

The shallow circuit family (depth 0–3) makes the `0.010` physical perturbation look epsilon-equivalent. The sealed deeper circuit family (depth 4–6) amplifies the same mechanism difference beyond epsilon. As shot count increases, both the generic comparator and the current OARL certificate become increasingly confident about what the shallow boundary says — and therefore increasingly willing to make a merge that fails under the deeper boundary.

In compact form:

```text
more evidence inside an insufficient boundary
            does not
recover distinctions outside that boundary
```

This is directly relevant to the motivating OARL thesis, but it is **not** evidence that the present OARL certifier solves the problem. The benchmark has exposed a failure mode the current method still needs to address.

## What did survive

Three narrower conclusions survive.

1. **Raw representation distance is unusable here.** The gauge-naive threshold accepted zero operationally equivalent pairs. Independently gauge-transformed representations can be far apart internally while remaining observationally equivalent.
2. **Precision-first abstention helps.** OARL reduced operational false merges from 1,191 to 522 and raised aggregate precision from 0.7497 to 0.8355.
3. **The simple depth-stability heuristic is insufficient.** It helps at moderate shot counts but converges toward the same unsafe shallow-boundary conclusion as measurement noise disappears.

At 100,000 shots OARL achieved precision **0.9362** with recall **0.9456**, versus generic precision **0.7500** and recall **1.0000**. That is useful descriptive evidence of a better local safety/recall tradeoff, but it does not override the preregistered zero-false-merge requirement.

## Interpretation

The strongest interpretation is not “OARL failed as an idea.” It is narrower and more useful:

> **Equivalence certification is boundary-relative. A certifier cannot safely extrapolate equivalence beyond the observational family on which it was certified unless it also models how distinctions evolve as that boundary changes.**

The current cross-fit certificate addresses finite-sample uncertainty. It does not adequately address **boundary extrapolation uncertainty**.

That is now the next technical problem.

## What not to do next

Do not simply lower `DEPTH_SLOPE_LIMIT` until this confirmatory set passes. That would overfit the held-out evidence and invalidate the prospective claim.

Do not add sealed circuits to the discovery set and declare success. That would remove the exact hidden-boundary challenge the experiment revealed.

Do not relabel the `0.010` physical controls as equivalent. Their sealed behavior violates the preregistered epsilon criterion.

## Recommended next experiment: v0.6.2 boundary extrapolation

Freeze a new prospective protocol on fresh seeds and compare methods that explicitly estimate **how behavioral divergence changes with observational depth**.

Candidate OARL rule:

1. estimate pairwise difference by depth;
2. fit a conservative growth envelope rather than a raw slope threshold;
3. propagate uncertainty forward to a preregistered unseen depth horizon;
4. accept `EQUIVALENT` only if the upper extrapolated envelope remains below epsilon;
5. otherwise return `UNKNOWN` unless observed evidence already establishes `DISTINCT`.

Crucially, compare this against equally strong generic baselines: linear trend extrapolation, isotonic/monotone envelope, polynomial regression, and a simple worst-case Lipschitz growth bound. OARL only earns distinctive utility if its relational formulation beats those baselines on fresh held-out seeds.

## Claim boundary after v0.6.1

Supported:

> In an independently authored GST domain, gauge-equivalent internal representations can be observationally identical while physically distinct models can become distinguishable only as the experimental boundary changes. A conservative OARL-style cross-fit certificate improves the precision/false-merge tradeoff over direct shallow probability equivalence, but the frozen v0.6.1 method does not safely extrapolate equivalence to unseen deeper circuits.

Not supported:

- zero-false-merge finite-shot external certification;
- safe extrapolation beyond the discovery boundary;
- distinctive superiority over generic structural extrapolation baselines;
- physical identity from finite observational equivalence;
- broad real-world generalization.
