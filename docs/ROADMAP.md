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

### Completed: v0.6 CSuite suitability pilot

The adapter ran, but the tested published CSuite systems expose too few candidate intervention views for a serious pairwise equivalence-discovery benchmark. The suitability failure is preserved rather than manufacturing OARL-specific views.

### Completed: v0.6.1 pyGSTi finite-shot external gate

Result: **primary safety gate failed**.

- generic shallow comparator: 1,191 operational false merges;
- OARL cross-fit + depth stability: 522 operational false merges;
- on the decisive `op_noise=0.010` class, OARL false merges rose from 0/300 at 50k shots to 282/300 at 500k shots.

Interpretation: more evidence inside an insufficient boundary can increase confidence in an unsafe merge.

### Completed: v0.6.2 Boundary Information Audit

- initial Fisher rank 2 of 3;
- repetition factors 1, 10, 100 and 1000 all remained rank 2;
- one new depth-2 circuit completed rank 3;
- OARL null-space coverage and greedy D-optimality tied at added cost 2.

Interpretation: information magnitude and information span are different, but rank-aware measurement selection is classical optimal-design territory rather than an OARL novelty.

### Completed: v0.6.3 Safe Quotient Before Fixed D-Optimal Design

The downstream D-optimal algorithm was held identical for every method.

Result: **primary structural safety gate failed**.

- RAW: 508 classes, logdet 11.3141815, 4,064 score evaluations;
- ORACLE: 170 classes, 66.5% compression, identical downstream result;
- POINT: 1,143 false task merges;
- UCB: 1,032 false task merges;
- OARL-XFIT: 42.5% compression and preserved RAW logdet, but **555 false task merges**.

Interpretation: a large safe quotient exists, but finite response similarity is the wrong object to certify. Near-equal responses can have different local derivative/Fisher geometry.

See `evidence/v063/V063_RESULT.md`.

### Completed: v0.6.4 Task-Aligned Equivalence Certification

v0.6.4 moved the certificate into the object the downstream D-optimal task actually uses: finite Fisher geometry plus D-optimal marginal-value distortion.

Frozen benchmark:

- same external pyGSTi candidate family: 508 views;
- 19 mechanism probes;
- fresh seeds `640401` / `640402`;
- two independent 100,000-shot splits;
- 2,543 finite-FIM-shortlisted pairs;
- evaluator operational equivalence: relative Fisher distortion <=0.20 and frozen D-opt anchor distortion <=0.05;
- identical 8-step D-optimal downstream optimizer for every quotient.

Result: **safety repaired, useful compression failed**.

- RAW: 508 classes, logdet 11.3141815, 4,064 score evaluations;
- ORACLE: **91 classes**, **82.1% compression**, identical logdet and depth cost, 728 score evaluations;
- TV-UCB: 74.4% compression but **1,196 false task merges** and logdet loss 0.2652;
- FIM-POINT: 491 classes, **3.35% compression**, 21 accepted pairs, **0 false merges**, precision 1.000, identical logdet;
- FIM-UCB: 508 classes, **0% compression**, 0 false merges;
- OARL-TASK-XFIT: 508 classes, **0% compression**, 0 false merges, identical logdet.

Primary checks:

- oracle tolerance preserves RAW: PASS;
- OARL zero false task merges: PASS;
- OARL downstream preservation: PASS;
- OARL depth cost no greater than RAW: PASS;
- OARL compression >=20%: **FAIL**.

Under the frozen numerical evaluator, the family contained 3,842 view-level compatible pairs globally and 1,263 inside the learned shortlist. v0.6.5 later showed that this evaluator fragmented exact zero-Fisher classes, so these counts are preserved as evaluator-relative outputs rather than exact structural truth.

The frozen learned methods consumed **1,930,400,000 independently simulated view-shot units** each. FIM-UCB and OARL saved zero downstream score evaluations. Because ordinary/complement views are deterministic relabellings, shared physical acquisition would have been 965,200,000 shot units; the higher number remains the cost of the frozen implementation.

