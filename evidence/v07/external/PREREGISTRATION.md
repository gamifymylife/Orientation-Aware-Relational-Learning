# v0.7 External Complementarity Gate — preregistration

## Status

**FROZEN DESIGN / NO v0.7 EXTERNAL OARL OUTCOMES RUN.**

This programme tests whether the structural mechanism isolated in the supporting synthetic gate earns its keep on previously unseen real software/AI regressions. Candidate selection, A/B revisions, evaluator definitions and the policy implementations must be frozen before external OARL results are inspected.

## Primary question

> On previously unseen real software/AI regressions, does explicitly modeling relations among observational perspectives reduce the cost of reaching a warranted diagnosis compared with strong generic adaptive test selection?

## Unit of analysis

A case is one historical regression with:

- pinned pre-fix and post-fix revisions;
- an evaluator that reproduces the historical behavioral distinction without live nondeterministic services where avoidable;
- a bounded candidate orientation/probe language available unchanged to every policy;
- an explicit decision target and an `UNKNOWN` outcome when the supplied observation family is insufficient.

An orientation may correspond to a component, request class, execution stage, tool state, environment configuration, trace slice, perturbation or intervention. A probe is an executable orientation/intervention choice. Case adapters may not expose repository names, PR numbers, witness locations or hidden evaluator labels to the acquisition policies.

## Corpus

Target **24** untouched cases; minimum **20** required to launch the confirmatory gate. Prefer multiple frameworks and regression families. Cases previously used to design or inspect OARL complementarity behavior are excluded.

Case admission is based only on reproducibility, bounded-interface feasibility and evaluator quality. No case may be replaced because OARL performs poorly.

## Frozen numeric thresholds

These values are frozen before any v0.7 external OARL outcome is inspected.

- success/correctness noninferiority margin: **5 percentage points absolute** relative to the strongest generic baseline;
- false warranted decisions on deterministic exact cases: **0 tolerated**;
- material complementarity threshold: **0.10 normalized decision-value units** on a per-case [0,1] decision-value scale;
- useful complementarity prevalence required for the domain claim: **at least 20% of admitted cases**;
- confidence level for paired case-bootstrap gates: **95%**;
- primary total-cost measure: **end-to-end wall-clock seconds from policy start through final decision**, including relation/quotient discovery, planning and execution;
- primary execution-cost measure: **logical/physical A/B probe executions**;
- `C_plan` and `C_structure` evaluation counts are mandatory secondary decomposition metrics and may not be omitted from reporting.

The primary total-cost gate uses measured end-to-end wall-clock time rather than an arbitrary weighted sum of planning evaluations and probe executions. Paid external-call cost, where nonzero, is reported separately and may additionally support a practical-cost claim, but it does not replace the primary wall-clock gate.

## Policies

All policies receive the same candidate probes, observations, validity feedback, declared execution costs and accumulated history.

1. `random` — randomized ordering sanity floor.
2. `fixed` — deterministic fixed-order baseline.
3. `greedy_information` — one-step mechanism-information gain.
4. `greedy_decision` — one-step decision-risk / decision-entropy reduction.
5. `cost_aware_greedy` — one-step task utility per measured/declared execution cost.
6. `generic_two_step` — fair two-step decision lookahead over the raw candidate space.
7. `generic_set_cover` — generic maximum-coverage / set-cover style selection over observed distinguishing signatures where applicable.
8. `oarl_equivalence_only` — exact/certified quotient, no complementarity term.
9. `oarl_complementarity_only` — complementarity-aware planning, no quotient.
10. `oarl_full` — quotient followed by complementarity-aware planning.
11. `oarl_scrambled_relations` — preserves individual orientation statistics but deterministically scrambles relation assignments; causal ablation only, never used for tuning.

The exact policy source and parameters must be hash-frozen before the first confirmatory result is inspected.

## Decision completeness

For surviving candidate explanations `M_S`, a warranted action requires:

`|{d(m): m in M_S}| = 1`.

