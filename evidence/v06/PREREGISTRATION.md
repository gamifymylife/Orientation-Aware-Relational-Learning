# v0.6 External Competitive Gate — Preregistration

Status: **PROSPECTIVE / NO CONFIRMATORY RESULTS YET**

This protocol is frozen before confirmatory execution. Pilot work may be used to debug adapters and arithmetic, but any threshold or algorithm change informed by pilot outcomes requires a new preregistration version and a disjoint confirmatory split.

## Scientific question

> On a third-party causal system that was not constructed around OARL, can a precision-first orientation-equivalence certifier remove genuinely redundant experimental views while preserving mechanism-discriminating information better than simpler structural baselines?

The purpose of this gate is not to show that quotienting known duplicates saves computation. The purpose is to test whether OARL's **discovery / certification / abstention** layer provides incremental utility on independently authored systems.

## Primary external target

The first target is **Microsoft CSuite**, a public suite of causal benchmark datasets generated from independently authored structural equation models (SEMs) with published true causal graphs, observational data, and interventional test environments.

CSuite is treated as third-party evidence because OARL did not define its SEMs, causal graphs, interventions, or benchmark data.

DREAM4 Size100 is retained as a **secondary replication target**, not as the sole external gate, because DREAM4 has already influenced earlier OARL development.

## Blinding and split policy

1. Adapter development may use a named pilot subset only.
2. The confirmatory systems/environments must be disjoint from the pilot subset.
3. Ground-truth graph/SEM information may be used by the evaluator and oracle baseline, but not by OARL or non-oracle baselines during structure discovery.
4. No threshold tuning is permitted on the confirmatory split.
5. Any post-confirmatory algorithm change creates a new version and a new disjoint confirmatory split.

## Experimental object

For each third-party system, define a set of candidate experimental views from the benchmark's existing observed/interventional environments. A view is represented only through evidence available to the competing method.

Two views are considered safely quotientable only if substituting one for the other preserves the preregistered mechanism-discrimination target within tolerance. Ground-truth equivalence/distinction labels are computed by the evaluator from the independently defined benchmark mechanism and intervention semantics, not from OARL scores.

No synthetic OARL class labels may enter the external evaluator.

## Competitors

Every method receives the same pilot/confirmatory split and evidence budget.

1. **No quotient / Generic OED** — every experimental view remains distinct.
2. **Oracle quotient** — evaluator ground truth; upper bound, not a learnable competitor.
3. **Exact duplicate canonicalization** — merge only byte/numerically identical view signatures.
4. **Generic similarity clustering** — cluster views from normalized predictive signatures with thresholds calibrated only on pilot data.
5. **Symmetry / canonical transform baseline** — use only transformations known a priori from benchmark representation metadata; no learned OARL certificate.
6. **Behavioral-equivalence baseline** — merge views whose empirical response distributions are statistically indistinguishable under a frozen two-sample criterion.
7. **Non-abstaining classifier** — a forced binary equivalent/distinct comparator using the same evidence family as the OARL certifier.
8. **OARL precision-first certifier** — `EQUIVALENT`, `DISTINCT`, or `UNKNOWN`; only `EQUIVALENT` creates quotient merges.

If a baseline cannot naturally apply to a target, that non-applicability must be reported rather than silently omitted.

## Primary safety endpoint

The primary endpoint is **false-merge rate among truly distinct view pairs**.

A false merge is any accepted equivalence that causes the evaluator to collapse views that differ on the preregistered mechanism-discrimination target.

Primary OARL gate:

- false-merge rate <= 0.1% on confirmatory distinct pairs;
- and no statistically supported evidence that OARL's false-merge rate exceeds the safest nontrivial baseline.

Zero observed false merges is preferred but is not asserted as a universal requirement when the confirmatory population is large enough to estimate a tight upper bound.

## Secondary structure endpoints

Report for every learnable competitor:

- pairwise equivalence precision;
- pairwise equivalence recall;
- abstention / unmerged coverage;
- number of discovered quotient classes;
- compression fraction;
- accepted transport / mapping errors where applicable.

OARL may trade recall for precision. A high-recall method that creates materially more false merges is not considered superior under this protocol.

## Downstream endpoints

Run the same mechanism-identification / intervention-selection task over each learned quotient.

Report:

- final mechanism / graph discrimination accuracy;
- false-high-confidence decisions;
- number of experimental acquisitions;
- acquisition-score evaluations;
- certificate evidence cost;
- certification compute;
- total wall-clock runtime;
- total end-to-end cost under explicitly stated cost weights.

## Incremental-utility criterion

OARL does **not** pass merely by being safe.

At least one confirmatory regime must establish an incremental advantage over all applicable non-oracle baselines on the Pareto frontier of:

1. false-merge risk;
2. downstream mechanism-discrimination preservation;
3. compression / acquisition reduction;
4. total end-to-end cost.

A legitimate pass may therefore be of the form:

> At matched false-merge risk, OARL preserves downstream mechanism discrimination while achieving materially greater compression or lower total cost than generic similarity, canonicalization, and behavioral-equivalence baselines.

## Kill / narrowing outcomes

The major-methodological-advantage claim is rejected or narrowed if any of the following holds:

- a simpler baseline matches or dominates OARL on safety and efficiency;
- OARL false merges materially degrade downstream causal/mechanism identification;
- OARL's abstention is so high that no useful compression remains;
- certification cost erases the search savings in all tested regimes;
- performance depends on representation assumptions absent from the third-party benchmark;
- the result cannot be reproduced from pinned third-party data and a frozen adapter.

A failed gate is an informative scientific result and must be preserved.

## Reporting discipline

The confirmatory report must clearly separate:

- external facts supplied by the benchmark;
- evaluator-derived ground truth;
- OARL outputs;
- baseline outputs;
- pilot findings;
- confirmatory findings.

Do not describe a CSuite result as real-world causal discovery; CSuite is independently authored but synthetic. The stronger claim tested here is **external construction-family generalization**, not real-world validation.