Historical diagnostic: task alignment fixed the v0.6.3 wrong-object problem relative to the frozen evaluator, but direct local derivative/Fisher estimation from independent finite shots was too noisy for the chosen envelope. v0.6.5 subsequently showed that finite evidence was not the only bottleneck: independent relabelling, near-zero numerical conditioning and an analytically solvable structural family were also confounded.

See `evidence/v064/V064_RESULT.md` and `evidence/v064/EVALUATOR_CORRECTION_NOTE.md`.

### Completed: v0.6.5 Structural Baseline and Evaluator Audit

v0.6.5 first tested whether the pyGSTi family still contained a legitimate learned-discovery target after admitting the strongest generic known-structure baseline.

The gate corrected three confounds before evaluating utility:

1. ordinary/complement views were separated as deterministic relabellings rather than independent physical candidates;
2. analytic integer/half-integer `SO(3)` transport replaced central finite differences as the exact evaluator;
3. exact and operational relations were tested for transitivity and insertion-order stability before quotient language was used.

The confirmatory family was all 256 gate words at held-out depth 8.

Result:

- RAW-VIEWS: 512 classes, logdet 12.3273695, 4,096 score evaluations;
- VIEW-CANONICAL: 256 physical classes, identical logdet, 2,048 score evaluations;
- generic STRUCTURAL-TRANSPORT: **50 exact classes**, **80.47% physical compression**, identical logdet, 400 score evaluations, zero Bernoulli shots;
- OPERATIONAL-ORACLE: exactly the same 50 classes and downstream result;
- exact and operational relations were reflexive, symmetric and transitive;
- 257 insertion orders all produced 50 classes and the same downstream result.

The structural-baseline utility gate passed. The learned-discovery suitability gate failed because residual oracle compression beyond the generic structural baseline was **0%**. The adaptive learned stage was therefore not run.

The retrospective v0.6.4 correction found 58 analytic physical classes rather than 91 legacy finite-difference classes. The old evaluator missed 3,261 of 4,158 analytically exact equivalent physical pairs because tiny numerical matrices around true zero Fisher norm were compared with a purely relative metric.

Interpretation: generic analytic transport completely solves this ideal Clifford family. That supports structural canonicalization but cannot support an OARL-specific learned algorithm claim. The pyGSTi line is closed for learned-discovery utility.

See `evidence/v065/V065_RESULT.md`.

## Completed: v0.6.6 — black-box mutation-matrix suitability gate

v0.6.6 screened independently authored Defects4J mutant-test kill matrices. Tests were candidate experiments and held-out mutant kill vectors supplied an exact, non-numerical task-equivalence relation.

Frozen result: **overall suitability gate failed** because `Closure-118` retained only 67 development-active eligible tests, below the required 200. The other three matrices exposed strong exact oracle compression:

- Lang-33: 258 eligible tests → 147 exact held-out classes, 43.02% compression;
- Math-22: 225 → 114, 49.33% compression;
- Time-6: 1,225 → 165, 86.53% compression.

All exact oracle quotients preserved the fixed greedy maximum-coverage result. Generic development-signature grouping was unsafe, producing 51,316 held-out false merge pairs across the four matrices.

Interpretation: the four-matrix preregistered gate failed, but mutation testing is the first external domain in this programme to expose both large hidden task redundancy and a real finite-evidence generalization problem beyond metadata or an exposed analytic model.

See `evidence/v066/V066_RESULT.md`.

## Next: v0.6.7 — prospective mutation-equivalence certification

The inspected v0.6.6 held-out columns cannot be reused for a prospective learned claim. Select new fault matrices using development-only activity, then freeze the target faults and mutant splits before fitting or evaluating a learner.

### Required benchmark properties

The next family must provide:

