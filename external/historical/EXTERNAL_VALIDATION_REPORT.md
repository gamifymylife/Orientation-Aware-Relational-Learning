# OARL External Historical Validation v0.1

## Executive result

Two famous mechanism-discrimination experiments that predate OARL were replayed as boundary-selection problems.

| Case | Coarse boundary | Alternate boundary | Result |
|---|---|---|---|
| Meselson–Stahl (1958) | mean DNA density | full density-band distribution | **PASS** |
| Luria–Delbrück (1943) | aggregate/mean mutant count | preserve independent-culture distribution | **PASS** |

The narrow external claim supported is:

> **Mechanism identifiability can be boundary-dependent.**

This does not establish that the full OARL software stack beats generic optimal experimental design on a third-party executable benchmark.

## Meselson–Stahl

Candidate mechanisms were conservative, semiconservative and dispersive DNA replication.

After `n` generations in light nitrogen, all three mechanisms have the same expected mean heavy-isotope fraction:

`2^-n`.

A readout that collapses the sample to mean density therefore contains **0 bits** of mechanism information in the deterministic replay.

The full density-band distribution differs. Generation 1 removes conservative replication; generation 2 separates semiconservative from dispersive. With equal prior probability over the three mechanisms, the generation-2 full-band observation carries `log2(3) = 1.585` bits in the deterministic abstraction.

**External Gate 1: PASS.**

## Luria–Delbrück

Candidate mechanisms were induced resistance after exposure versus spontaneous mutation before exposure.

The key discriminator is not the first moment alone but the fluctuation across independently grown cultures. Historical summary values used in the replay were:

- independent cultures: mean 11.3, variance 694;
- bulk-culture aliquots: mean 16.7, variance 15.

The variance/mean ratio is therefore about **61.4** for independent cultures versus **0.90** for bulk aliquots. Preserving culture identity exposes the jackpot structure predicted by spontaneous pre-selection mutation; aggregation suppresses it.

**External Gate 1: PASS.**

## Why these cases matter

Neither experimental system, candidate mechanism set nor decisive observation was created for this project. The two cases lose information in different ways:

- Meselson–Stahl: distribution -> mean;
- Luria–Delbrück: independent lineage histories -> aggregate count.

Both instantiate the same structural pattern:

`coarse boundary / aggregation -> observational equivalence`

`structure-preserving boundary -> mechanism distinction`.

## What remains open

Still not externally validated:

- automatic recovery of orientation equivalence classes;
- certified approximate quotienting on real measurements;
- search-compute reduction versus generic OED on a third-party executable benchmark;
- prospective selection of a previously unknown decisive experiment.

The next executable gate is DREAM4.
