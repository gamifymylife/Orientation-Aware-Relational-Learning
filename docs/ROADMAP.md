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

The family contains 3,842 evaluator-side task-equivalent pairs globally and 1,263 inside the learned shortlist, so the failure is not absence of structure. It is finite-evidence certification power.

The frozen learned methods consumed **1,930,400,000 Bernoulli shot units** each. FIM-UCB and OARL saved zero downstream score evaluations. Even FIM-POINT's small safe quotient required roughly **14.2 million shot units per D-opt score evaluation saved**.

Diagnostic: task alignment fixed the v0.6.3 wrong-object problem, but direct local derivative/Fisher estimation from independent finite shots is too noisy and data-hungry. Among true-equivalent shortlisted pairs, the median pooled Fisher point distance was ~0.225 and the median pooled Fisher bootstrap UCB ~0.593; no true pair passed the frozen pooled D-opt decision UCB.

See `evidence/v064/V064_RESULT.md`.

## Next: v0.6.5 — structural transport first, adaptive task certification second

This is now the highest-priority scientific gate.

### Decisive question

> Can a cheap structural/transport proposal stage identify high-probability equivalence candidates, then allocate task-aligned evidence sequentially only where needed, achieving nontrivial safe compression at materially lower evidence cost than exhaustive pairwise Fisher certification?

The next method must not simply multiply IID samples across every view × probe cell. v0.6.4 shows that route is economically poor even before broader deployment concerns.

### Required architecture

```text
candidate experimental views
        ↓
cheap structural / transform proposal
        ↓
small candidate equivalence graph
        ↓
sequential task-aligned evidence
        ↓
EQUIVALENT | DISTINCT | UNKNOWN
        ↓
complete-link safe quotient
        ↓
unchanged D-optimal optimizer
```

### Structural proposal stage

Use only benchmark-neutral observable structure. Candidate mechanisms to test include:

- outcome-label permutation / complement hypotheses;
- canonicalized response signatures;
- transport consistency across mechanism probes;
- symmetry/canonicalization baselines;
- learned transform proposals without evaluator metadata.

The proposal stage may improve recall/cost but cannot itself declare a safe merge unless the transform is exact by construction.

### Adaptive certification stage

Instead of collecting the same probe budget everywhere:

1. start with a small frozen pilot shot budget per proposed pair;
2. estimate task/Fisher distortion uncertainty;
3. stop early as `DISTINCT` when a margin is crossed;
4. stop early as `EQUIVALENT` only when the task-distortion upper bound is inside tolerance;
5. otherwise allocate another evidence batch up to a preregistered cap;
6. unresolved pairs remain `UNKNOWN`.

Report the full distribution of evidence spent per pair, not only total runtime.

### Mandatory baselines

At minimum:

- RAW;
- ORACLE;
- exact/known transform canonicalization where applicable;
- generic nearest-signature + sequential confidence testing;
- generic pooled FIM sequential UCB;
- OARL transform-proposal + task-XFIT sequential certification.

If a generic transform/canonicalization pipeline dominates, narrow the OARL-specific claim.

### Primary gate

Require simultaneously:

1. zero operational task-false merges;
2. >=20% compression;
3. downstream D-opt logdet within the frozen tolerance of RAW;
4. no greater selected depth cost than RAW;
5. at least **10× lower finite-evidence cost** than the v0.6.4 exhaustive 1.9304B-shot reference, unless the downstream score cost independently justifies a smaller reduction.

The 10× target is a new v0.6.5 prospective requirement, not a reinterpretation of v0.6.4.

### Kill / narrowing criterion

If safe compression still requires evidence on the order of exhaustive acquisition, the project should stop presenting external finite-noise quotient discovery as an efficiency method. The surviving contribution would then be the boundary-relative identifiability / structural-audit framework and exact/synthetic quotienting results.

## Paper programme

The August 2026 OARL paper remains historical. The current manuscript is `paper/CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md`.

The paper should preserve the failure sequence rather than hide it:

1. exact fixed-boundary equivalence survives IID repetition;
2. Fisher magnitude can grow without span growing;
3. v0.6.1: confidence can outpace boundary adequacy;
4. v0.6.2: a new boundary adds rank that 1000× repetition cannot, while D-optimality already handles the local selection problem;
5. v0.6.3: response similarity gives useful compression but unsafe task merges;
6. v0.6.4: task-aligned Fisher certification repairs safety but collapses to zero useful coverage under conservative finite uncertainty;
7. v0.6.5 therefore tests whether structural transport + selective evidence can recover the oracle opportunity economically.

Do not submit the manuscript as a strong algorithm paper until v0.6.5 or an equivalent independent gate resolves the safety/coverage/cost frontier.

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
