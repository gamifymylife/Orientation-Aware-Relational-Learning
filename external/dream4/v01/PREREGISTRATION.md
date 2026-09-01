# Preregistration — DREAM4 External Gate

## Claim under test

> Preserving the intervention-response boundary contains directed mechanism information
> that is lost when the same measurements are detached from intervention identity.

## Hypotheses

### H-D1 — intervention-boundary value

For targeted knockout data:

`AUPRC(KO_ID) > AUPRC(KO_ERASED)`

paired by DREAM4 network.

### H-D2 — modality replication

The same effect appears independently for knockdown data:

`AUPRC(KD_ID) > AUPRC(KD_ERASED)`.

### H-D3 — cross-boundary consistency

Directed edge evidence derived independently from KO and KD is positively associated.

### H-D4 — negative control

Random row/intervention permutations do not systematically preserve the directed
network-recovery advantage.

## Fixed estimator

For perturbation matrix `X`, wild-type vector `w`, source gene `i`, target gene `j`:

`effect[i,j] = abs((X[i,j] - w[j]) / s[j])`

where `s[j]` is the robust across-intervention scale of gene `j`, estimated by MAD and
falling back to standard deviation if MAD is zero.

The self-edge diagonal is zeroed.

The identity-erased control applies a deterministic seeded permutation to the
mapping between intervention targets and response rows **without changing X**.

KO/KD consensus uses the arithmetic mean of min-max-normalized KO and KD score
matrices.

No tuning against gold-standard edges is permitted.

## Seeds

Identity-erasure permutations:

`20260831 + 1000 * network_id + repeat`

with 100 repeats per network.

The identity-preserved estimator is deterministic.

## Statistics

For each network:

- AUPRC
- AUROC
- AUPRC / prevalence
- top-|E| precision

For erased controls report the distribution over 100 permutations.

Confirmatory paired statistic:

For each network and modality, compare the fixed identity-preserved score with
the mean erased-control score.

Pool the ten paired effects (5 networks × 2 modalities) for a hierarchical/simple
paired bootstrap, resampling networks first and modalities within network.

Report median effect and 95% bootstrap interval.

## Pass condition

- positive identity effect in >= 4/5 networks for KO;
- positive identity effect in >= 4/5 networks for KD;
- pooled median AUPRC difference > 0;
- bootstrap 95% CI excludes 0;
- identity-preserved normalized AUPRC > 1 on >= 3/5 networks for at least one modality.

## Failure interpretation

If the effect fails:

- do not claim DREAM4 external support;
- keep the historical Meselson-Stahl / Luria-Delbruck result separate;
- investigate whether the intervention-response relation is too indirect/noisy for
  this estimator;
- any method revision requires a development/confirmatory split.

## Not claimed

This test does not establish:

- causal sufficiency of expression perturbations;
- exact orientation equivalence classes;
- superiority to specialist GRN inference algorithms;
- prospective scientific discovery.
