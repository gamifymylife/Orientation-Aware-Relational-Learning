# v0.7 external case-selection protocol

## Contamination boundary

No v0.7 external OARL policy may be executed until the case set, A/B revisions, evaluator definitions, candidate-probe language, costs, policy source hashes and exclusion list are frozen.

Selection may use only public issue/PR metadata, reproducibility evidence, package-install feasibility and evaluator-only red/green preflight. Selection may not use OARL scores, discovered complementarity, quotientability, witness locations or post-hoc difficulty.

## Target

- target: 24 admitted historical regressions;
- minimum to launch: 20;
- prefer at least 4 independent frameworks/projects;
- prefer heterogeneous failure modes rather than repeated variants of one bug family.

## Admission

A candidate is admitted only if all of the following hold:

1. exact pre-fix and post-fix revisions can be pinned;
2. the same bounded public interface exists on both revisions;
3. evaluator-only preflight reproduces the historical contrast on at least 3/3 fresh A/B pairs;
4. matched same-revision negative controls do not produce the target contrast;
5. a bounded candidate orientation/probe language can be generated without embedding the known witness;
6. candidate execution is sufficiently deterministic or explicitly modeled as noisy;
7. costs can be measured or declared consistently across policies.

## Rejection vocabulary

Reject only for a frozen reason:

- `NOT_MERGED_OR_UNPINNABLE`
- `NO_COMMON_INTERFACE`
- `HISTORICAL_CONTRAST_NOT_REPRODUCED`
- `NEGATIVE_CONTROL_FAILED`
- `UNBOUNDED_OR_WITNESS_LEAKING_PROBE_LANGUAGE`
- `NONDETERMINISTIC_BEYOND_PROTOCOL`
- `DEPENDENCY_OR_ENVIRONMENT_UNREPRODUCIBLE`
- `DUPLICATE_CASE_FAMILY`
- `PREVIOUS_OARL_EXPOSURE`

No `OARL_FAILED`, `LOW_COMPLEMENTARITY`, or `LOW_QUOTIENT` rejection is permitted.

## Freeze artifact

When at least 20 cases are admitted, create `CONFIRMATION_LOCK.json` containing, per case: case id, project, pre/post SHAs, evaluator hash, adapter/probe-language hash, cost model, negative control and admission provenance.

The lock must also contain exact hashes of all policy implementations and parameters, random seeds, bootstrap procedure, noninferiority margin, complementarity materiality threshold, total-cost normalization and corpus exclusions.

After this lock exists, no case, policy, threshold or evaluator may be changed in place.

## External-corpus reuse

Cases may be sourced from the same historical-regression collection infrastructure used by Mechanism Diff, but only cases untouched by the v0.7 OARL complementarity programme are eligible. Reusing collection infrastructure is allowed; reusing inspected OARL outcomes is not.

## Launch rule

The external gate must refuse to run if fewer than 20 cases are locked, any policy/adapter/evaluator hash differs, any result exists for an unlocked case, or the relation-scramble procedure is not frozen.
