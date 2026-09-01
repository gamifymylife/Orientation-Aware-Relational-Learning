# v0.6.2 Boundary Information Audit — Preregistration

Status: **PROSPECTIVE / NO v0.6.2 RESULT YET**

## Motivation

v0.6.1 established a specific failure mode: repeated finite-shot evidence inside a shallow observational boundary can become increasingly precise while remaining unsafe for equivalence claims at a deeper boundary. The next question is therefore not whether more samples reduce sampling error. They do. The question is whether repeated evidence adds new *distinguishing directions*.

## Core proposition tested

For a fixed experimental boundary `b`, IID repetition scales the per-observation Fisher information matrix without changing its rank or null space:

`I_b^(n)(theta) = n I_b(theta)`.

Therefore, for `n > 0`,

`rank(I_b^(n)) = rank(I_b)` and `null(I_b^(n)) = null(I_b)`.

This proposition is standard information geometry / identifiability theory, not an OARL novelty claim. v0.6.2 uses it as an externally grounded diagnostic principle.

## External system

- package: `pygsti==0.10.2`
- model pack: `smq1Q_XYI`
- target: independently implemented pyGSTi one-qubit gate-set model
- candidate experimental probes: circuits over `Gxpi2` and `Gypi2`

## Local mechanism coordinates

The audit uses three small, independently defined coherent perturbation directions around the pyGSTi target model:

1. uniform X-axis rotation;
2. uniform Y-axis rotation;
3. uniform Z-axis rotation.

For each circuit, response sensitivity to each direction is estimated by frozen central finite differences with step `h = 1e-4`.

These directions are used only to define a local three-dimensional mechanism space. Gauge transforms are not supplied to the selector.

## Bernoulli Fisher contribution

For a circuit with target success probability `p` and local sensitivity vector `s = dp/dtheta`, the per-shot local information contribution is

`F_c = s s^T / max(p(1-p), variance_floor)`.

Frozen `variance_floor = 1e-9`.

The information matrix for a set of circuits is the sum of their contributions. Repeating the same circuit set by factor `n` multiplies the matrix by `n` exactly in this audit.

## Boundary construction

Circuit depths 1 through 6 are generated exhaustively over the two gates.

- initial observational boundary: **all depth-1 circuits**;
- candidate new probes: every circuit at depths 2 through 6;
- circuit execution cost: circuit depth.

The initial boundary has two circuits, so its local sensitivity matrix cannot have rank greater than two in the three-dimensional mechanism space. This is a structural fact fixed before execution, not a result inferred from the data.

## Primary structural endpoints

1. **Repeat-rank invariance** — multiplying the depth-1 information matrix by repetition factors `1, 10, 100, 1000` must leave numerical rank and null-space dimension unchanged.
2. **Boundary expansion** — at least one admissible circuit outside the initial depth-1 boundary must contribute nonzero information in the initial information null space.
3. **Rank completion** — determine whether adding new circuit orientations can increase local information rank to three.

Numerical rank tolerance is frozen at `1e-9 * max_eigenvalue`, with an absolute floor of `1e-12`.

## Selection policies

All policies start with the same depth-1 boundary and select additional circuits from depths 2–6 without replacement until full rank is reached or no candidate remains.

### 1. repeat-only control

Spend additional cost only on the existing depth-1 boundary. By construction this can scale information magnitude but cannot change its span.

### 2. random-new-view

Select a new candidate circuit uniformly at random with frozen RNG seed `6202`.

### 3. cosine-diversity

Choose the candidate whose variance-normalized sensitivity direction has the smallest maximum absolute cosine similarity to already selected sensitivity directions, normalized by circuit depth cost.

This is the direct baseline for the informal “100 A's” / redundant-direction intuition.

### 4. D-optimal greedy

Choose the circuit with the greatest regularized log-determinant gain per depth cost.

Frozen ridge: `1e-9 I`.

### 5. E-optimal greedy

Choose the circuit with the greatest increase in the smallest Fisher eigenvalue per depth cost.

### 6. null-space coverage

Choose the circuit with maximum variance-normalized sensitivity energy projected into the current Fisher null space, divided by depth cost. Rank gain is the primary tie-breaker; projected energy is secondary.

This policy is an OARL-motivated *boundary audit* candidate, but closely related rank/sensitivity-based experimental design already exists. It earns no novelty claim merely by working.

## Comparative endpoints

For each policy report:

- whether full local rank is achieved;
- number of new circuits selected;
- total added circuit-depth cost;
- final numerical rank;
- final minimum eigenvalue;
- final condition number over the positive eigenspectrum;
- selected circuit sequence.

## Scientific interpretation rules

### Strong negative for OARL-specific novelty

If D-optimal, E-optimal or another generic baseline reaches full rank at equal or lower cost than null-space coverage, the correct result is:

> The boundary-vs-repetition phenomenon is real, but this local information-design task does not establish an OARL-specific selection advantage over established optimal-design machinery.

### Narrow positive

A narrow OARL-specific result is allowed only if null-space coverage reaches the same or greater identifiable span at strictly lower cost than all generic baselines on a later held-out family, not merely this structural pilot.

### Conceptual support independent of algorithmic novelty

Even if generic optimal design wins, the project may still retain the broader boundary-relative equivalence / safe-quotienting programme. The paper must separate that conceptual contribution from any claim of a superior measurement-selection algorithm.

## Paper consequence

The new manuscript must distinguish:

- **sampling uncertainty** — reducible by repetition under a fixed boundary;
- **mechanism uncertainty** — uncertainty over latent alternatives;
- **boundary uncertainty** — uncertainty arising because the observation operator may suppress mechanism directions.

The paper must explicitly acknowledge classical identifiability, Fisher-information and optimal-design literature. It must not present fixed-boundary rank invariance or D/E-optimality as novel.

## Integrity rules

- Do not alter perturbation directions, finite-difference step, rank tolerance, circuit depths, initial boundary, costs, policy definitions or RNG seed after viewing the v0.6.2 result.
- Execution/API repairs may be made only when they preserve all scientific settings and must be documented.
- A negative comparison against D/E-optimality is a valid scientific result and must be preserved.
