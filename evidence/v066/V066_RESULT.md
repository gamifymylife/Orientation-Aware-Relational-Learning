# v0.6.6 result — external mutation-matrix suitability gate

## Outcome

**THE FROZEN SUITABILITY GATE FAILED. THREE OF FOUR MATRICES EXPOSED A STRONG EXACT TARGET.**

The first genuinely black-box external screen moved OARL from model-supplied quantum structure to independently authored Defects4J mutant-test kill matrices. Tests are candidate experiments; mutant kills are binary outcomes; two tests are evaluator-equivalent exactly when their held-out kill vectors are identical.

The aggregate gate failed because `Closure-118` retained only **67** tests after the frozen development-activity eligibility rule, below the required 200. That failure is preserved. The project was not dropped post hoc and the threshold was not relaxed.

The other three matrices passed the substantive screen:

| Matrix | Eligible tests | Exact oracle classes | Oracle compression | Development-signature false merge pairs | RAW score evaluations | Oracle score evaluations |
|---|---:|---:|---:|---:|---:|---:|
| Closure-118 | 67 | 56 | 16.42% | 1 | 1,102 | 893 |
| Lang-33 | 258 | 147 | **43.02%** | 51 | 4,970 | 2,750 |
| Math-22 | 225 | 114 | **49.33%** | 182 | 2,847 | 1,404 |
| Time-6 | 1,225 | 165 | **86.53%** | 51,082 | 24,310 | 3,110 |

Median oracle compression was **46.18%**. Exact oracle quotienting preserved the fixed 20-test greedy maximum-coverage result on every matrix and reduced aggregate downstream marginal-gain scoring from **33,229 to 8,157 evaluations**.

## Frozen gates

| Gate | Result |
|---|---|
| Four external matrices evaluated | PASS |
| Every matrix has at least 200 eligible tests | **FAIL** |
| At least three matrices have at least 20% oracle compression | PASS |
| Median oracle compression at least 20% | PASS |
| Every exact oracle quotient preserves the fixed downstream task | PASS |

Because all gates were conjunctive, the official outcome is **FAIL**.

## Why this is nevertheless important

Unlike pyGSTi v0.6.5, the residual equivalence target is not directly encoded in test identifiers and cannot be analytically recovered from an exposed simulator. The only available evidence is externally generated test behavior against mutants.

Unlike a numerically thresholded Fisher relation, exact held-out kill-vector equality is reflexive, symmetric and transitive. It is well-conditioned at the all-zero vector and does not require a tolerance or insertion-order heuristic.

Most importantly, generic exact development-signature grouping was unsafe on every matrix. Across the four matrices it proposed 162,107 equivalent pairs and made **51,316 held-out false merges**. The three substantively suitable matrices therefore contain both:

1. large exact downstream redundancy; and
2. a genuine finite-evidence generalization problem.

That is the target pyGSTi lacked.

## What this does not establish

v0.6.6 does **not** establish:

- an OARL-specific learned advantage;
- zero-false-merge certification on mutation data;
- rich orientation-transport recovery—the kill/survive outcome semantics are fixed, so this primarily tests the certified-quotient core;
- semantic equivalence of test source code;
- population generalization beyond the frozen mutant family;
- end-to-end runtime or dollar savings.

The source matrices contain binary kill outcomes but not reliable per-test execution times. The 602,352 development evidence cells and 652,954 held-out evaluator cells therefore support logical and computational accounting, not an acquisition-cost claim.

## Correct next experiment

Do not fit a learner on these confirmatory held-out columns and report it as prospective. They have now been inspected.

v0.6.7 must select **new fault matrices** using a development-only activity screen, freeze the faults and mutant splits, and then compare:

- deterministic metadata canonicalization;
- exact development signatures;
- generic nearest-signature proposal;
- generic sequential confidence testing;
- an OARL orientation-aware proposal/certifier;
- RAW and evaluator-only oracle bounds.

The learned method must achieve zero held-out false merges and strictly improve the compression/evidence-cost frontier over every generic baseline. Otherwise the algorithmic claim should be narrowed.

## Reproduction

```bash
python -m pip install -e '.[dev]'
pytest -q tests/test_mutation_equivalence.py
python scripts/run_v066_mutation_suitability.py
```

Machine-readable output: `evidence/v066/summary_compact.json`.
