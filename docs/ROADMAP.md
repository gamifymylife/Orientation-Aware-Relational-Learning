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

Gate-set tomography supplies an independently established equivalence structure: gauge transformations can substantially alter internal representation while preserving observable circuit probabilities.

The deterministic smoke gate passed. The subsequent preregistered finite-shot competitive gate asked whether shallow evidence at circuit depths 0–3 could safely certify equivalence under sealed depths 4–6.

Result: **primary safety gate failed**.

- 9,600 classifications per method;
- generic shallow probability comparator: 1,191 operational false merges, precision 0.7497;
- OARL cross-fit + depth stability: 522 operational false merges, precision 0.8355;
- OARL recall: 0.7364;
- decisive boundary case: `op_noise=0.010`, sealed max difference 0.02926 > epsilon 0.020;
- OARL false merges on that class increased from 0/300 at 50k shots to 282/300 at 500k shots.

Interpretation: the current method handles finite-sample uncertainty better than the direct comparator but does not adequately handle **boundary uncertainty**. More evidence inside an insufficient boundary can increase confidence in an unsafe merge.

See `evidence/v061/FINITE_SHOT_REPORT.md`.

### Completed: v0.6.2 Boundary Information Audit

v0.6.2 tested the distinction between evidence quantity and information span directly in the external pyGSTi system.

Frozen local mechanism directions were uniform X/Y/Z rotations. The initial boundary was the two depth-1 circuits. Candidate probes were exhaustive circuits at depths 2–6.

Result: **structural gate passed; no OARL-specific selection advantage established**.

- initial Fisher spectrum approximately `[0, 1, 1]`;
- initial rank **2**, nullity **1**;
- repetition factors 1, 10, 100 and 1000 all remained rank **2**;
- at 1000x repetition the spectrum was approximately `[0, 1000, 1000]` — magnitude increased, span did not;
- the expanded 126-probe family reached rank **3**;
- one depth-2 circuit (`Gxpi2.Gypi2`) completed rank 3;
- OARL-motivated null-space coverage selected that circuit at added depth cost **2**;
- greedy D-optimality selected the same circuit at the same cost **2**;
- E-optimality and cosine diversity reached rank 3 at cost 3;
- random new-view selection reached rank 3 at cost 6.

Interpretation: the “100 A's do not create a new informational direction” phenomenon is cleanly demonstrated, but **rank-aware selection is not an OARL novelty**. Classical optimal-design machinery already solves this local selection problem at least as well in the frozen audit.

See `evidence/v062/V062_RESULT.md`.

## Next: v0.6.3 — active boundary vs repetition under finite cost

This is now the highest-priority scientific gate.

### Decisive question

> Given a finite budget, when should the system spend another sample on an existing boundary and when should it pay to acquire a genuinely different boundary?

The target is no longer merely rank completion. The gate must include finite-shot uncertainty, explicit probe cost, equivalence/abstention risk and downstream mechanism discrimination.

### Fresh evidence only

Use fresh seeds and, preferably, additional mechanism families not used to design v0.6.1 or v0.6.2.

The policy must not see sealed evaluator boundaries or hidden generating transforms.

### Mandatory competitors

At minimum include:

- repeat-current-boundary;
- random new-view selection;
- cosine/diversity selection;
- greedy D-optimality;
- greedy E-optimality;
- generic sensitivity/null-space rank design;
- generic Bayesian expected information gain where tractable;
- OARL boundary-equivalence + abstention + quotient-aware policy.

D/E-optimality and null-space coverage are not weak strawmen; v0.6.2 showed they are the correct local competitors.

### OARL-specific burden

OARL only earns incremental utility if its structural layer adds something classical design does not already provide. Candidate advantages that may be tested are:

1. safer refusal to quotient superficially redundant views;
2. lower false-merge risk at matched experimental cost;
3. explicit `UNKNOWN` handling when the available boundary family is insufficient;
4. cheaper search by certifying transport-equivalent experiment families before ordinary OED;
5. better total cost once evidence acquisition + certification + downstream search are counted together.

### Primary endpoints

- mechanism-identification correctness;
- false-high-confidence rate;
- false-equivalence/false-merge rate;
- abstention rate;
- total experimental cost;
- number of distinct boundaries acquired;
- repeated samples spent on already covered information directions;
- final information rank / condition where locally meaningful;
- total computation including certification.

### Kill / narrowing criterion

If standard D/E-optimal or generic Bayesian design matches OARL on safety and total cost without the structural certification layer, narrow OARL to a conceptual/equivalence-analysis framework rather than claiming a superior active measurement policy.

## Paper programme

The August 2026 OARL paper is historical. The current paper direction is `paper/CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md`.

Its central structure is:

1. define boundary-relative observational equivalence;
2. prove exact fixed-boundary IID repetition cannot break exact equivalence;
3. distinguish information magnitude from information span using the classical Fisher-rank result;
4. present v0.6.1 as a prospective failure showing confidence can outpace boundary adequacy;
5. present v0.6.2 as the clean executable rank demonstration;
6. explicitly show D-optimality ties the OARL-motivated local selector;
7. locate the remaining novelty burden in safe equivalence/abstention/quotienting upstream of standard OED;
8. make v0.6.3 the decisive algorithmic utility test.

Do not submit the new manuscript as a strong algorithm paper until v0.6.3 or an equivalent held-out utility gate resolves that burden.

## Still required: v0.5C practical gate

v0.5C remains necessary but is not the immediate priority.

### Admissibility certification

The system must distinguish certified admissible, certified invalid and unknown. The primary safety metric is invalid-as-valid rate because v0.4 showed that admitting a semantically invalid high-information action can be catastrophic.

### End-to-end finite-noise economics

Measure:

`cost(certificate evidence) + cost(certification) + cost(quotient OED)`

against:

`cost(exhaustive Generic OED)`.

Include evidence acquisition, certificate computation, score evaluations, wall-clock runtime, final correctness, false-high-confidence decisions and abstention.

Do not call the method deployable unless the full pipeline is cheaper while preserving correctness and risk.

## Later generalization

After v0.6.3:

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

The novelty burden is not the fact that quotienting known duplicates saves search, nor the fact that Fisher-rank-aware design can seek new sensitivity directions. It is whether an orientation-aware **discovery/certification/risk layer** can safely determine which experimental distinctions survive changes of boundary and improve a useful frontier over established methods.

## Repository engineering

- Keep evidence immutable by version.
- Tag confirmatory releases when tooling permits.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Preserve failed pilots and negative confirmatory results.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
