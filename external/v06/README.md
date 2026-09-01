# v0.6 External Competitive Gate

This directory contains adapters and reproducibility material for the first OARL external competitive benchmark.

## Why this exists

The internal v0.5 programme established that exact and precision-first finite-noise equivalence certification can work in OARL's current synthetic affine/permutation family. That is not enough to establish a distinctive method advantage.

v0.6 asks whether the same discovery/certification idea survives on independently authored systems and whether it outperforms simpler alternatives at matched safety.

## Target order

1. **Microsoft CSuite** — primary third-party causal construction-family gate.
2. **DREAM4 Size100** — secondary replication/escalation gate using the already corrected OARL DREAM4 harness.
3. A later real or executable prospective system — required before any real-world generalization claim.

## Important CSuite limitation

CSuite supplies independently authored SEMs, true causal graphs, observational samples and interventional environments, but it was **not designed as an orientation-equivalence benchmark** and does not publish OARL-style equivalence classes.

Therefore v0.6 must not manufacture external ground truth by thresholding the same similarity score used by OARL. The adapter instead makes a deterministic 50/50 split inside each published interventional environment:

- **discovery half** — available to OARL and every non-oracle competitor;
- **holdout evaluator half** — unavailable during discovery and used only to measure whether proposed transports preserve the independently generated intervention-response structure.

The current pilot outputs continuous holdout transport scores. It does **not** turn them into confirmatory equivalence labels. Any hard tolerance must be frozen after the named pilot systems and before disjoint confirmatory systems are touched.

## Pilot subset

The adapter-development pilot is frozen to:

- `lingauss`;
- `nonlin_simpson`;
- `cat_chain`.

Pilot results may diagnose adapter errors and calibrate a later v0.6.1 protocol. They are never counted as confirmatory evidence.

The remaining CSuite systems are reserved until that protocol is frozen.

## Adapter boundary

`src/oarl_bench/csuite.py` loads the upstream `interventions.json` files and exposes only benchmark-neutral evidence to competing methods:

- system identifier;
- candidate view identifier;
- discovery-half primary and reference samples;
- intervention-minus-reference response signature in CSuite's published node coordinates;
- uncertainty estimate.

The neutral adapter deliberately does **not** standardize each response coordinate by split- or view-specific variance. The first CI fixture exposed that such independent coordinate-wise scaling can destroy a genuine global affine relation. Any competitor-level normalization must therefore be explicit, frozen and applied by that competitor rather than silently built into the shared evidence representation.

The holdout arrays and upstream intervention/effect/conditioning metadata remain evaluator-side. Ground-truth graph/SEM information is never supplied to OARL or non-oracle baselines during discovery.

The row split is derived from a SHA-256 hash of the stable `system:environment` identifier so repeated runs select exactly the same discovery and holdout rows without storing a tunable random seed.

## Pilot execution

```bash
python scripts/run_v06_csuite_pilot.py --out evidence/v06/pilot_outputs
```

The runner downloads the pinned CSuite v0.1 `interventions.json` artifacts for the pilot subset, records SHA-256 hashes, runs the neutral exact-duplicate and similarity baselines, and writes evaluator-only pair transport scores.

GitHub Actions workflow:

```text
.github/workflows/v06-csuite-pilot.yml
```

The workflow uploads the pilot outputs as an artifact. It does not commit pilot output into the scientific evidence directory automatically.

## Reproducibility manifest

Before confirmatory execution, add a machine-readable manifest recording:

- upstream repository / dataset citation;
- exact upstream version, tag, or commit where available;
- hashes for downloaded benchmark artifacts;
- adapter version;
- pilot system IDs;
- confirmatory system IDs;
- frozen baseline parameters;
- frozen OARL parameters;
- environment / dependency lock information.

No confirmatory output should be interpreted without this manifest.

## Baseline matrix

| Method | Learns equivalence? | Can abstain? | Uses hidden ground truth? |
|---|---:|---:|---:|
| Generic OED | no | n/a | no |
| Oracle quotient | no; supplied | no | yes |
| Exact canonicalization | yes, trivial identity only | effectively yes | no |
| Generic similarity clustering | yes | optional/frozen | no |
| Symmetry/canonical transform | uses declared transform family | yes | no |
| Behavioral equivalence | yes | yes | no |
| Forced binary comparator | yes | no | no |
| OARL precision-first | yes | **yes** | no |

## Non-negotiable reporting rule

Compression is never reported alone. Every compression result must be paired with false-merge risk and downstream mechanism-discrimination preservation.

A method that compresses more by erasing a genuine distinction has failed the purpose of the benchmark.

See `evidence/v06/PREREGISTRATION.md` for the scientific gate.
