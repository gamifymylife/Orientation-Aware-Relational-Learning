# Amendment 001 — candidate-explanation and decision contract

## Why this amendment is required

The v0.7 preregistration correctly defines decision completeness over a surviving candidate-explanation set `M_S`, but a historical buggy/fixed A/B package pair does **not** by itself define a nontrivial multi-hypothesis family `M`.

This matters because the synthetic complementarity result in PR #12/v0.7 relies on multiple candidate mechanisms with a task decision map. If a real-case curator were allowed to invent candidate explanations after reading the bug, complementarity and `UNKNOWN` could be manufactured by representation choice rather than discovered externally.

This amendment is frozen during corpus construction and before any v0.7 external OARL policy execution.

## Two evidence tracks

A case may support one or both of the following tracks, but their claims must not be conflated.

### Track R — regression-search utility

Required objects:

- exact buggy/fixed executable revisions;
- one frozen common experiment language;
- mechanically generated observation orientations;
- a historical evaluator that decides whether an executed probe exposes the frozen A/B distinction.

Track R asks:

> Does relational/quotient structure reduce the execution or planning cost required to find a stable historical behavioral witness relative to strong generic adaptive search?

A Track-R case does **not** establish decision-complete multi-hypothesis diagnosis merely because it contains an A/B pair.

### Track D — decision-complete multi-hypothesis utility

In addition to Track-R quality, Track D requires a candidate explanation family `M` and decision map `d: M -> D` that are fixed independently of OARL outcomes.

Track D asks:

> Does relational orientation structure reduce the cost of acquiring enough evidence that every surviving explanation implies the same task decision, while returning `UNKNOWN` when the supplied evidence family is insufficient?

Only Track-D cases count toward claims about external decision completeness, complementarity among evidence views in the PR-#12 sense, or calibrated `UNKNOWN` over `M_S`.

## Admissible sources of `M`

A real case may enter Track D only when `M` comes from one of these frozen, auditable sources:

1. **Externally authored alternatives** — the upstream benchmark, issue, protocol or test family already supplies multiple competing mechanisms/faults/configurations before v0.7 analysis.
2. **Mechanical perturbation family** — a case-independent generator produces candidate mechanisms by the same declared transformation grammar for every eligible case, before any OARL outcome is inspected.
3. **Frozen simulator/model family** — an executable external model exposes a declared parameter/mechanism family, with the candidate grid frozen before acquisition.
4. **Prospectively generated fault family** — independently generated mutations/faults are frozen before evaluator outcomes, then treated as candidate mechanisms under a common task definition.

The following are forbidden:

- natural-language explanations invented after reading the historical fix;
- hypotheses chosen because they make XOR/complementarity appear;
- candidate models inferred from the held-out OARL trajectory;
- adding explanations after `UNKNOWN` or a policy failure;
- using the known witness location as a candidate-hypothesis label.

## Decision map

The decision map `d` must also be external or mechanically derived. Examples include:

- fault detected / not detected;
- safe / unsafe substitution;
- invariant preserved / violated;
- remediation class supplied by an external benchmark;
- action choice derived by a frozen deterministic rule from model outputs.

A curator-written semantic label is not sufficient unless it is frozen from independently authored external ground truth before OARL is run.

## Aggregation rule

The v0.7 external report must publish Track R and Track D separately.

- Track R may establish prospective real-world regression-search utility/generalization.
- Track D may establish prospective external decision-complete/complementarity utility.
- A Track-R success must not be described as external validation of PR #12's multi-hypothesis decision-completeness mechanism.

If fewer than the preregistered minimum Track-D cases can be constructed without violating this contract, preserve that as a benchmark-suitability result rather than inventing hypotheses to reach the sample target.

## Relation to the original gate

The main practical-advantage question remains valid for Track R. The stronger complementarity-relevance and calibrated-`UNKNOWN` claims require Track D. The final report must state exactly which claim each case supports.
