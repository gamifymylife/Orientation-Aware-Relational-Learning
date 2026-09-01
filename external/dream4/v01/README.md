# OARL DREAM4 External Gate v0.1

This project is a **preregistered external falsification harness** for the
Orientation-Aware Relational Learning (OARL) claim that mechanism identifiability
depends on the boundary through which an experiment is represented.

It is designed for the official 2009 **DREAM4 In Silico Network Challenge** archive.

## Why DREAM4?

The benchmark was created independently of OARL. For each network the challenge
provides experimentally distinct views of the same underlying gene-regulatory mechanism:

- wild type;
- one knockout per gene;
- one knockdown per gene;
- perturbation/relaxation time series;
- gold-standard directed networks;
- held-out dual-knockout targets in the bonus round.

That gives a third-party mechanism with real experimental boundary structure.

## Primary gate

The decisive comparison is deliberately simple.

### Boundary A — perturbation identity preserved

For knockout experiment `i`, retain the fact that **gene i was intervened on** and the
full resulting response vector.

The edge score for `i -> j` is derived from the standardized response of gene `j`
to intervention on `i`.

### Boundary B — same values, perturbation identity erased

Use the **exact same response rows**, but destroy the mapping from each response row
to the gene that was intervened on.

This condition has the same numerical measurements and sample count. What it loses is
the relational boundary:

`which intervention -> which response`

If directed mechanism recovery collapses, the lost information was not "more data";
it was the intervention-response relation.

## Additional conditions

1. `KO_ID`: knockout response with intervention identity.
2. `KO_ERASED`: same knockout matrix, row/intervention identity permuted.
3. `KD_ID`: knockdown response with intervention identity.
4. `KD_ERASED`: same knockdown matrix, row/intervention identity permuted.
5. `KO_KD_CONSENSUS`: average normalized KO and KD edge evidence.
6. `TIME_SERIES`: simple lagged-regression baseline from the official time-series data.
7. `RANDOM`: prevalence-control baseline.

## Primary outcome

Directed edge recovery against the official gold standard:

- AUPRC;
- AUPRC / edge prevalence;
- AUROC;
- top-|E| precision;
- direction-sensitive recovery.

The primary paired effect is:

`AUPRC(KO_ID) - AUPRC(KO_ERASED)`

and independently:

`AUPRC(KD_ID) - AUPRC(KD_ERASED)`.

## Acceptance rule fixed before seeing results

Call the external Gate-1 effect **supported** only if:

1. identity-preserved AUPRC exceeds identity-erased AUPRC on at least **4/5 networks**;
2. median paired AUPRC improvement is positive;
3. a network-level paired bootstrap 95% CI excludes zero when KO and KD comparisons
   are pooled as two preregistered modalities;
4. identity-preserved AUPRC/prevalence is > 1.0 on at least three networks;
5. no claim of a novel network-inference state of the art is made.

This gate tests boundary-dependent identifiability, **not** whether a simple knockout
estimator beats specialist DREAM4 inference algorithms.

## Gate 2 — cross-boundary replication

A structural edge supported by knockout evidence should tend to receive concordant
evidence under knockdown:

- Spearman correlation of directed edge scores;
- overlap of top-k edges;
- sign/effect consistency when meaningful.

This tests whether the relation survives a second intervention intensity.

## Gate 3 — held-out perturbation prediction

Optional stronger test:

- fit a relational response model using single knockouts / knockdowns;
- predict the official hidden dual-knockout responses;
- compare with a direction-specific regression baseline.

This asks whether cross-boundary relational structure improves out-of-sample
mechanism use, not merely edge ranking.

## Data

Preferred source:

- GNW DREAM4 challenge archive:
  `https://gnw.sourceforge.net/resources/DREAM4%20in%20silico%20challenge.zip`

The runner also accepts an already extracted challenge directory.

No generated replacement data should be used for the confirmatory run.

## Run

```bash
python run_dream4_gate.py --archive "/path/to/DREAM4 in silico challenge.zip" --out outputs
```

or:

```bash
python run_dream4_gate.py --root "/path/to/extracted/DREAM4" --out outputs
```

The script searches recursively for the official files.

## Important

Do **not** edit the estimator or acceptance criteria after seeing the five-network results.
If the simple estimator is poor, report that result. A later method-development set must be
separated from a fresh confirmatory benchmark.
