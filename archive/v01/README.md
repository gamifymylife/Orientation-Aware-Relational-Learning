# Orientation-Aware Relational Learning Benchmark v0.1

A deliberately adversarial benchmark for testing whether **orientation-aware experiment selection**
provides substantial value beyond ordinary active experimental design.

The benchmark is designed around one central question:

> Does explicitly searching over admissible relational orientations, while accounting for cost and
> orientation-specific instability, identify hidden mechanisms more efficiently and reliably than
> fixed-orientation or generic experimental-design baselines?

## What this version tests

Each synthetic world contains:

- a hidden mechanism \(H^\*\);
- multiple candidate mechanisms \(H_1,\dots,H_N\);
- multiple admissible orientations \(\omega\);
- multiple interventions \(a\);
- a deliberately uninformative default orientation;
- alternative orientations with heterogeneous discriminatory power;
- orientation-specific experimental cost;
- orientation-specific instability;
- optional unmodelled perturbation that grows with instability.

An experiment is:

\[
e=(\omega,a)
\]

and the learner updates a posterior over candidate mechanisms after each observation.

## Policies

1. `passive`
   - stays at the default orientation;
   - samples an intervention without optimizing information.

2. `fixed_oed`
   - stays at the default orientation;
   - chooses the intervention with maximum estimated information gain.

3. `random_orientation`
   - randomly selects orientation and intervention.

4. `generic_oed`
   - searches the complete \((\omega,a)\) experiment space;
   - maximizes estimated information gain only.

5. `oarl_no_stability`
   - searches the same \((\omega,a)\) space;
   - maximizes information gain minus experimental cost.

6. `full_oarl`
   - searches the same \((\omega,a)\) space;
   - maximizes information gain minus experimental cost and orientation instability.

7. `oracle`
   - knows the true mechanism;
   - selects the experiment that maximally separates it from the posterior-weighted alternatives.
   - This is an upper-bound reference, not a deployable method.

## Primary metrics

### N95

\[
N_{95}
=
\text{number of experiments required until }
P(H^\*=H_{\mathrm{true}})\ge0.95
\]

### C95

Total experimental cost required to reach the same threshold.

### Identification success

Whether the policy reaches the threshold within the declared budget.

### Score evaluations

How many candidate experiments the acquisition policy evaluates.

### Wall-clock time

Actual policy runtime.

## The critical comparison

The benchmark is **not passed** merely because searching over orientation beats a fixed boundary.

The critical comparison is:

\[
\text{Full OARL}
\quad\text{vs}\quad
\text{Generic OED over the identical }(\omega,a)\text{ action space}.
\]

If these are approximately equal, orientation may be useful but behaves mainly as another experimental-design
variable.

If Full OARL wins materially and robustly, the additional orientation-specific structure is doing useful work.

## Go / no-go thresholds

These are intentionally demanding and should be preregistered before large runs.

### Useful

- >= 20% median reduction in C95 versus `generic_oed`;
- effect present in >= 75% of benchmark instances;
- bootstrap 95% confidence interval excludes zero;
- no material loss in identification success.

### Substantial

- >= 30% median reduction in C95 versus `generic_oed`;
- survives multiple mechanism counts, noise levels, cost regimes, and perturbation regimes.

### Best-practice candidate

Do **not** use this label from synthetic evidence alone.

Require:

- >= 20-30% median cost reduction;
- at least 3 substantively different domains;
- at least 1 external benchmark per domain;
- low false structural distinction rate;
- acceptable computational overhead;
- at least one independent replication.

## Important scientific caveat

The current synthetic generator creates a controlled environment in which the default orientation is
deliberately uninformative and alternative orientations can expose hidden mechanism differences.

That establishes whether the acquisition machinery behaves correctly under known ground truth.

It does **not** establish that real scientific, AI, engineering, or ABM problems have the same structure.

The correct escalation is:

1. synthetic relational mechanisms;
2. dynamical system identification;
3. ABM equifinality;
4. learned latent representations;
5. historical replay;
6. prospective external experiments;
7. independent replication.

## Run

Install:

```bash
pip install -e .
```

Quick benchmark:

```bash
python scripts/run_quick.py
```

Full configurable benchmark:

```bash
oarl-bench run \
  --seeds 100 \
  --mechanisms 8 16 32 \
  --noise 0.5 1.0 2.0 \
  --budget 60 \
  --orientations 12 \
  --interventions 16 \
  --output outputs/full_results.csv
```

Summarize:

```bash
oarl-bench summarize outputs/full_results.csv
```

## Information-gain modes

`proxy` is the default and is fast. It uses a Gaussian channel-capacity approximation:

\[
IG \approx \frac12\log\left(1+\frac{\operatorname{Var}_p[\mu_H]}{\sigma^2}\right)
\]

This is useful for large benchmark sweeps.

`quadrature` numerically estimates the discrete-hypothesis mutual information for the one-dimensional
Gaussian mixture using Gauss-Hermite quadrature. It is slower but should be used for confirmatory runs.

```bash
oarl-bench run --ig-mode quadrature ...
```

## What would falsify the practical thesis?

Treat the project as unsuccessful or substantially weakened if any of these persist after tuning and replication:

- `generic_oed` matches `full_oarl`;
- gains appear only in worlds deliberately constructed to favour orientation search;
- the stability penalty helps only because the benchmark's perturbation model was chosen to reward it;
- computational search cost exceeds saved experimental cost;
- gains disappear on external or real mechanism-identification problems.

That outcome would still leave multi-orientation classification as a mathematical object, but it would not
justify a broad AI or scientific best-practice claim.
