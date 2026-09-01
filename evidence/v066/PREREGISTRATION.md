# v0.6.6 preregistration — external mutation-matrix suitability gate

**Status:** apparatus frozen before reading any confirmatory kill-cell values from the four selected matrices.

## Question

Does an independently authored software-testing family contain a large, exact, task-preserving quotient after deterministic metadata canonicalization, while leaving a nontrivial finite-evidence discovery problem for a later OARL-specific gate?

v0.6.6 is a **benchmark-suitability gate**, not an OARL algorithm test. It must not claim learned utility.

## External source

- repository: `donghwan-shin/Diversity-aware-Mutation-Testing`;
- pinned source commit: `f8d8376e0efe345161f26ff6483a404c8548fe1c`;
- upstream license: MIT;
- externally supplied object: Defects4J test-by-mutant binary kill matrices;
- development pilot inspected before this freeze: `Chart-1` only.

Each row is an actual developer, Randoop or EvoSuite-branch test. Each mutant column records whether that test killed the mutant. OARL does not generate tests, mutants, outcomes or equivalence labels.

## Confirmatory matrices

The following matrices were selected without reading their kill-cell values. Within each non-Chart project, eligible filenames were required to contain at least 500 raw tests, at least 200 mutant columns and no more than 15 MB. The selected fault is the lowest SHA-256 of `v066-confirm:<project>:<fault>`.

| Project | Fault | Raw tests | Mutants |
|---|---:|---:|---:|
| Closure | 118 | 8,295 | 623 |
| Lang | 33 | 1,401 | 630 |
| Math | 22 | 1,290 | 332 |
| Time | 6 | 3,469 | 797 |

Only file headers, line counts and byte sizes were inspected to apply this rule. Kill outcomes remain sealed until this preregistration and apparatus are committed.

## Candidate and evidence boundary

For each matrix:

1. exact duplicate `(testType, test)` identifiers retain their first occurrence;
2. mutant columns are assigned deterministically using SHA-256 of `v066-mutant-split:<project>:<fault>:<mutant-id>`;
3. digest byte 0 below 128 is development evidence; all other columns are held out;
4. a test is eligible only if it kills at least one development mutant.

The eligibility rule is frozen and cannot inspect held-out outcomes. A matrix with fewer than 200 eligible tests fails the screen.

## Exact evaluator relation

Two eligible tests are held-out task-equivalent exactly when their binary kill vectors over all held-out mutants are identical.

This relation is:

- exact and dataset-relative;
- reflexive, symmetric and transitive by equality;
- independent of numerical tolerances;
- not a claim that the test source code is semantically identical outside this mutant family.

The oracle partition is used only for evaluation. No held-out signature may enter a later learned method.

## Comparators

1. **RAW** — every eligible test is a singleton.
2. **DEVELOPMENT-SIGNATURE** — generic grouping by exact development kill vector. This is a diagnostic baseline, not safe by assumption.
3. **HELDOUT-ORACLE** — exact held-out kill-vector classes.

Report DEVELOPMENT-SIGNATURE compression, proposed pairs, false held-out merge pairs and pair precision. This establishes whether the future problem is trivial for a generic finite signature.

## Fixed downstream task

Every partition uses the identical deterministic greedy maximum-mutant-coverage algorithm with a budget of 20 tests. Class representatives are the lowest original eligible-test index. Ties are broken by representative index.

Report selected tests, covered held-out mutants, coverable held-out mutants and marginal-gain score evaluations. An exact oracle quotient must match RAW covered-mutant count and selected-test count.

## Frozen suitability gate

The family passes only if all are true:

1. all four matrices contain at least 200 eligible tests;
2. at least three of four matrices have at least 20% oracle compression;
3. median oracle compression is at least 20%;
4. every oracle quotient preserves RAW greedy coverage and selected-test count.

Passing establishes a suitable **external target**, not OARL utility. Failure is preserved and closes this target.

## Cost accounting

Report separately:

- development test-mutant outcome cells available to a learner;
- held-out evaluator cells;
- downstream marginal-gain score evaluations;
- analysis wall-clock time;
- compact artifact sizes.

The source matrices do not contain reliable per-test execution times. v0.6.6 therefore cannot claim dollar or wall-clock acquisition savings. A later algorithm gate must obtain or measure execution time before making an end-to-end economic claim.

## Integrity

No threshold, split, matrix, eligibility rule or downstream policy may change after confirmatory kill outcomes are inspected. A negative result is valid output and must not fail CI. Any changed experiment becomes v0.6.7 or later.
