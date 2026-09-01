# v0.6.4 evaluator and accounting correction

## Status

The frozen v0.6.4 code, preregistration and result remain preserved. This note narrows their interpretation after the independently versioned v0.6.5 analytic audit.

## What remains valid

v0.6.4 reproducibly showed that, under its frozen finite-difference evaluator and finite-shot estimator:

- response-space TV-UCB compressed aggressively and made 1,196 evaluator-defined false merges;
- FIM-POINT accepted 21 shortlisted pairs with zero observed evaluator-defined false merges;
- FIM-UCB and OARL-TASK-XFIT accepted no equivalences;
- the learned conservative methods therefore produced no downstream computational saving.

No threshold or frozen v0.6.4 artifact has been rewritten.

## What is corrected

### 1. The evaluator was numerical, not exact

`exact_true_fims` used central finite differences with step `1e-4`. The v0.6.5 analytic `SO(3)` audit shows that this fragments theoretically identical zero-Fisher circuits when paired with a purely relative distance whose denominator is near zero.

On the 254 physical circuits used by v0.6.4:

- analytic exact/operational classes: **58**;
- legacy finite-difference operational classes: **91**;
- analytically exact equivalent physical pairs: **4,158**;
- pairs retained by the legacy evaluator: **897**;
- analytically exact pairs missed by the legacy evaluator: **3,261**.

Accordingly, `508 -> 91` is the output of the frozen legacy evaluator, not the correct exact structural quotient.

### 2. Known outcome relabelling was mixed with learned compression

The 508 views were 254 physical circuits duplicated under ordinary and complement outcome conventions. That deterministic `508 -> 254` canonicalization must be reported separately and cannot count as learned-discovery utility.

### 3. Shot accounting was implementation-specific

The frozen implementation simulated 1.9304B independent view-level shot units. Because ordinary and complement outcomes can be derived from the same physical Bernoulli observations, faithful shared-observation accounting is 965.2M physical shot units. The 1.9304B number remains the cost of the frozen implementation, not a necessary physical acquisition cost.

## Revised interpretation

v0.6.4 shows that its selected noisy derivative estimator and bootstrap envelope were unusable under its own numerical evaluator. It does **not** establish that finite evidence is the fundamental bottleneck for the pyGSTi family. v0.6.5 shows that generic analytic structural transport exhausts the held-out oracle without finite evidence.

See `evidence/v065/V065_RESULT.md` for the prospective held-out correction.
