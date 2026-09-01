# Research Roadmap

## Completed foundation: v0.5 certified structure discovery

### v0.5A — exact structural discovery

In the exact synthetic candidate-model setting, OARL can infer exact quotient structure from likelihood geometry without hidden class labels. The frozen gate showed zero observed false merges and a real break-even regime when experiment scoring is expensive. Cheap proxy scoring does not amortize discovery overhead.

### v0.5B.1 — finite-noise equivalence certification

The initial 500-sample pilot false-merged a distinct pair and is preserved as a failure. The replacement post-pilot protocol was frozen before held-out evaluation.

Preregistered result:

- 72,600 truly distinct pair challenges;
- 0 false equivalence certificates;
- pair precision 1.000;
- pair recall 0.2757;
- 17.9% mean discovered compression;
- 829 accepted direct certificates;
- 0 accepted intervention-mapping errors.

Interpretation: precision-first finite-noise equivalence certification is viable in the current affine/permutation synthetic family when the evidence family contains the relevant distinction.

## External escalation: v0.6

External validity is now higher priority than further optimization of the synthetic construction.

### Completed: v0.6 CSuite suitability pilot

The adapter ran, but the tested published CSuite systems expose too few candidate intervention views for a serious pairwise equivalence-discovery benchmark. The suitability failure is preserved rather than manufacturing OARL-specific views.

### Completed: v0.6.1 pyGSTi external gate

Gate-set tomography supplies an independently established equivalence structure: gauge transformations can substantially alter internal representation while preserving observable circuit probabilities.

The deterministic smoke gate passed and established that the external domain contains the target phenomenon.

The subsequent preregistered finite-shot competitive gate then asked whether shallow evidence at circuit depths 0–3 could safely certify equivalence under sealed depths 4–6.

Result: **primary safety gate failed**.

- 9,600 classifications per method;
- generic shallow probability comparator: 1,191 operational false merges, precision 0.7497;
- OARL cross-fit + depth stability: 522 operational false merges, precision 0.8355;
- OARL recall: 0.7364;
- decisive boundary case: `op_noise=0.010`, sealed max difference 0.02926 > epsilon 0.020;
- OARL false merges on that class increased from 0/300 at 50k shots to 282/300 at 500k shots.

Interpretation: the current method handles finite-sample uncertainty better than the direct comparator but does not adequately handle **boundary extrapolation uncertainty**. More evidence inside an insufficient boundary can increase confidence in an unsafe merge.

See `evidence/v061/FINITE_SHOT_REPORT.md`.

## Next: v0.6.2 — prospective boundary extrapolation

This is now the highest-priority scientific gate.

### Question

> Can we certify that an apparent equivalence is likely to remain inside tolerance as the observational/interventional boundary changes, rather than merely certifying it on the boundary already observed?

### Required design

Use fresh seeds that have never been used to tune or evaluate v0.6.1.

Discovery evidence must remain shallow; sealed deeper circuits remain hidden until evaluation.

Candidate OARL method should:

1. estimate behavioral difference as a function of orientation/depth;
2. estimate uncertainty in the change of that difference across depth;
3. construct a conservative forward growth envelope;
4. propagate the envelope to a preregistered unseen horizon;
5. emit `EQUIVALENT` only if the entire upper envelope remains below epsilon;
6. emit `DISTINCT` only when observed evidence establishes violation;
7. otherwise emit `UNKNOWN`.

### Mandatory baselines

Do not compare only against the weak direct probability comparator. Include:

- direct simultaneous probability equivalence;
- linear trend extrapolation;
- isotonic/monotone growth envelope;
- polynomial regression with uncertainty;
- a simple Lipschitz/worst-case growth bound;
- pyGSTi gauge provenance oracle as evaluator only;
- OARL relational boundary-extrapolation certificate.

If a generic trend/envelope method matches or dominates OARL, narrow the OARL-specific claim.

### Primary safety gate

Zero accepted merges whose sealed max difference exceeds the frozen epsilon, with useful equivalence recall under a preregistered minimum.

Do not lower a threshold after inspecting confirmatory failures. Any new threshold or model is a new prospective protocol.

## Still required: v0.5C practical gate

v0.5C remains necessary but is no longer the immediate priority.

### Admissibility certification

The system must distinguish certified admissible, certified invalid and unknown. The primary safety metric is invalid-as-valid rate because v0.4 showed that admitting a semantically invalid high-information action can be catastrophic.

### End-to-end finite-noise economics

Measure:

`cost(certificate evidence) + cost(certification) + cost(quotient OED)`

against:

`cost(exhaustive Generic OED)`.

Include evidence acquisition, certificate computation, score evaluations, wall-clock runtime, final correctness, false-high-confidence decisions and abstention.

Do not call the method deployable unless the full pipeline is cheaper while preserving correctness and risk.

## Later v0.6+ generalization

After the boundary-extrapolation gate:

1. run corrected DREAM4 Size100 confirmatory gate;
2. add another third-party executable benchmark with genuine redundant admissible views;
3. implement held-out-orientation representation generalization;
4. add a classical dynamical-system benchmark with known symmetries/equivalences;
5. add an ABM equifinality benchmark;
6. test non-Gaussian predictive families;
7. test non-affine and approximate transports with calibrated abstention;
8. run a prospective/blinded mechanism-discrimination task.

## Novelty gate

Before claiming a major methodological contribution, benchmark against symmetry/group reduction, canonicalization, bisimulation/behavioral equivalence, causal abstraction and generic experimental-design compression.

The novelty burden is not the fact that quotienting known duplicates saves search. It is whether an orientation-aware **discovery/certification/risk layer** can safely identify which distinctions survive changes of boundary and improve a useful frontier over generic alternatives.

## Repository engineering

- Keep evidence immutable by version.
- Tag confirmatory releases when tooling permits.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Preserve failed pilots and negative confirmatory results.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
