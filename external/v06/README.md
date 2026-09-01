# v0.6 External Competitive Gate

This directory contains adapters and reproducibility material for the first OARL external competitive benchmark.

## Why this exists

The internal v0.5 programme established that exact and precision-first finite-noise equivalence certification can work in OARL's current synthetic affine/permutation family. That is not enough to establish a distinctive method advantage.

v0.6 asks whether the same discovery/certification idea survives on independently authored systems and whether it outperforms simpler alternatives at matched safety.

## Target order

1. **Microsoft CSuite** — primary third-party causal construction-family gate.
2. **DREAM4 Size100** — secondary replication/escalation gate using the already corrected OARL DREAM4 harness.
3. A later real or executable prospective system — required before any real-world generalization claim.

## Required adapter boundary

A third-party adapter must expose only the following benchmark-neutral objects to competing methods:

- system identifier;
- candidate view identifier;
- pilot/confirmatory split label;
- observations or predictive summaries available to all competitors;
- acquisition cost metadata if supplied or frozen by protocol.

Ground-truth mechanism, graph, SEM, and equivalence labels live behind the evaluator boundary and are unavailable to OARL and non-oracle baselines during discovery.

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

See `evidence/v06/PREREGISTRATION.md` for the frozen scientific gate.
