# OARL v0.6.8 — Corrected feasibility-first external development result

**Official decision: CORRECTED EXPERIMENT VALID AS DEVELOPMENT COMPARISON; NO RELATION-PROXY ADVANTAGE; STOP THIS PROXY.**

**Evidence:** Owner-supplied `FEASIBILITY_RESULT.json` on October 13, 2026. SHA-256 `01b21cfbe8c13c6bde21859ac9df415da859be0864627d8eaa758ed2fcb49ade` (57,059 bytes). The upload was parsed independently for aggregate arithmetic, selected-index validity and reported solver statuses. **The full result JSON and original NPZ source matrices are not being committed by this review**, and this is not independent re-execution of the source code. The canonical source matrices are locally owned and pinned by the original v0.6.7 manifests.

## Protocol and data integrity

- Protocol: `v068-feasibility-correction-development-v1`, fully evaluated in the provided file.
- Four previously inspected real-source development cases: Chart-1, Lang-9, Math-1, Time-4.
- Original eligible tests: Chart **395**, Lang **1,449**, Math **768**, Time **290**; aggregate **2,902**.
- Aggregated outer mutants *detectable by the eligible complete suites*: **1,107** (Chart 177, Lang 178, Math 466, Time 286). These are **mutant columns** across different project faults, not independently replicated natural bug discoveries.
- All **40** case × redundancy × method records set `development_coverage_verified=true`. No arbitrary 20/50 limit, all-tests fallback or failed feasibility gate.
- All eight MILP target instances claim `solver_optimality_proven=true`, MIP gap **0**, with integer lower bound matching incumbent. Thus the source reports certified *minimum selected-test count on the development columns*. Optimizing development cardinality says nothing about preserving every unseen mutant.
- Parsed assertions: each reported selected-index list has the stated length, no duplicate or out-of-range index, and `outer_detected_mutants + outer_missed_mutants == outer_detectable_mutants` in all 40 records.
- The earlier v0.6.7 heldout columns were already consumed: **not a fresh or independently administered confirmation**, despite retrospective outer scoring.
- The experiment reuses full, precomputed development kill matrices. A reduction in retained tests **does not measure end-to-end test execution savings**, and the full evidence-acquisition cost is not avoided.

## Aggregate results

Each table cell is **retained test count / missed outer detectable mutants**, summed across the four independent project-fault datasets (denominator 2,902 eligible tests, 1,107 detectable outer mutant columns).

| Method | C1: ≥1 development witness | C2: 2 witnesses where available |
|---|---:|---:|
| Standard greedy set cover | 105 / 56 | 185 / 35 |
| Rarest-first weighted greedy | **102 / 54** | **183 / 31** |
| Standard partition refinement | 105 / 59 | 189 / 35 |
| RCC-inspired relation proxy | **104 / 59** | **185 / 33** |
| MILP minimum-cardinality reference | **100 / 60** | **182 / 31** |

For the relation proxy:
- C1 retains 104 of 2,902 (96.42% fewer tests), losing 59/1,107 (5.33%) detectable outer mutant outcomes.
- C2 retains 185 (93.63% fewer tests), losing 33/1,107 (2.98%) detectable outer mutant outcomes.
- Rarity greedy **strictly beats its aggregate retained count and outer misses** at both targets (102/54 and 183/31 respectively). This is a descriptive aggregate, not a claim of casewise dominance in every case.
- MILP minimizes development test count (100,182); its outer misses are 60,31. Its C1 minimum test set does **not** minimize unseen mutant misses. C2 MILP beats relation proxy on both aggregate objectives (182/31 vs 185/33).

## Per-case relation-proxy vs strongest controls

| Case | Eligible tests | C1 relation | C1 illustrative superior/comparator | C2 relation | C2 illustrative superior/comparator |
|---|---:|---:|---|---:|---|
| Chart-1 | 395 | 29 / 12 | Rarity greedy 29 / 9 | 50 / 6 | Greedy, rarity, MILP 50 / 6 |
| Lang-9 | 1,449 | 11 / 6 | MILP 11 / 3 | 18 / 3 | Rarity, partition and MILP 18 / 3 |
| Math-1 | 768 | 43 / 33 | Rarity greedy 42 / 25 | 75 / 21 | MILP 73 / 19 |
| Time-4 | 290 | **21 / 8** | Non-dominated in *retained count vs missed outer outcomes* among these five methods | 42 / 3 | Greedy, rarity and MILP 41 / 3 |

The Time-4 C1 case alone offers a local tradeoff that is not dominated by another tested approach. It does not overcome aggregate and other-case losses, extra complexity, or the already-burned evaluation data.

**Signature overlap:** In C1, relation proxy and standard partition refinement selected exactly the same *set* on Chart-1, Lang-9 and Math-1. This does not establish that the proxy provides unique relation-aware information. C2 choices also overlap heavily.

## Computation and decision

The relation proxy computes pairwise partition-split gains at each step; rarity greedy does not. Across four cases, cumulative reported relation-proxy algorithm time is about **0.142 s C1** and **0.319 s C2**, against rarity greedy about **0.037 s** and **0.067 s**. These are one-run, small-scale source timings, **not** validated end-to-end benchmarks or universal performance ratios.

The previously frozen correction protocol requires multi-dataset superiority on safety–retention–cost tradeoff to establish RCC-specific utility. This criterion is **NOT MET**. This is a useful properly feasible baseline study, but **not proof that exact equivalence can be inferred from finite evidence or a competitive novel OARL certifier**.

**Decision:** Preserve both v0.6.8 outcomes (the invalid-budget all-abstention study and this informative correction) separately. **Do not adjust relation weights on these inspected cases and relabel them prospective**. Stop this proxy. A future relation-first idea should supply a *distinct, falsifiable mechanism*, with a genuine information/evidence-cost advantage over exact ILP and cost-aware set-cover baselines, and new independently administered heldout faults **before** expensive experiments.
