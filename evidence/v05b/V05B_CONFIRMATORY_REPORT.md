# OARL v0.5B.1 Confirmatory Report

## Result

**PASS on the preregistered synthetic finite-noise safety/coverage gate.**

v0.5B.1 tested whether a precision-first structural certifier can recover a useful subset of exact affine/permutation orientation equivalences from finite noisy predictive evidence without introducing false merges or incorrect transports.

The answer on the frozen benchmark is **yes, conditionally and narrowly**.

## Protocol

The protocol was frozen in `PREREGISTRATION.md` after an earlier pilot certifier had already failed by producing a false merge at 500 predictive samples per cell. That failed prototype remains documented in `PILOT_FAILURE_NOTE.md` and is not included as confirmatory evidence.

The replacement certifier used two independent predictive splits, each representing **2,000 IID Gaussian predictive samples per mechanism/orientation/intervention cell**. It could return only:

- `EQUIVALENT` — merge permitted;
- `DISTINCT` — retain separately;
- `UNKNOWN` — abstain and retain separately.

Only `EQUIVALENT` declarations were allowed to alter the quotient.

The certifier required replicated forward mappings, exact inverse recovery in the reverse direction, assignment separation, affine-parameter stability/reciprocity, simultaneous response-equivalence bounds, and predictive-noise compatibility. Mechanism-flat or ambiguous pairs were intentionally allowed to abstain.

## Preregistered held-out population

### Distinct controls

Four `standard` configurations were tested over seeds **1000–1299**. Every orientation pair was challenged directly.

Total truly distinct pair challenges: **72,600**.

False `EQUIVALENT` certificates: **0**.

### Equivalence controls

Four `equivalent_redundancy` configurations with four true equivalence classes were tested over seeds **2000–2099**.

Total worlds: **400**.

## Primary results

| Metric | Result | Gate |
|---|---:|---:|
| Distinct-pair challenges | 72,600 | — |
| False equivalence certificates on distinct pairs | **0** | 0 |
| Equivalence-world pair false positives | **0** | 0 |
| Pairwise precision | **1.000** | 1.000 |
| Pairwise true positives | 1,213 | — |
| Pairwise false negatives | 3,187 | — |
| Pairwise recall | **0.2757** | >= 0.20 |
| Accepted direct equivalence certificates | **829** | — |
| Accepted intervention-mapping errors | **0** | 0 |
| Maximum accepted scale relative error | **0.03924** | <= 0.06 |
| Maximum accepted offset error | **0.02122 sigma** | <= 0.05 sigma |
| Mean discovered compression fraction | **0.1787** | >= 0.10 |

Every preregistered primary criterion passed.

## What the result means

The important result is not high recall. It is the combination of **observed perfect precision and non-zero useful coverage** under a deliberately asymmetric loss function.

v0.4 showed that a false structural merge can damage downstream correctness, whereas a missed equivalence normally costs computation. v0.5B.1 therefore behaves conservatively: it recovers only about **27.6%** of the true pair equivalences and abstains on the rest, yet that partial recovery still reduces the mean number of orientation classes by about **17.9%**.

That is the intended design trade-off:

```text
ambiguous evidence -> UNKNOWN -> keep raw orientation
strong replicated evidence -> EQUIVALENT -> quotient permitted
```

## Transport correctness

Class labels alone are not sufficient. A correct equivalence declaration paired with the wrong intervention permutation or affine transport could still corrupt inference.

For every accepted direct certificate, the hidden benchmark truth was used **only after certification for evaluation**. Across the confirmatory set:

- intervention mapping errors: **0**;
- maximum scale relative error: **3.92%**;
- maximum offset error: **0.0212 sigma**.

Thus the gate did not merely recover compatible class membership; the accepted transports also satisfied the preregistered accuracy bounds.

## Secondary downstream result

A descriptive downstream comparison used the first 25 seeds of each positive configuration, for **100 worlds** total.

| Metric | Oracle quotient | Finite-noise discovered quotient |
|---|---:|---:|
| Correct argmax rate | 0.76 | **0.78** |
| False-high-confidence rate | 0.01 | **0.01** |

The 0.02 correctness difference is not a claim of superiority; this secondary sample was not powered or preregistered to establish that difference.

The discovered quotient used substantially **more score evaluations than the oracle quotient**: the stored metric `discovered_vs_oracle_score_eval_reduction` is **-1.2737**, meaning the conservative discovered structure required about **2.27x** the oracle quotient's score evaluations. This is expected because the oracle knows every true equivalence while v0.5B.1 deliberately abstains on most of them.

This comparison is against the **oracle quotient**, not exhaustive Generic OED, and therefore is not an end-to-end efficiency claim.

## What this does establish

Within the exact affine/permutation synthetic family used here:

> A conservative cross-fit certifier can infer a useful subset of orientation equivalences from finite noisy predictive evidence while abstaining on ambiguous pairs, with zero observed false merges across 72,600 held-out distinct-pair challenges and zero observed transport-map errors among accepted confirmatory certificates.

This closes an important gap between v0.3 and v0.4: the quotient no longer has to be supplied entirely as perfect hidden metadata in order to obtain some safe structural compression.

## What this does **not** establish

v0.5B.1 does not show that:

- semantic or physical admissibility can be inferred from data;
- approximate equivalence is safe in arbitrary systems;
- the certifier generalizes to learned neural representations;
- the same thresholds transfer to non-Gaussian or non-affine systems;
- finite-noise certification is end-to-end cheaper than exhaustive OED after certificate acquisition cost;
- OARL beats specialist symmetry-reduction, causal-abstraction, bisimulation, canonicalization or causal-discovery baselines;
- OARL is state of the art in causal discovery or active inference.

Those are separate gates.

## Research-integrity note

The failed 500-sample pilot remains part of the record. v0.5B.1 is a new post-pilot protocol with new held-out seed ranges. The confirmatory thresholds were frozen before the full held-out run and were not altered after its results were observed.

## Reproduce

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q tests/test_noisy_certification_v05b.py
python scripts/run_v05b.py
```

The authoritative machine-readable result is `outputs/v05b_summary.json`.