If the available admissible probe set is exhausted without decision completeness, the required output is `UNKNOWN`. A found behavioral difference alone is not automatically a regression unless the case evaluator/declared invariant supplies that direction.

Track R (regression search) and Track D (multi-hypothesis decision completeness) are reported separately. A historical A/B regression is sufficient to enter Track R after preflight, but Track D additionally requires an independently authored or mechanically generated nontrivial hypothesis family frozen before acquisition.

## Costs

Report separately:

- `C_probe`: logical and physical A/B executions;
- `C_plan`: candidate utility / pair / set evaluations;
- `C_structure`: cost of discovering or certifying quotient/relational structure;
- wall-clock runtime;
- external paid-call cost where nonzero.

No planning or preprocessing cost may be omitted merely because it occurs before acquisition.

## Primary safety gates

- zero false warranted decisions on deterministic exact cases;
- matched error/abstention calibration on noisy cases if any are admitted;
- OARL success/correctness may be at most **5 percentage points absolute below** the strongest generic baseline; otherwise the noninferiority gate fails;
- genuinely unresolved cases must return `UNKNOWN` rather than forced convergence.

## Primary utility gate

At matched decision correctness / abstention quality, v0.7 passes practical utility only if `oarl_full` improves the safety-adjusted cost frontier over the strongest generic baseline with a 95% paired case-bootstrap confidence interval excluding zero for at least one of:

1. physical/logical A/B execution cost; or
2. end-to-end wall-clock cost including structure discovery, planning and execution.

A planning/computational win is valid only if execution success/correctness passes the 5-point noninferiority gate and all structural-discovery work is included in the measured end-to-end time.

## Complementarity relevance gate

A nontrivial fraction of admitted real cases must exhibit useful complementarity: at least **20% of cases** must contain an acquired pair/set whose joint normalized decision value exceeds the sum of its one-step values by at least **0.10**. If fewer than 20% do, complementarity may be mathematically valid but is not established as practically frequent in this domain.

## Structural causality gate

The relational claim requires the deterministic `oarl_scrambled_relations` ablation to materially reduce the advantage of `oarl_full`. The paired case-level reduction in OARL advantage must have a positive 95% bootstrap lower bound. Otherwise the result may be attributable to a more complicated generic acquisition heuristic rather than orientation relations.

## Quotient safety

Any quotient used by `oarl_full` must be exact or explicitly certified under a frozen task-relative substitution rule. Held-out false merges that alter the warranted decision are a safety failure. Approximate non-transitive compatibility must not be silently treated as an equivalence relation.

## Kill conditions

The standalone OARL practical-advantage claim fails if any of the following occurs:

- any false warranted decision occurs on deterministic exact cases;
- OARL success/correctness is more than 5 percentage points absolute below the strongest generic baseline;
- all apparent cost savings disappear after counting structure discovery and planning overhead in end-to-end time;
- relation scrambling leaves the advantage essentially unchanged under the frozen bootstrap gate;
- useful complementarity occurs in fewer than 20% of admitted cases using the frozen 0.10 materiality threshold;
- case selection or replacement uses OARL outcomes.

## Interpretation ladder

### A — strong win

OARL passes safety/noninferiority and improves real execution cost and/or total end-to-end wall-clock cost over strong generic adaptive planning, with relational scrambling destroying a statistically supported material part of the advantage.

### B — computational win only

Generic lookahead chooses equally good experiments, but quotienting/relational structure materially reduces end-to-end planning/search cost after structure-discovery overhead is included. Interpret OARL as a structural acceleration layer for active experimental design.

### C — no incremental advantage

Generic adaptive methods match OARL in both executions and total computation. Preserve exact equivalence certification, safe quotienting, decision completeness, `UNKNOWN` and complementarity diagnostics, but do not maintain a broad standalone algorithmic-superiority claim.

## Claim boundary

Even a positive v0.7 establishes prospective external generalization only within the admitted software/AI-regression domain and bounded probe languages. Cross-domain / cross-ontology generalization requires a later frozen test in a materially different experimental domain.