1. at least 200 genuinely distinct physical candidate experiments after deterministic metadata canonicalization;
2. at least 20% task-preserving oracle compression beyond all known generic structural/canonicalization baselines;
3. transformations that are not directly supplied by candidate identifiers or exactly calculable from an exposed simulator;
4. a trustworthy analytic, symbolic or independently converged evaluator that remains well-conditioned at zero information;
5. an exact equivalence relation, or explicit safe-substitution graph semantics if approximate compatibility is non-transitive;
6. a held-out family whose task truth was not used to design the learner;
7. realistic shared-observation and wall-clock cost accounting.

Candidate faults must be screened using development-only activity before algorithm work. A benchmark-suitability failure must be preserved rather than repaired by manufacturing duplicate views.

### Frozen comparator burden

Preregister structural proposal plus adaptive task certification against:

- deterministic canonicalization;
- generic symmetry/transform discovery;
- generic nearest-signature proposal;
- generic sequential confidence testing;
- RAW and evaluator-only oracle bounds.

The learned method must strictly improve the zero-false-merge compression/cost frontier. Evidence cost must count test-mutant executions, and end-to-end economics require measured execution time rather than binary-cell counts alone. Otherwise narrow OARL to the boundary-relative identifiability and structural-audit framework.

## Paper programme

The August 2026 OARL paper remains historical. The current manuscript is `paper/CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md`.

The paper should preserve the failure sequence rather than hide it:

1. exact fixed-boundary equivalence survives IID repetition;
2. Fisher magnitude can grow without span growing;
3. v0.6.1: confidence can outpace boundary adequacy;
4. v0.6.2: a new boundary adds rank that 1000× repetition cannot, while D-optimality already handles the local selection problem;
5. v0.6.3: response similarity gives useful compression but unsafe task merges;
6. v0.6.4: task-aligned finite-Fisher certification collapses to zero useful coverage under its frozen numerical evaluator;
7. v0.6.5: analytic transport reveals that the evaluator fragmented exact zero-Fisher classes and that generic known structure exhausts the held-out oracle without finite evidence;
8. v0.6.6: external mutation matrices expose a genuine hidden redundancy target, but the four-matrix suitability gate fails because Closure-118 has too few eligible tests;
9. the remaining open question is whether a prospective certifier can recover useful exact mutation-test equivalence with zero held-out false merges.

Do not submit the manuscript as a strong algorithm paper. v0.6.5 closes the pyGSTi line and v0.6.6 identifies a mutation-testing target without evaluating a learner. A new-fault prospective gate must establish safe incremental utility first.

## Still required: practical admissibility and end-to-end economics

Admissibility certification remains unresolved. The system must distinguish certified admissible, certified invalid and unknown, with invalid-as-valid as the primary safety error.

End-to-end economics must include evidence acquisition, certification, downstream score evaluations, wall time, final correctness and abstention. Do not call the method deployable unless the full pipeline is cheaper while preserving risk.

## Later generalization

After v0.6.5:

1. add another third-party executable benchmark with genuine redundant admissible views;
2. run corrected DREAM4 Size100 only if the benchmark supports the relevant quotient task;
3. add a classical dynamical-system symmetry benchmark;
4. add an ABM equifinality benchmark;
5. test non-Gaussian predictive families;
6. test non-affine and approximate transports;
7. run a prospective/blinded mechanism-discrimination task.

## Novelty gate

The novelty burden is not known symmetry reduction, Fisher-rank design, Blackwell comparison, or the fact that quotienting known duplicates saves search.

The remaining burden is whether a boundary-aware **discovery + certification + abstention** layer can learn a task-valid quotient from finite evidence and improve the safety/coverage/cost frontier while the downstream optimizer is held fixed.

## Repository engineering

- Keep evidence immutable by version.
- Never overwrite preregistered apparatus after a mismatch; issue a new version.
- Preserve failed pilots and negative confirmatory results.
- Tag confirmatory releases when tooling permits.
- Add independent reproduction when feasible.
- Select an explicit software/content license before external reuse is encouraged.
