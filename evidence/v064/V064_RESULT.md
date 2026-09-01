# v0.6.4 result — task-aligned finite-evidence equivalence

## Outcome

**PRIMARY SAFETY GATE FAILED — for insufficient compression, not false merges.**

The task-aligned reformulation repaired the specific v0.6.3 safety failure: OARL-TASK-XFIT accepted **zero operational false merges** and exactly preserved the RAW downstream D-optimal result. However, its bootstrap envelope was too conservative to certify a single equivalence, so compression was **0%**, below the preregistered 20% minimum.

No threshold was retuned after this result.

## Frozen confirmatory setting

- pyGSTi 0.10.2 / `smq1Q_XYI`
- 254 physical circuits, 508 candidate views
- 19 mechanism probes
- two fresh 100,000-shot splits
- 2,543 shortlisted pairs
- 3,842 evaluator-side task-equivalent pairs globally
- shortlist contained 1,263 task-equivalent pairs (32.87% global recall)
- finite evidence burden per learned method: **1,930,400,000 Bernoulli shots**

## Main result

| Method | Classes | Compression | False task merges | Pair precision | D-opt logdet | Score evals |
|---|---:|---:|---:|---:|---:|---:|
| RAW | 508 | 0.0% | — | — | 11.3141815 | 4,064 |
| ORACLE | 91 | **82.1%** | 0 | — | **11.3141815** | **728** |
| TV-UCB | 130 | 74.4% | **1,196** | 0.5136 | 11.0490150 | 1,040 |
| FIM-POINT | 491 | 3.35% | **0** | **1.000** | **11.3141815** | 3,928 |
| FIM-UCB | 508 | 0.0% | **0** | — | **11.3141815** | 4,064 |
| OARL-TASK-XFIT | 508 | **0.0%** | **0** | — | **11.3141815** | 4,064 |

The evaluator-only operational quotient is therefore very large: `508 -> 91`, an 82.1% reduction in candidate classes, while preserving exactly the RAW D-optimal outcome and selected depth cost.

## Primary checks

- oracle operational quotient preserves RAW: **PASS**
- zero OARL accepted task-false merges: **PASS**
- OARL downstream logdet preserved: **PASS**
- OARL selected depth cost no greater than RAW: **PASS**
- OARL compression >=20%: **FAIL (0%)**

Overall: **FAIL**.

## Diagnostic

The failure is not lack of genuine structure. The oracle finds 91 task classes, and 1,263 true task-equivalent pairs were present even inside the learned shortlist.

The problem is finite-evidence certification power.

Among the 1,263 shortlisted true-equivalent pairs, exact evaluator-side distortions were essentially zero for almost all pairs, yet noisy finite Fisher estimates were much less stable:

- median pooled point Fisher distance: ~0.225;
- median pooled bootstrap Fisher UCB: ~0.593;
- minimum pooled D-opt decision UCB among true pairs: ~0.292, already far above the frozen 0.05 equivalence tolerance;
- no true pair passed the pooled decision UCB;
- consequently neither FIM-UCB nor OARL-TASK-XFIT accepted any equivalence.

Even exact ordinary/complement views suffered large finite derivative/Fisher uncertainty because the certificate estimates local slopes from independent Bernoulli experiments. Task alignment solved the *wrong-object* problem from v0.6.3, but the chosen finite estimator cannot certify the right object economically at this evidence level.

## Important contrast

The forced point task-space comparator, FIM-POINT, accepted 21 true pairs with **zero false merges**, giving 3.35% compression and preserving D-optimality. This shows that the point estimates do contain useful task structure. The conservative uncertainty envelope, rather than the task representation itself, is what eliminated coverage.

However, FIM-POINT required roughly **14.2 million evidence-shot units per downstream score evaluation saved** under this accounting, so even its small safe compression is nowhere near an established economic win.

## Scientific interpretation

v0.6.3 and v0.6.4 together identify two separate failure modes:

1. **response equivalence is too weak** — it compresses aggressively but false-merges task-distinct experiments;
2. **direct finite Fisher certification is too data-hungry** — it can be safe but collapses into abstention/no compression.

This narrows the next problem substantially. The next method should not merely collect more IID evidence for every candidate pair. It should exploit known or learnable structural transports first, then spend task-aligned evidence only where structural ambiguity remains.

A promising next architecture is therefore:

```text
cheap structural / transport proposal
        ↓
exact or near-exact invariants
        ↓
small candidate equivalence set
        ↓
adaptive task-aligned evidence allocation
        ↓
EQUIVALENT | DISTINCT | UNKNOWN
        ↓
safe quotient
        ↓
unchanged D-optimal optimizer
```

This should be tested against a generic transform/canonicalization baseline and a sequential confidence-bound baseline. If those dominate, OARL should be narrowed accordingly.

## Claim boundary

This result does **not** establish an OARL-specific algorithmic advantage. It does establish that:

- a large task-preserving quotient exists in this external executable family;
- response-space certification is unsafe for discovering it;
- task-space point estimates can identify a very small safe subset;
- the frozen conservative finite-Fisher certificate is presently too weak/data-hungry to recover useful compression.

The negative result is preserved without post-hoc threshold changes.
