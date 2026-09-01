# OARL External Historical Validation v0.1

## Executive result

Two famous mechanism-discrimination experiments that predate OARL were replayed as boundary-selection problems.

| Case | Fixed/coarse boundary | Alternate boundary | Result |
|---|---|---|---|
| Meselson–Stahl (1958) | mean DNA density | full density-band distribution | **PASS** |
| Luria–Delbrück (1943) | mean mutant count / pooled view | preserve independent-culture distribution | **PASS** |

The narrow external claim supported is:

> **Mechanism identifiability can be boundary-dependent.**

This does not yet establish that the full OARL software stack beats generic optimal experimental design on a third-party benchmark.

---

## 1. Meselson–Stahl

Candidate mechanisms:

- conservative
- semiconservative
- dispersive

For all three, after `n` generations in light nitrogen the *mean* remaining heavy-isotope fraction is:

`2^-n`

Therefore a readout that compresses the sample to mean density has **0 bits of mechanism information** at generations 1, 2 and 3.

The full density distribution is different:

- generation 1: conservative predicts heavy+light bands; semiconservative and dispersive predict one intermediate band.
- generation 2:
  - conservative: heavy + light
  - semiconservative: hybrid + light
  - dispersive: one shifted intermediate band

With equal prior probability over the three historical hypotheses, generation-2 full-band observation has:

`I(H;Y) = log2(3) = 1.584963 bits`

Historical replay:

`['conservative', 'semiconservative', 'dispersive'] -> ['semiconservative', 'dispersive'] -> ['semiconservative']`

The observed single intermediate band after one generation removes conservative replication. The observed hybrid+light two-band pattern after the next generation uniquely retains semiconservative replication.

**Gate 1: PASS.**

---

## 2. Luria–Delbrück

Candidate mechanisms:

- induced resistance after exposure
- spontaneous mutation before exposure

The first moment alone is not the key discriminator. The competing models can be adjusted to similar average resistant counts.

The decisive boundary is whether culture identities are preserved.

Historical summary:

- independent cultures: mean `11.3`, variance `694.0`
- bulk-culture aliquots: mean `16.7`, variance `15.0`

Variance/mean:

- independent cultures: `61.42`
- bulk aliquots: `0.90`

Under the induced/Poisson-like prediction, variance should be of the same order as the mean.
Spontaneous pre-selection mutations create inherited clones and "jackpots", yielding variance far above the mean.

For a two-hypothesis deterministic discrimination abstraction:

- mean-only boundary: `0 bits`
- distribution-preserving independent-culture boundary: `1 bit`

As a simple diagnostic against the Poisson-like induced prediction, with 20 cultures the observed variance gives an approximate chi-square upper-tail probability:

`p ≈ 1.125e-235`

This p-value is **not** a substitute for the exact Luria–Delbrück likelihood; it is only a transparent measure of how incompatible the observed variance is with a Poisson-like fluctuation model.

**Gate 1: PASS.**

---

## 3. Why these are meaningful external cases

Neither experimental system, mechanism set, nor decisive observation was created for this project.

Both show the same structural failure mode:

`coarse boundary / aggregation -> observational equivalence`

`preserve the relevant relational structure -> mechanism distinction`

The two cases differ materially:

- Meselson–Stahl loses information by collapsing a **distribution of molecular densities to its mean**.
- Luria–Delbrück loses information by collapsing **separate lineage/culture histories into an aggregate count**.

This is stronger evidence for the generality of boundary-dependent identifiability than another internally generated affine benchmark.

---

## 4. What remains open

Still not externally validated:

- automatic discovery of the correct orientation equivalence classes;
- certified approximate quotienting on real measurements;
- search-compute reduction vs generic OED on a third-party executable benchmark;
- prospective selection of a previously unknown decisive experiment.

Next escalation:

1. DREAM4 perturbational gene networks.
2. CausalBench Perturb-seq.
3. Prospective/blinded mechanism-discrimination task.
