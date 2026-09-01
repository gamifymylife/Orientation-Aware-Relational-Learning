# v0.6.4 preregistration — task-aligned finite-evidence equivalence

**Status:** frozen before any v0.6.4 confirmatory output.

## Decisive question

> Can finite evidence certify that two candidate experimental views are interchangeable for the **actual downstream D-optimal task**, rather than merely similar in response space, with zero operational false merges and useful compression?

v0.6.3 established that response-level similarity is the wrong primary certificate: OARL-XFIT preserved the downstream D-optimal result but accepted 555 pairs whose evaluator-side Fisher geometry was not task-equivalent. v0.6.4 therefore certifies the object the quotient is required to preserve.

## Development / confirmation separation

The completed v0.6.3 artifact is development evidence only. It was used to choose a non-degenerate task tolerance before this protocol was frozen. On its shortlisted pairs the evaluator-side Fisher-distance distribution had a large separation: a near-equivalent cluster lay well below 0.20 while clearly different pairs occupied a much larger-distance regime. No v0.6.4 finite-evidence output was inspected before freezing the values below.

v0.6.4 uses fresh Bernoulli seeds `640401` and `640402`.

## External executable system

- `pygsti==0.10.2`
- model pack `smq1Q_XYI`
- all `Gxpi2/Gypi2` circuits of depths 1–7: 254 physical circuits
- two hidden outcome conventions per physical circuit (`p` and `1-p`): 508 candidate views

The hidden outcome convention is not supplied to learned methods.

## Downstream task

The downstream optimizer is identical for every method: 8-step greedy D-optimal design with replacement in three local coherent-rotation coordinates (uniform X/Y/Z rotation).

Evaluator-side exact local Fisher matrices are computed using central finite difference step `1e-4`. Learned methods never see these exact matrices.

## Finite discovery evidence

The finite probe library is frozen to 19 mechanism states:

- target;
- ±0.0025, ±0.0050 and ±0.0100 rotations independently on X, Y and Z.

For each view × probe, two independent Bernoulli count splits are drawn with **100,000 shots per split**. Local slopes are estimated by the frozen symmetric linear fit over the three positive/negative scales, and each learned view receives an estimated 3×3 Fisher matrix.

## Task-relative evaluator truth

For exact evaluator-side Fisher matrices `F_i` and `F_j`, define symmetric relative Fisher distortion

`d_F(i,j) = ||F_i-F_j||_F / max(||F_i||_F, ||F_j||_F, 1e-12)`.

Also define a frozen D-optimal decision-value distortion over nine generic positive-definite anchor states:

`d_D(i,j) = max_S | gain_D(S,F_i) - gain_D(S,F_j) |`,

where `gain_D(S,F)=logdet(S+F)-logdet(S)` and anchors are isotropic scales 0.1, 1, 10 plus all permutations of diag(0.1,1,10).

Two views are operationally **task-equivalent** iff both:

- `d_F <= 0.20`
- `d_D <= 0.05`

A clearly distinct margin is frozen at:

- `d_F >= 0.30` or
- `d_D >= 0.10`.

These are operational task tolerances, not claims of exact statistical-experiment identity. Exact outcome-complement duplicates remain a strict subset with zero true distortion.

## Pair shortlisting

All learned methods use the same shortlist. Using only pooled finite-evidence Fisher point estimates, each view contributes its 8 nearest neighbours by relative Fisher distance; the union of undirected pairs is certified. Missed evaluator-equivalent pairs count only as lost recall/compression.

## Methods

1. **RAW** — no quotient.
2. **ORACLE** — evaluator-only complete-link quotient under the frozen task-equivalence relation.
3. **TV-UCB** — generic response/distribution comparator. It chooses identity vs outcome-complement transport from pooled finite evidence and uses simultaneous Bernoulli response bounds. `EQUIVALENT` requires an upper response discrepancy ≤0.020; `DISTINCT` requires a lower discrepancy ≥0.030; otherwise `UNKNOWN`.
4. **FIM-POINT** — forced binary task-space point comparator. `EQUIVALENT` iff pooled estimated `d_F <=0.20` and pooled estimated `d_D <=0.05`; otherwise `DISTINCT`.
5. **FIM-UCB** — pooled parametric-bootstrap task-space bound. `EQUIVALENT` only when the 0.99 bootstrap upper bounds satisfy both task tolerances; `DISTINCT` when the 0.01 lower bound crosses either distinct margin; otherwise `UNKNOWN`.
6. **OARL-TASK-XFIT** — precision-first task-aligned certificate. It requires **both independent splits and the pooled evidence** to have 0.99 bootstrap upper bounds inside both task tolerances. `DISTINCT` requires pooled lower-bound evidence beyond a distinct margin; all other cases are `UNKNOWN`.

Bootstrap size is frozen at 128 draws with deterministic method seeds. The bootstrap is a conservative stability envelope for this benchmark; no universal coverage theorem is claimed.

All learned equivalence edges are converted to classes with complete-link safety clustering. `UNKNOWN` never merges.

## Frozen constants

- shots per split: 100,000
- evidence seeds: 640401 / 640402
- shortlist neighbours: 8
- bootstrap draws: 128
- bootstrap lower/upper quantiles: 0.01 / 0.99
- Fisher equivalence tolerance: 0.20
- Fisher distinct margin: 0.30
- D-opt anchor equivalence tolerance: 0.05
- D-opt anchor distinct margin: 0.10
- TV equivalence tolerance: 0.020 probability units
- TV distinct margin: 0.030
- downstream selections: 8
- downstream ridge: 1e-9
- allowed learned-vs-RAW final logdet loss: 0.005
- minimum OARL compression: 20%

No scientific constant, seed or method rule may be changed after confirmatory output. A changed method becomes v0.6.5 or later.

## Primary OARL safety gate

OARL-TASK-XFIT passes only if all are true:

1. zero accepted operational task-false merges;
2. final exact evaluator-side D-opt logdet is no worse than RAW by more than 0.005;
3. selected total depth cost is no greater than RAW;
4. compression is at least 20%.

The ORACLE quotient is also required to preserve RAW logdet within 0.005; otherwise the operational equivalence tolerance itself is judged too loose for this task.

## Incremental-utility gate

An OARL-specific certifier advantage is established only if OARL-TASK-XFIT is not dominated by TV-UCB or FIM-UCB on the joint frontier of:

- operational false merges;
- downstream logdet preservation;
- compression;
- abstention / recall;
- certification burden and break-even cost.

If generic FIM-UCB matches or dominates OARL-TASK-XFIT, the result supports **task-aligned equivalence certification** but not an OARL-specific cross-fit advantage.

## Cost accounting

Report separately:

- finite evidence shots;
- certified pair count;
- bootstrap work units;
- downstream score evaluations;
- selected acquisition depth cost;
- wall-clock runtime;
- downstream-score break-even cost required to amortize finite certification evidence.

The existence of a safe quotient is not enough to claim economic utility if discovering it costs more than exhaustive RAW search.

## Integrity

A scientific failure is valid output and must not fail CI. CI failure is reserved for execution/integrity errors. Negative results are preserved and thresholds are not repaired on the same confirmatory seeds.