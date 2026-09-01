# v0.6.3 preregistration — finite-evidence safe quotient before fixed D-optimal design

**Status:** frozen before confirmatory output.

## Decisive question

> When the downstream optimizer is held fixed, can a finite-evidence `EQUIVALENT / DISTINCT / UNKNOWN` certification layer safely learn enough hidden redundancy in a large external experiment family to reduce downstream search without changing the D-optimal design result, and does that structural benefit survive certification cost accounting?

This gate is deliberately narrower than claiming a new optimal-design criterion. D-optimality remains the downstream optimizer for every method.

## External executable system

- `pygsti==0.10.2`
- model pack `smq1Q_XYI`
- candidate physical circuits: every `Gxpi2/Gypi2` sequence of depths 1–7 (254 physical circuits)
- each physical circuit is exposed through two hidden binary outcome conventions: ordinary and outcome-complemented, producing 508 candidate **views**

Outcome complementation is an invertible relabeling of a binary statistical experiment, not an OARL-specific affine construction. The certifier receives no `circuit_id`, complement flag, or oracle equivalence class.

## Mechanism-discrimination coordinates

The downstream task is local discrimination/estimation in three frozen coherent-rotation directions around the pyGSTi target model:

- uniform X rotation
- uniform Y rotation
- uniform Z rotation

Central finite differences use step `1e-4`. Exact local Fisher information matrices are evaluator-side quantities used by the fixed downstream D-optimal optimizer and oracle safety checks.

## Finite discovery evidence

Each view is evaluated on the following frozen mechanism probe library:

- target model;
- ±0.0025, ±0.0050 and ±0.0100 coherent rotations independently on X, Y and Z.

For every view × mechanism probe, two independent Bernoulli shot splits are generated. Confirmatory shot count is **4,000 shots per split**. Seeds are fixed in code and are not tuned after results.

## Hidden task-equivalence truth

Two candidate views are **task-equivalent** iff their exact evaluator-side Fisher information matrices agree within frozen relative Frobenius tolerance `1e-8`.

This is deliberately task-relative: the downstream algorithm is D-optimality, whose objective depends on these information matrices. A pair can therefore be structurally redundant for this task even if some higher-order observable differs.

The oracle quotient is built only from this evaluator-side relation and is unavailable to all learned baselines.

## Methods

All learned methods receive the same finite Bernoulli summaries and no hidden metadata.

1. **RAW** — no quotient; D-optimality searches all 508 views.
2. **ORACLE** — evaluator-only quotient under exact task-equivalence.
3. **POINT** — forced binary point-estimate similarity under identity/outcome-complement transport; no abstention.
4. **UCB** — single pooled simultaneous confidence-bound equivalence test; `UNKNOWN` otherwise.
5. **OARL-XFIT** — transport must agree on two independent splits; `EQUIVALENT` only when both simultaneous upper bounds fit inside the frozen response tolerance; `DISTINCT` only when pooled lower evidence is outside the distinct margin; otherwise `UNKNOWN`.

For POINT, UCB and OARL-XFIT, accepted equivalence edges are converted to classes with **complete-link safety clustering**: a new view may join a class only when its pair relation is `EQUIVALENT` to every current class member. UNKNOWN never merges.

## Pair shortlisting

To avoid making certification trivially quadratic, all learned compression methods use the same cheap canonicalized point-signature shortlist:

- canonicalize each view under `p` versus `1-p` by lexicographic choice;
- find the **4 nearest candidate signatures** by normalized RMSE;
- certify the union of these undirected candidate pairs.

Shortlisting recall against oracle-equivalent partners is reported explicitly. A missed oracle pair counts as lost compression, never as a successful certificate.

## Frozen thresholds

- shots per split: 4,000
- shortlist neighbours: 4
- familywise alpha: 0.001
- response equivalence tolerance: 0.020 probability units
- response distinct margin: 0.030 probability units
- task-equivalence relative-Frobenius tolerance: `1e-8`
- downstream greedy D-optimal selections: 8
- D-optimal ridge: `1e-9`
- circuit acquisition cost: circuit depth

No threshold may be changed after confirmatory output. A changed method becomes v0.6.4 or later.

## Downstream comparison

Every quotient is passed to the **same greedy D-optimal selector**. Representatives are chosen deterministically as the lowest-cost member of each learned class. For the selected representative set, evaluator-side exact FIMs are used only to score the downstream scientific outcome.

Report for every method:

- number of learned classes and compression fraction;
- pair precision/recall and false task merges;
- abstention where applicable;
- shortlist recall of oracle-equivalent partners;
- downstream D-opt log-determinant;
- selected experiment total depth cost;
- downstream score evaluations;
- certification pair count and cell comparisons;
- wall-clock runtime;
- break-even downstream-score cost required to amortize certification comparisons.

## Primary safety gate

OARL-XFIT passes the structural safety gate only if:

1. **zero accepted task-false merges**;
2. downstream D-opt log-determinant is no worse than RAW by more than `1e-8`;
3. selected total depth cost is no greater than RAW;
4. compression fraction is at least 20%.

## Incremental-utility gate

An OARL-specific advantage is established only if OARL-XFIT is not dominated by POINT or UCB on the joint frontier of:

- false task merges;
- downstream D-opt preservation;
- compression;
- certification burden / break-even cost.

If UCB or another generic baseline matches or dominates OARL-XFIT, the result supports safe finite-evidence quotienting as a useful *problem formulation* but not an OARL-specific certifier advantage.

## Integrity rules

- A scientific gate failure is a valid result and must not make CI itself fail.
- Execution/integrity errors may be repaired only without changing scientific thresholds, seeds or method logic.
- Confirmatory failures are preserved; no post-hoc threshold tuning on the same views/seeds.
- Blackwell/Le Cam comparison and classical optimal design are treated as prior art for experiment comparison/informativeness, not as OARL contributions.
