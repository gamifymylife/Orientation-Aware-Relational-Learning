# Changelog

## v0.5B.1 — finite-noise structure certification — 2026-08-31

- Preserved the failed first v0.5B pilot, which false-merged a unique orientation pair at 500 predictive samples/cell.
- Added a separate post-pilot preregistration for a precision-first finite-noise equivalence certifier.
- Added independent fit/validation predictive splits, bidirectional intervention-map agreement, assignment-separation, affine stability/reciprocity, simultaneous response bounds and predictive-noise compatibility.
- Added explicit `EQUIVALENT / DISTINCT / UNKNOWN` abstention semantics; only `EQUIVALENT` can create a quotient merge.
- Added transport-accuracy evaluation against hidden benchmark truth after certification.
- Passed the frozen confirmatory gate: 72,600 distinct pair challenges, 0 false equivalences, precision 1.000, recall 0.2757, 829 accepted direct certificates, 0 mapping errors, 17.9% mean compression.
- Added `evidence/v05b/V05B_CONFIRMATORY_REPORT.md` and frozen machine-readable outputs.

## v0.5A — exact structure discovery — 2026-08-31

- Added exact orientation-equivalence and affine/permutation transport discovery from candidate likelihood geometry without reading hidden class labels.
- Verified zero false merges in the frozen exact synthetic gate and agreement with the oracle quotient.
- Added end-to-end runtime accounting showing that discovery overhead does not pay for cheap proxy scoring but can pay for expensive quadrature IG scoring.
- Preserved exact discovery evidence under `evidence/v05/`.

## Repository consolidation — 2026-08-31

- Promoted v0.4 benchmark code to the canonical live implementation.
- Preserved v0.1 and v0.2 code snapshots under `archive/`.
- Preserved frozen evidence for v0.1, v0.2, v0.3 and v0.4 under `evidence/`.
- Regenerated the missing v0.3 result artifacts from the frozen `run_v03.py`, including the quadrature scaling run.
- Added historical Meselson–Stahl and Luria–Delbrück replays.
- Preserved DREAM4 v0.1 unchanged and added a v0.2 harness correcting preregistration/runner mismatches.
- Added an explicit claims ledger, roadmap, provenance record and CI.

## v0.4

See `evidence/v04/V04_CLASSIFIER_ROBUSTNESS_REPORT.md`.
