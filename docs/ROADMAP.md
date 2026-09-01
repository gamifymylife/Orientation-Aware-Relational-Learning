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

### Completed: v0.6.1 pyGSTi finite-shot external gate

The deterministic gauge-equivalence smoke gate passed. The preregistered finite-shot competitive gate then asked whether shallow evidence at circuit depths 0–3 could safely certify equivalence under sealed depths 4–6.

Result: **primary safety gate failed**.

- 9,600 classifications per method;
- generic shallow probability comparator: 1,191 operational false merges, precision 0.7497;
- OARL cross-fit + depth stability: 522 operational false merges, precision 0.8355;
- decisive boundary case: `op_noise=0.010`, sealed max difference 0.02926 > epsilon 0.020;
- OARL false merges on that class increased from 0/300 at 50k shots to 282/300 at 500k shots.

Interpretation: more evidence inside an insufficient boundary can increase confidence in an unsafe merge.

### Completed: v0.6.2 Boundary Information Audit

v0.6.2 tested evidence quantity versus information span directly.

- initial Fisher spectrum approximately `[0, 1, 1]`;
- initial rank 2, nullity 1;
- repetition factors 1, 10, 100 and 1000 all remained rank 2;
- at 1000x repetition the spectrum was approximately `[0, 1000, 1000]`;
- one depth-2 circuit completed rank 3;
- OARL-motivated null-space coverage and greedy D-optimality both reached rank 3 at added depth cost 2.

Interpretation: the “100 A's do not create a new informational direction” phenomenon is cleanly demonstrated, but rank-aware measurement selection is established optimal-design territory rather than an OARL novelty.

### Completed: v0.6.3 Safe Quotient Before Fixed D-Optimal Design

v0.6.3 finally held the downstream optimizer fixed and tested the structural quotient layer itself.

Frozen benchmark:

- 254 physical pyGSTi circuits, depths 1–7;
- two hidden binary outcome conventions per circuit;
- 508 candidate views;
- 19 mechanism probes;
- two independent 50,000-shot evidence splits;
- task-equivalence oracle: exact equality of local Fisher matrices at relative tolerance `1e-8`;
- same 8-step greedy D-optimal selector with replacement for every method.

Result: **primary structural safety gate failed; OARL-specific utility not established**.

- RAW: 508 classes, D-opt logdet 11.3141815, 4,064 score evaluations;
- ORACLE: 170 classes, 66.5% compression, identical D-opt logdet and depth cost, 1,360 score evaluations;
- POINT: 216 classes, 1,143 false task merges, D-opt logdet 11.1466039;
- UCB: 225 classes, 1,032 false task merges, D-opt logdet 11.1466039;
- OARL-XFIT: 292 classes, 42.5% compression, **555 false task merges**, pair precision 0.2620, but the RAW D-opt logdet and depth cost were preserved exactly.

The oracle result proves there is a large real structural-compression opportunity in this external candidate space. The failure is in **learning the correct equivalence relation safely**.

The critical lesson is that finite response-level similarity is not the same object as task-relative Fisher/D-optimal equivalence. Near-equal probe probabilities can have materially different local derivatives/Fisher geometry.

See `evidence/v063/V063_RESULT.md`.

## Next: v0.6.4 — task-aligned equivalence certification

This is now the highest-priority scientific gate.

### Decisive question

> Can finite evidence certify that substituting one experiment for another changes the downstream task by no more than a preregistered amount, rather than merely certifying that their observed response vectors are close?

The v0.6.3 failure says the certifier must target the object that the quotient is required to preserve.

### Candidate preserved objects

For the current D-optimal task, prospective methods may certify one of the following directly:

1. **Fisher-information distortion**
   - estimate local sensitivities from finite probe evidence;
   - construct simultaneous uncertainty sets for the sensitivity vectors;
   - derive an upper bound on relative FIM distortion under substitution;
   - merge only when the entire bound lies inside a frozen tolerance.

2. **D-optimal objective distortion**
   - bound the worst-case change in `log det(I + F_e)` over a preregistered family of current-information states `I`;
   - certify substitution only when the decision value difference is uniformly small.

