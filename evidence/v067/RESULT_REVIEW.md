# OARL v0.6.7 — External mutation baseline result

**Disposition: DEVELOPMENT BASELINES UNSAFE; OARL-SPECIFIC LEARNED ADVANTAGE NOT TESTED.**

Source: user-supplied `RESULT.json` received October 13, 2026; complete-file SHA-256:
`2268e82648b30589fa63cfdd41feb21680e053d9efc399b23aeaa0148f7c96ec`.

This report transcribes and checks numerical aggregates from that JSON; **it is not an independent re-execution**. Local test stdout, source-conversion logs, and a sealed evaluator receipt were not supplied with the file. Results are from public previously unused project-fault matrices, with *procedural* split only, and cannot be promoted to independent confirmation.

## Eligibility and outcomes

Official output: `protocol=v067-development-1`; `outcome=DEVELOPMENT_ONLY_NOT_CONFIRMATORY`; `eligible_count=4`.

| Frozen fault | Development-active tests | Exact-development compression | Exact false heldout pair merges | Distinct heldout mutant outcomes lost by reducing each class to a representative | Hamming false pair merges | Hamming lost mutant outcomes |
|---|---:|---:|---:|---:|---:|---:|
| Chart-1 | 395 | 70.13% | 1,086 | 2 | 1,312 | 2 |
| Lang-9 | 1,449 | 91.86% | 43,412 | 0 | 57,874 | 0 |
| Math-1 | 768 | 46.88% | 1,495 | 3 | 1,977 | 6 |
| Time-4 | 290 | 60.00% | 601 | 2 | 825 | 2 |
| **Aggregate** | **2,902** | — | **46,594** | **7** | **61,988** | **10** |

Exact-development grouping proposed 133,977 equivalent pairs, **34.78% false** on heldout mutant signatures (65.22% precision). Hamming-1 proposed 156,169 pairs, **39.69% false** (60.31% precision). These are pair counts, **not** unique defects.

## Planning score computations (not real execution time)

| Method | Aggregate planning-score calculations | Change against raw |
|---|---:|---:|
| RAW (no grouping) | 47,249 | — |
| Exact-development signature | 13,726 | **70.95% fewer** |
| Complete-link Hamming-1 | 11,754 | **75.12% fewer** |

All arms reuse 956,843 provided development outcome cells across four project-fault matrices; the experiment **does not measure source-test execution reduction or certification acquisition costs**. These planning numbers do not imply a 71% actual runtime speedup.

## Downstream selection: an interpretive trap

Greedy selections generated from development signatures, with a budget of 20, detected 994 heldout mutants across four matrices for both RAW and exact-development grouping, with the same heldout selection vectors. This agreement is largely expected from identical development signatures and deterministic representatives; **it is not an independent proof of generalization**.

The Hamming-1 baseline detected 992 heldout mutants; Time-4 missed two that RAW selected. Separately, discarding nonrepresentative members of every proposed class removed 7 heldout mutant outcomes for exact grouping and 10 for Hamming-1 relative to the full eligible suite, even when the budgeted greedy result was unchanged.

A technically important distinction: **pairwise behavioral identity is stronger than preserving a downstream decision or total detectable-mutant coverage.** Lang-9 has 43,412 false pair equivalences but zero mutant outcomes lost by representative-only full-suite reduction *on this heldout matrix*. This suggests testing decision-specific redundancy separately from exact pairwise equivalence, not declaring grouping safe for future unknown mutants.

## Gate outcome

- Four frozen cases admitted (development admission PASS).
- Both naive aggressive baselines violate zero-false-merge safety (FAIL).
- No OARL-specific method evaluated; **no RCC/OARL superiority demonstrated**.
- No external hidden evaluation, chronological drift test, paid runtime data, or measured end-to-end resource advantage.
- These four faults and their exposed heldout results are now **consumed for further confirmatory use**.

## Narrow next question

Before acquiring another confirmatory cohort, develop a **single decision-preserving, abstaining test-retention policy** on development-only data. Compare its incremental test/mutant inspection costs and previously unseen mutation coverage with established greedy set cover, test subsumption/dominance, and sequential/risk-limited verification. Freeze the policy and error criterion **before** any new independently administered, unseen faults are scored. Finite signatures alone cannot certify universal equivalence against arbitrary future faults.

Keep the current negative result immutable and `main` unchanged.
