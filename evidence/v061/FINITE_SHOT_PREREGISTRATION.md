# v0.6.1 Finite-Shot Competitive Gate — Preregistration

Status: **PROSPECTIVE / NO FINITE-SHOT RESULT YET**

This protocol is frozen after the successful deterministic pyGSTi smoke gate and before inspecting finite-shot confirmatory outcomes.

## Question

Can a benchmark-neutral, precision-first OARL certificate use only shallow finite-shot circuit evidence to avoid unsafe equivalence merges that a simpler observable-probability comparator accepts, while retaining useful equivalence recall?

The decisive comparison is not against pyGSTi's gauge oracle. Gauge freedom is already established in GST. The question is whether OARL's relational safety logic adds anything over ordinary probability-space equivalence testing.

## External system

- `pygsti==0.10.2`
- model pack `smq1Q_XYI`
- gates `Gxpi2`, `Gypi2`
- discovery circuits: all gate strings of length 0–3 (15 circuits)
- sealed evaluator circuits: all gate strings of length 4–6 (112 circuits)

The sealed circuits are never supplied to any classifier.

## Pair construction

Two independently gauge-transformed representations are constructed for each challenge so raw parameter distance is deliberately confounded by representation choice.

### Gauge-equivalent challenges

Both members come from the same physical target model and differ only by independently generated invertible full-gauge transformations.

### Physical-control challenges

One member comes from the target model and the other from a depolarized model. Frozen operation-noise levels are:

`0.002, 0.005, 0.010, 0.020, 0.030, 0.050, 0.080`.

Both members are independently gauge transformed before raw-parameter comparison. Gauge matrices are evaluator provenance only; classifiers receive no gauge matrix.

## Two truth notions — both must be reported

Finite samples cannot establish exact equality of continuous probabilities. We therefore refuse to hide the distinction between physical identity and operational equivalence.

1. **physical truth**: only pure-gauge pairs are physically equivalent; every depolarized pair is physically distinct.
2. **operational truth**: a pair is epsilon-equivalent when the maximum absolute probability difference over the 112 sealed circuits is at most `epsilon = 0.020`.

Primary finite-shot safety is evaluated against **operational truth** because the classifiers are explicitly asked to certify equivalence within a nonzero tolerance. Physical false merges are reported separately and must never be described as proof of physical identity.

## Shot budgets

Per model, per discovery circuit:

`50,000; 100,000; 250,000; 500,000` shots.

Counts are sampled directly from the exact pyGSTi circuit probabilities with NumPy binomial draws. No individual Bernoulli samples are materialized.

Confirmatory seeds: `1000–1299` inclusive.

Each seed contributes one pure-gauge pair and all seven physical-control levels at every shot budget.

Total planned classifications per method: `300 × 8 × 4 = 9,600`.

## Classifiers

All non-oracle methods receive only discovery-circuit evidence plus, for the intentionally naive baseline, raw model parameter vectors.

### A. Raw parameter distance

Gauge-naive negative control. `EQUIVALENT` iff raw parameter-vector L2 distance is at most `0.10`; otherwise `DISTINCT`.

This baseline is expected to fail under gauge transformations and is not a serious competitor.

### B. Generic simultaneous probability equivalence

A conventional probability-space equivalence comparator. For every discovery circuit, compute the observed difference in binomial proportions and a normal-approximation simultaneous confidence bound using Bonferroni familywise `alpha = 0.01` across 15 circuits.

- `EQUIVALENT` iff every simultaneous upper bound on absolute probability difference is at most `epsilon = 0.020`.
- `DISTINCT` iff any simultaneous lower bound exceeds epsilon.
- otherwise `UNKNOWN`.

This is the primary generic baseline. It uses the full shot budget.

### C. OARL relational safety certificate

OARL uses the same observable evidence but imposes two additional safety requirements motivated by the project's core asymmetry: missed compression costs compute; false compression can corrupt inference.

1. **cross-fit replication**: split each shot budget deterministically into two independent halves; each half must independently satisfy the same simultaneous epsilon-equivalence gate;
2. **orientation/depth stability**: on each half, compute mean absolute pair difference separately at circuit depths 0, 1, 2 and 3. Fit a least-squares slope versus depth. An equivalence certificate is rejected to `UNKNOWN` when either split has positive divergence slope greater than `epsilon / 10 = 0.002` probability per circuit layer.

`DISTINCT` is emitted only when a discovery-circuit lower confidence bound exceeds epsilon. Everything else is `UNKNOWN`.

The depth rule is deliberately simple and benchmark-neutral: it does not know quantum mechanics, depolarization, the hidden gauge transformation, or the sealed circuits. It asks whether an apparent shallow equivalence is stable as the observational orientation (circuit depth) changes.

### D. pyGSTi provenance oracle

Reports whether the pair was generated by pure gauge transformation or by a physical perturbation. This is evaluator truth, not a learnable competitor.

## Primary endpoints

At each shot budget and aggregated across budgets:

- operational false-merge count/rate;
- operational equivalence precision;
- operational equivalence recall;
- UNKNOWN/abstention rate;
- sealed-circuit violation rate among accepted merges.

Secondary:

- physical false-merge count;
- raw-distance failure under gauge changes;
- classification counts by physical perturbation level;
- incremental circuit/shot cost of OARL cross-fitting;
- compression proxy = fraction of operationally equivalent challenges accepted.

## Incremental-utility gate

OARL earns a **narrow positive incremental-utility result** only if all are true:

1. OARL has zero operational false merges across the full confirmatory grid;
2. generic probability equivalence has at least one operational false merge **or** OARL has strictly higher operational precision at a shot budget where both accept at least 25 operationally equivalent pairs;
3. OARL retains aggregate operational equivalence recall of at least 0.20;
4. every OARL-accepted merge respects the sealed epsilon criterion;
5. the result does not require gauge matrices or sealed-circuit access.

If both methods have zero operational false merges, no superiority claim is made unless OARL improves recall at matched zero false merges.

If the generic comparator matches or dominates OARL on safety and recall, the distinctive-method claim is narrowed.

## Kill / narrowing conditions

- Any OARL accepted merge with sealed max difference > 0.020 fails the primary safety gate.
- Aggregate OARL operational recall < 0.20 fails usefulness.
- If the depth-stability rule only helps because its threshold is retuned after confirmatory inspection, the result is exploratory, not confirmatory.
- Physical-control pairs that fall inside the sealed epsilon band must be reported as physically distinct but operationally equivalent; they may not be relabelled as physically identical.
- Exact gauge equality is not inferred from finite samples.

## Claim boundary

A pass would show that a simple OARL-style cross-fit + orientation-stability certificate can improve the safety frontier of shallow finite-shot equivalence discovery in this independently authored GST domain. It would not establish a new quantum-tomography result, general approximate equivalence, semantic admissibility, or broad real-world generalization.