3. **Decision-theoretic / deficiency-style distortion**
   - define a task-restricted loss family;
   - estimate a Blackwell/Le Cam-inspired deficiency or simulation bound between candidate experiments;
   - certify only when the implied worst-case decision-risk increase is within tolerance.

These are alternatives, not three claims to combine indiscriminately. The chosen v0.6.4 method must be frozen before confirmatory evidence.

### Mandatory baselines

At minimum compare against:

- RAW no quotient;
- ORACLE task quotient;
- point response similarity;
- response UCB equivalence;
- direct noisy-FIM similarity;
- conservative FIM confidence-bound equivalence;
- a Blackwell/Le Cam-inspired task-restricted comparison where computationally tractable;
- OARL task-aligned `EQUIVALENT / DISTINCT / UNKNOWN` certificate.

The same downstream D-optimal algorithm must remain fixed for every method.

### Primary safety endpoint

False accepted substitutions measured against the **task oracle**, not generic response similarity.

Zero false task merges remains the preferred primary gate. If a nonzero tolerance is used, it must be defined prospectively as a bound on downstream decision/information distortion, not chosen after seeing results.

### Utility endpoint

Only after safety passes, measure:

`cost(structural evidence + certification + quotient D-opt)`

against

`cost(raw D-opt)`.

The v0.6.3 break-even estimate (~1,511 probability-cell operations per saved D-opt score evaluation for OARL-XFIT) is descriptive only because the safety gate failed.

### Kill / narrowing criterion

If a generic conservative FIM/deficiency baseline safely learns the quotient at equal or lower cost, narrow OARL to the broader **task-aligned structural audit / abstention architecture** rather than claiming a unique certification algorithm.

If no finite-evidence method obtains useful compression without false task merges, preserve v0.5 synthetic results and treat safe external quotient discovery as unresolved rather than deployable.

## Paper programme

The August 2026 OARL paper is historical. The current manuscript is `paper/CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md`.

The paper should now make the evidence trajectory explicit:

1. fixed-boundary exact equivalence survives IID repetition;
2. Fisher information magnitude can grow without information span growing;
3. v0.6.1: confidence can outpace boundary adequacy;
4. v0.6.2: one genuinely new observation direction can add rank that 1000x repetition cannot;
5. classical D-optimality already solves the local rank-selection problem;
6. v0.6.3: even when a large safe oracle quotient exists, generic response equivalence is not a safe proxy for the downstream task-equivalence relation;
7. therefore the remaining contribution is **task-aligned, risk-bounded structural certification with abstention before ordinary optimal design**.

Do not submit the manuscript as a strong algorithm paper until v0.6.4 or an equivalent task-aligned held-out gate resolves the certification burden.

## Still required: v0.5C practical gate

v0.5C remains necessary but is downstream of the task-aligned safety problem.

### Admissibility certification

The system must distinguish certified admissible, certified invalid and unknown. The primary safety metric is invalid-as-valid rate.

### End-to-end finite-noise economics

Measure:

`cost(certificate evidence) + cost(certification) + cost(quotient OED)`

against:

`cost(exhaustive Generic OED)`.

Do not call the method deployable unless the full pipeline is cheaper while preserving correctness and risk.

## Later generalization

After v0.6.4:

1. run corrected DREAM4 Size100 confirmatory gate;
2. add another third-party executable benchmark with genuine redundant admissible views;
3. implement held-out-orientation representation generalization;
4. add a classical dynamical-system benchmark with known symmetries/equivalences;
5. add an ABM equifinality benchmark;
6. test non-Gaussian predictive families;
7. test non-affine and approximate transports with calibrated abstention;
8. run a prospective/blinded mechanism-discrimination task.

## Novelty gate

The novelty burden is not the fact that quotienting known duplicates saves search, not the fact that repeated sampling cannot create missing Fisher rank, and not the classical comparison of statistical experiments.

The remaining burden is whether an orientation-/boundary-aware **discovery, certification and abstention layer** can learn a task-valid structural quotient from finite evidence and improve safety or total cost when the downstream inference algorithm is held fixed.

## Repository engineering

- Keep evidence immutable by version.
- Tag confirmatory releases when tooling permits.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Preserve failed pilots and negative confirmatory results.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
