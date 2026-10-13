# OARL v0.6.7 — Prospective redundancy screening, phase 0

**Status:** APPARATUS READY; NO NEW EXTERNAL MATRIX ADMITTED; NO CONFIRMATORY RUN; NO OARL LEARNER CLAIM.

## Decision

Investigate whether nontrivial *learned* equivalence of software tests can reduce redundant work **without changing which unseen mutants are detected**. The previous v0.6.6 result found large evaluator-known redundancy, but false merges made exact development signatures unsafe; its four matrices are consumed and barred from positive prospective evidence.

This is a **development-only admission and falsification harness**. A public heldout mutant partition is not a secret, independently administered evaluation. The independent confirmatory experiment must be separately authorized, with source and scoring held outside the development workflow.

## Fixed data contract

- Source: independently authored binary mutant/test kill matrices (Defects4J-family matrices are one possible source), exact source URL and immutable commit recorded per matrix.
- New faults only; `Closure-118`, `Lang-33`, `Math-22`, `Time-6` are permanently barred as fresh cases. No synthetic data count as external evidence.
- Admit at least **three** new fault matrices with at least **200** development-active, identifier-canonical tests apiece; no retrospective threshold relaxation.
- Record SHA-256 of each `.npz` projection and identify the exact source. `upstream_commit` is provenance metadata, not proof of source equivalence: conversion must be independently checked before a scientific claim.
- Split mutants using `SHA256('v067-develop:{project.casefold()}:{fault}:{mutant_id}')`, first byte `<128` for development. Holdout used only for scoring after proposals are fixed. Developer may inspect development data. This partition is *procedurally* held out, not institutionally sealed.
- Re-run only on newly admitted faults. Once inspected, an entire project-fault and its heldout observations are **burned** for any confirmatory claim.

## Measured question and cost ledger

Tests are candidates; mutants are intervention outcomes. Two tests are *dataset-relative* equivalent only if every heldout mutant kill result matches. This does **not** mean they are identical programs or universally equivalent on unknown future mutants.

1. **Primary safety:** unordered heldout false-equivalence pairs. Zero required for a safe-equivalence claim; report number of proposed pairs, precision and abstention/compression.
2. **Primary consequence:** heldout mutants detectable by the full eligible suite but lost when discarding all but one representative per proposed equivalence class. The fixed-budget (20-test) greedy policy is selected **using development evidence only**, and its full heldout detection vector is reported as a secondary diagnostic. **Critical caveat:** exact development-signature grouping and raw greedy naturally select the same earliest representatives, so agreement of this secondary diagnostic cannot validate safety.
3. **Resource accounting:** (a) development evidence cells already supplied; (b) planning-score evaluations; (c) any **measured** real execution times (none in this phase). Do not turn (b) into a speedup for (c).
4. **Cost of discovery:** acquisition cells/queries, proposals, certification checks and any refutation probes, once a *new* method exists. A proposed future cost model is not a measured result.
5. **Robustness to change:** cross-version drift requires chronological revisions, not just a random mutant partition. Do not label same-version holdout disagreement as temporal drift.

## Frozen development controls

- `raw`: one class per eligible test; the decision-reference arm.
- `exact_development`: group identical development mutant signatures; **known unsafe** baseline.
- `near_hamming_1`: complete-link grouping of rows at Hamming distance <=1; **deliberately unsafe negative** control.
- Metadata canonicalization occurs before arms as an exact-identifier deduplication contract. Validate identifiers against source semantics; do not call this behavioral certification.
- Evaluator-only exact heldout grouping may be used to calculate an *unattainable upper bound* in a later version, but cannot drive development proposals, greedy selection, or eligibility.
- A genuinely OARL-specific certifier has **not been specified** for the binary outcome semantics. Do not silently relabel exact signatures or nearest signatures as OARL.

## Stop / go decisions

- **STOP / unsuitable** if fewer than 3 new, eligible matrices meet the source and development-only admission rule.
- **STOP / noncompetitive** if the eventual learned method has any heldout false merge, worsens the heldout detection vector, or lacks total accounted savings versus a comparably informed generic control.
- **STOP / no novelty** if generic exact signatures, sequential verification or set-cover methods match its safety–utility–cost frontier.
- **PROCEED** to a *separate* independent confirmation only if a pre-frozen new method strictly beats the strongest applicable generic comparison on uninspected development-transfer faults with explicit acquisition costs.
- A failure stays a failure. Do not relabel an exploratory positive as a confirmatory result.

## Current executable scope

`run_v067_development.py` checks SHA-256, rejects burned/duplicate fault IDs, prevents path traversal, insists on new-fault eligibility and evaluates only generic baseline controls. The apparatus does **not** download datasets, execute mutants, request model calls, install dependencies, or run an OARL-specific certifier.

Example (not executable until a valid manifest and the actual, uninspected external matrix files exist):

```bash
python scripts/run_v067_development.py \
  --manifest evidence/v067/ADMITTED_INPUTS.json \
  --data-root external/mutation/v067/data \
  --out evidence/v067/DEVELOPMENT_RUN_001.json
pytest -q tests/test_v067_development.py
```

Output files are created once, not overwritten. Do not commit raw matrices or results as "private heldout". A fresh external evaluator would be required for a defensible confirmatory result.

## Related research and closest competing methods

- OARL v0.6.6: `evidence/v066/V066_RESULT.md` (four consumed cases; high oracle compression, 51,316 false development merges).
- Defects4J: <https://github.com/rjust/defects4j>.
- External kill-matrix source used by v0.6.6: <https://github.com/donghwan-shin/Diversity-aware-Mutation-Testing> (2018 work; additional fault matrices must be *explicitly* selected and verified).
- Generic comparison classes to implement before scientific competition: sequential verification/risk bounds, greedy set-cover/minimization, change-coverage selection and cost-aware test prioritization. Meta's predictive test selection: <https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/>.
- Research integrity: operator selection and mutant family strongly affect apparent utility. No absolute proof of future behavioral equivalence follows from finite observational matching without additional model assumptions.
