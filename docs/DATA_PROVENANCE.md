# Data and Artifact Provenance

## Uploaded benchmark archives

The repository consolidation was assembled on 2026-08-31 from the supplied archives:

- `orientation-aware-benchmark-v0.1 (1).zip`
- `orientation-aware-benchmark-v0.2 (1)(1).zip`
- `orientation-aware-benchmark-v0.4(1).zip`
- `OARL_DREAM4_External_Gate_v0_1(1).zip`

A second supplied DREAM4 ZIP was byte-identical and was not duplicated.

## Historical external artifacts

The Meselson–Stahl and Luria–Delbrück replay report, CSVs and dashboard were recovered from the project artifact library and placed under `external/historical/`. They are historical abstractions of published experiments, not newly collected biological measurements.

## v0.3 regeneration

The v0.4 archive contained `scripts/run_v03.py` and `V03_GATE2_REPORT.md` but omitted the v0.3 output artifacts. During consolidation:

- the 100-seed confirmatory blocks and proxy scaling were rerun from the frozen script;
- the expensive quadrature scaling was rerun using parallel execution of the same independent episode calls, without changing configuration, seeds, policies or estimator;
- generated v0.3 CSV/JSON/dashboard artifacts were frozen under `evidence/v03/outputs/`.

The reproduced headline is an 83.333% median score-evaluation reduction in the 24→4 quotient with 100% paired equality for correctness, `N95` and penalized `C95`.

## DREAM4 status

`external/dream4/v01/` preserves the original uploaded apparatus unchanged. `v02/` corrects executable mismatches with the written preregistration; it does not contain or claim an official Size100 result. Official DREAM4 data are not vendored into this repository.

## v0.6.5 pyGSTi analytic audit

v0.6.5 contains no uploaded or separately collected dataset. The 256 held-out depth-8 circuits are exhaustively generated from the public `Gxpi2/Gypi2` gate alphabet in pyGSTi 0.10.2's `smq1Q_XYI` model pack.

The authoritative Fisher evaluator is derived analytically from the public ideal gate semantics using integer `SO(3)` orientation transport. Independently generated pyGSTi central finite differences at steps `1e-3`, `1e-4` and `1e-5` are numerical cross-checks, not evaluator truth. Ordinary/complement view labels share one physical binary observation by construction.

## v0.6.6 external mutation matrices

v0.6.6 uses test-by-mutant kill matrices from `donghwan-shin/Diversity-aware-Mutation-Testing`, pinned at source commit `f8d8376e0efe345161f26ff6483a404c8548fe1c` under its MIT license.

Four preregistered CSV matrices were losslessly projected into compressed NPZ files containing only test type, test identifier, mutant identifier and binary kill outcome. `external/mutation/v066/manifest.json` records the source paths, source SHA-256 checksums, compact checksums, dimensions and byte sizes. The compact artifacts load with `allow_pickle=False`.

`Chart-1` was the only outcome matrix inspected during development. The confirmatory matrices were Closure-118, Lang-33, Math-22 and Time-6. Before apparatus freeze, only their filenames, headers, row counts and byte sizes were inspected. Their kill outcomes were read only after preregistration commit `e1dda2c`.
