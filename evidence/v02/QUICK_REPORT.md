# Quick Benchmark Report — v0.1

This is a smoke-test run, **not publication evidence**.

Configuration:

- 8 seeds per condition
- mechanism counts: 8, 16
- noise: 0.75, 1.5
- perturbation: 0.0, 0.35
- orientations: 8
- interventions: 10
- budget: 35

## Aggregate results

| policy             |   success_rate |   correct_rate |   median_n95 |   median_c95 |   mean_score_evals |   mean_runtime_s |
|:-------------------|---------------:|---------------:|-------------:|-------------:|-------------------:|-----------------:|
| fixed_oed          |         0.0000 |         0.0625 |      36.0000 |      31.2091 |           350.0000 |           0.0028 |
| full_oarl          |         0.1406 |         0.5312 |      36.0000 |      18.5779 |          2477.5000 |           0.0177 |
| generic_oed        |         0.7656 |         0.8438 |      13.5000 |      15.5145 |          1345.0000 |           0.0092 |
| oarl_no_stability  |         0.5938 |         0.8125 |      20.5000 |      12.6442 |          1655.0000 |           0.0116 |
| oracle             |         0.7969 |         0.9375 |      11.5000 |      12.3444 |          1265.0000 |           0.0130 |
| passive            |         0.0000 |         0.0625 |      36.0000 |      32.1408 |             0.0000 |           0.0005 |
| random_orientation |         0.3750 |         0.7656 |      36.0000 |      38.4886 |             0.0000 |           0.0005 |

## Critical paired comparison

Median paired C95 reduction of Full OARL vs Generic OED: **-13.6%**
Bootstrap 95% CI: **[-66.2%, 19.5%]**

Do not interpret this as validation. The quick run exists to prove the benchmark executes and to reveal
whether the default synthetic generator is obviously biased, broken, or incapable of differentiating policies.

The next scientifically meaningful run should use >=100 seeds, preregistered settings, exact/quadrature IG
on a confirmatory subset, negative controls, and domain-level external benchmarks.