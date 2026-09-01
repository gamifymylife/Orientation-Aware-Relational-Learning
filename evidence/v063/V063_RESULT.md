# v0.6.3 result — finite-evidence safe quotient before fixed D-optimal design

## Verdict

**Primary structural safety gate: FAILED.**

**OARL-specific incremental utility: NOT ESTABLISHED.**

The failure is scientifically informative. The benchmark contains substantial real task redundancy and the oracle quotient removes it without changing downstream D-optimal design. The current finite-response OARL certificate, however, does not safely infer that task-relative equivalence: it frequently merges experiments whose finite response signatures are close while their local Fisher-information matrices are not equal under the frozen task criterion.

No threshold was retuned after this result.

## Frozen setup

- external executable system: `pygsti==0.10.2`, `smq1Q_XYI`;
- 254 physical X/Y circuits at depths 1–7;
- 2 hidden binary outcome conventions per physical circuit;
- 508 candidate views total;
- 19 mechanism probe models;
- 2 independent Bernoulli splits × 50,000 shots per view/probe;
- 4-nearest complement-invariant shortlist;
- task-equivalence oracle: exact local Fisher matrices equal within relative Frobenius tolerance `1e-8`;
- downstream algorithm for every method: the same 8-step greedy D-optimal selector with replacement.

The 50,000-shot value was fixed before confirmatory execution from the analytic simultaneous-bound width. The earlier written 4,000-shot value was corrected before any benchmark output because it could not certify exact `p≈0.5` equivalence inside the preregistered 0.020 probability envelope after familywise correction.

## Headline result

| method | classes | compression | accepted false task merges | pair precision | global pair recall | D-opt logdet | D-opt score evals | selected depth cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RAW | 508 | 0.0% | — | — | — | **11.3141815** | 4,064 | 56 |
| ORACLE | 170 | **66.5%** | 0 by construction | — | — | **11.3141815** | 1,360 | 56 |
| POINT | 216 | 57.5% | **1,143** | 0.2068 | 0.1573 | 11.1466039 | 1,728 | 53 |
| UCB | 225 | 55.7% | **1,032** | 0.2241 | 0.1573 | 11.1466039 | 1,800 | 53 |
| OARL-XFIT | 292 | 42.5% | **555** | **0.2620** | 0.1040 | **11.3141815** | 2,336 | 56 |

The oracle result is important: the candidate space really does contain a large amount of removable task redundancy. `508 → 170` classes cuts downstream score evaluations by 66.5% while producing exactly the same selected D-optimal sequence, final information matrix, log-determinant and depth cost as RAW.

OARL-XFIT also preserved the RAW downstream result exactly while reducing the candidate search to 292 classes. But it did so with 555 accepted pairwise false task merges, violating the preregistered zero-false-merge requirement.

## Primary gate

| check | result |
|---|---|
| zero accepted task-false merges | **FAIL — 555 false merges** |
| downstream D-opt logdet preserved | PASS |
| selected depth cost ≤ RAW | PASS |
| compression ≥ 20% | PASS — 42.5% |

Therefore the primary gate fails.

## What OARL did improve

OARL-XFIT was materially more conservative than the generic finite-response baselines:

- POINT: 1,143 false task merges;
- UCB: 1,032 false task merges;
- OARL-XFIT: 555 false task merges.

OARL-XFIT also abstained on 47.8% of shortlisted pairs and preserved the RAW D-optimal result, whereas POINT and UCB changed the downstream D-optimal result from logdet 11.3141815 to 11.1466039.

So cross-fit + abstention improved the safety/utility frontier descriptively. It was still nowhere near safe enough for the frozen exact task-equivalence criterion.

## Why the gate failed

The key mismatch is now explicit:

```text
finite response similarity
        ↓
can support
"these probe probabilities look interchangeable"

but does NOT imply
        ↓
local Fisher-information equality
        ↓
"these experiments are interchangeable for D-optimal design"
```

The mechanism-probe response tolerance was 0.020 probability units. The task oracle was much stricter and structurally different: equality of local derivative/Fisher geometry at relative tolerance `1e-8`.

Near-equal finite response values can therefore hide different local derivatives. More samples reduce uncertainty about the response values; they do not turn response-level equivalence into derivative-level/task-level equivalence.

This is a new version of the same boundary warning exposed by v0.6.1: **certifying the wrong representation of the task more precisely does not make the structural conclusion valid.**

## Shortlist limitation

The shared four-neighbour shortlist contained 298 of 1,894 oracle-equivalent pairs, a global pair recall of only 15.7%. This limits attainable compression for every learned method. It is not the cause of OARL's safety failure: false task merges occur among pairs that were shortlisted and explicitly accepted.

A future method may improve blocking/shortlisting, but doing so does not repair the current false-merge problem.

## Economics

OARL-XFIT reduced downstream D-opt score evaluations:

`4,064 → 2,336` (42.5%).

Its conservative structural-work proxy was 2,611,056 probability-cell operations, implying a break-even downstream-score cost of about **1,511 probability-cell operations per D-opt score evaluation**.

This means the quotient could plausibly amortize when downstream scoring is expensive (simulation, quadrature, learned rollouts, etc.). It does **not** establish economic utility because the safety gate failed.

## Competitive interpretation

No generic baseline strictly dominated OARL-XFIT on the frozen multi-axis definition: OARL had fewer false merges and preserved downstream D-optimality while POINT/UCB did not. However, OARL also did not establish incremental utility because its own primary safety gate failed.

The correct statement is therefore:

> Cross-fit abstention improves finite-response compression safety relative to simpler point/UCB baselines in this benchmark, but response-level equivalence is not a sufficiently strong certificate of task-relative D-optimal equivalence.

## Consequence for OARL

Do **not** respond by lowering the task oracle tolerance or tuning the response threshold on this confirmatory set.

The next method must certify the object that the quotient is required to preserve. For this task, that means a decision-/information-relative certificate, such as a bound on Fisher-information distortion or downstream decision risk, rather than generic response closeness alone.

This sharply narrows the next question:

> Can finite evidence certify that replacing experiment `e_i` with `e_j` changes the downstream decision/information criterion by at most a preregistered amount, with abstention when that guarantee cannot be established?

That direction is closer to approximate sufficiency / Blackwell–Le Cam deficiency and task-aware abstraction than to generic similarity clustering.

## Integrity

The confirmatory CI completed successfully as an execution/integrity run. The scientific result is negative by design and is preserved as such.

GitHub Actions artifact: `v063-safe-quotient-evidence` from the first v0.6.3 workflow run. The full artifact contains `summary.json`, `summary_compact.json` and `pair_predictions.csv`.
