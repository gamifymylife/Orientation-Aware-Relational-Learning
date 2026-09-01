from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def run_sweep(kind: str, rates, seeds):
    rows = []
    for rate in rates:
        if kind == "false_merge":
            cfg = BenchmarkConfig(
                world_regime="equivalent_redundancy",
                n_mechanisms=12, n_orientations=32, n_equivalence_classes=8,
                n_interventions=12, budget=30,
                metadata_false_merge_rate=float(rate),
            )
        elif kind == "false_split":
            cfg = BenchmarkConfig(
                world_regime="equivalent_redundancy",
                n_mechanisms=12, n_orientations=24, n_equivalence_classes=4,
                n_interventions=12, budget=30,
                metadata_false_split_rate=float(rate),
            )
        elif kind == "admissibility_fp":
            cfg = BenchmarkConfig(
                world_regime="asymmetric_invalid",
                n_mechanisms=12, n_orientations=16, n_interventions=12,
                budget=30, invalid_orientation_fraction=0.25,
                admissibility_false_positive_rate=float(rate),
            )
        elif kind == "admissibility_fn":
            cfg = BenchmarkConfig(
                world_regime="standard",
                n_mechanisms=12, n_orientations=16, n_interventions=12,
                budget=30,
                admissibility_false_negative_rate=float(rate),
            )
        elif kind == "transport_noise":
            cfg = BenchmarkConfig(
                world_regime="equivalent_redundancy",
                n_mechanisms=12, n_orientations=24, n_equivalence_classes=4,
                n_interventions=12, budget=30,
                transport_metadata_noise=float(rate),
            )
        else:
            raise ValueError(kind)

        for seed in seeds:
            r = run_episode(cfg, int(seed), "structured_oarl")
            r["error_kind"] = kind
            r["error_rate"] = float(rate)
            rows.append(r)
    return pd.DataFrame(rows)


def summarize(df):
    return (
        df.groupby(["error_kind", "error_rate"], as_index=False)
        .agg(
            correct_rate=("correct_argmax", "mean"),
            success_rate=("success_95", "mean"),
            false_high_conf_rate=("false_high_confidence", "mean"),
            median_penalized_c95=("penalized_c95", "median"),
            mean_score_evals=("score_evals", "mean"),
            mean_declared_classes=("n_equivalence_classes", "mean"),
            mean_false_admissible_positive=("false_admissible_positive", "mean"),
            mean_false_admissible_negative=("false_admissible_negative", "mean"),
            mean_true_invalid_queries=("true_inadmissible_queries", "mean"),
        )
    )


def paired_bootstrap_diff(df, kind, rate, metric, B=5000, seed=123):
    sub = df[df.error_kind == kind]
    w = sub.pivot(index="seed", columns="error_rate", values=metric).dropna()
    d = (w[float(rate)] - w[0.0]).to_numpy(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(B, len(d)))
    vals = d[idx].mean(axis=1)
    lo, hi = np.quantile(vals, [0.025, 0.975])
    return float(d.mean()), float(lo), float(hi)


def main():
    # Full shape sweeps: 100 paired worlds per point.
    full = pd.concat([
        run_sweep("false_merge", [0, .125, .25, .375, .5], range(0, 100)),
        run_sweep("false_split", [0, .25, .5, .75, 1.0], range(1000, 1100)),
        run_sweep("admissibility_fp", [0, .25, .5, .75, 1.0], range(2000, 2100)),
        run_sweep("admissibility_fn", [0, .10, .25, .50, .75, .90], range(3000, 3100)),
        run_sweep("transport_noise", [0, .02, .05, .10, .20, .40], range(4000, 4100)),
    ], ignore_index=True)
    full.to_csv(OUT / "v04_structure_error_sweeps.csv", index=False)
    summary = summarize(full)
    summary.to_csv(OUT / "v04_structure_error_summary.csv", index=False)

    # 500-seed critical paired confirmations.
    critical = pd.concat([
        run_sweep("false_merge", [0, .125], range(10000, 10500)),
        run_sweep("admissibility_fp", [0, .25], range(20000, 20500)),
        run_sweep("admissibility_fn", [0, .25], range(30000, 30500)),
        run_sweep("transport_noise", [0, .02, .05], range(40000, 40500)),
        run_sweep("transport_noise", [0, .10, .20, .40], range(50000, 50500)),
    ], ignore_index=True)
    # Duplicate clean transport blocks use different seed ranges; retain them as
    # independent confirmations rather than pooling incompatible pairs.
    critical.to_csv(OUT / "v04_critical_500seed.csv", index=False)

    # Compute paired CIs for blocks with unique seed/rate matrices.
    rows = []
    block_specs = [
        ("false_merge", .125, range(10000, 10500)),
        ("admissibility_fp", .25, range(20000, 20500)),
        ("admissibility_fn", .25, range(30000, 30500)),
    ]
    for kind, rate, seeds in block_specs:
        sub = critical[(critical.error_kind == kind) & (critical.seed.isin(seeds))]
        for metric in ["correct_argmax", "success_95", "false_high_confidence"]:
            diff, lo, hi = paired_bootstrap_diff(sub, kind, rate, metric)
            rows.append({"error_kind": kind, "error_rate": rate, "metric": metric,
                         "paired_mean_diff": diff, "ci95_low": lo, "ci95_high": hi})

    # Transport blocks are separately paired by seed range.
    for rate in [.02, .05]:
        sub = critical[(critical.error_kind == "transport_noise") & (critical.seed.between(40000, 40499))]
        for metric in ["correct_argmax", "success_95", "false_high_confidence"]:
            diff, lo, hi = paired_bootstrap_diff(sub, "transport_noise", rate, metric)
            rows.append({"error_kind": "transport_noise", "error_rate": rate, "metric": metric,
                         "paired_mean_diff": diff, "ci95_low": lo, "ci95_high": hi})
    for rate in [.10, .20, .40]:
        sub = critical[(critical.error_kind == "transport_noise") & (critical.seed.between(50000, 50499))]
        for metric in ["correct_argmax", "success_95", "false_high_confidence"]:
            diff, lo, hi = paired_bootstrap_diff(sub, "transport_noise", rate, metric)
            rows.append({"error_kind": "transport_noise", "error_rate": rate, "metric": metric,
                         "paired_mean_diff": diff, "ci95_low": lo, "ci95_high": hi})
    ci = pd.DataFrame(rows)
    ci.to_csv(OUT / "v04_paired_bootstrap_ci.csv", index=False)

    # Headline values from 500-seed confirmations.
    def rate_mean(kind, rate, seeds, col):
        x = critical[(critical.error_kind == kind) & (critical.error_rate == rate) & critical.seed.isin(seeds)]
        return float(x[col].mean())

    headline = {
        "false_merge_1_of_8_correct_clean": rate_mean("false_merge", 0, range(10000,10500), "correct_argmax"),
        "false_merge_1_of_8_correct_corrupt": rate_mean("false_merge", .125, range(10000,10500), "correct_argmax"),
        "admissibility_one_invalid_reopened_correct_clean": rate_mean("admissibility_fp", 0, range(20000,20500), "correct_argmax"),
        "admissibility_one_invalid_reopened_correct_corrupt": rate_mean("admissibility_fp", .25, range(20000,20500), "correct_argmax"),
        "false_negative_25pct_correct_clean": rate_mean("admissibility_fn", 0, range(30000,30500), "correct_argmax"),
        "false_negative_25pct_correct_corrupt": rate_mean("admissibility_fn", .25, range(30000,30500), "correct_argmax"),
    }
    (OUT / "v04_headline.json").write_text(json.dumps(headline, indent=2))

    def html_table(frame):
        return frame.to_html(index=False, float_format=lambda x: f"{x:.4f}", border=0, classes="data")
    dashboard = f"""<!doctype html><html><head><meta charset='utf-8'><title>OARL v0.4 Structural Error Dashboard</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:1180px;margin:36px auto;padding:0 20px;color:#171717;line-height:1.45}}h1,h2{{line-height:1.15}}.kpi{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:20px 0}}.card{{border:1px solid #ddd;border-radius:10px;padding:16px}}.big{{font-size:2rem;font-weight:700}}table.data{{border-collapse:collapse;width:100%;font-size:12px}}table.data th,table.data td{{padding:6px;border-bottom:1px solid #eee;text-align:right}}table.data th:first-child,table.data td:first-child{{text-align:left}}.note{{background:#f5f5f5;padding:14px;border-radius:8px}}</style></head><body>
<h1>Orientation-Aware Benchmark v0.4</h1><p>How imperfect can structural classification be before quotienting or admissibility gating becomes unsafe?</p>
<div class='kpi'>
<div class='card'><div class='big'>-{100*(headline['false_merge_1_of_8_correct_clean']-headline['false_merge_1_of_8_correct_corrupt']):.1f} pp</div><div>correctness after one false merge among eight true classes</div></div>
<div class='card'><div class='big'>-{100*(headline['admissibility_one_invalid_reopened_correct_clean']-headline['admissibility_one_invalid_reopened_correct_corrupt']):.1f} pp</div><div>correctness after reopening one of four adversarial invalid orientations</div></div>
<div class='card'><div class='big'>{100*(headline['false_negative_25pct_correct_corrupt']-headline['false_negative_25pct_correct_clean']):+.1f} pp</div><div>correctness change after conservatively rejecting 25% of valid orientations</div></div>
</div>
<p class='note'><strong>Main design implication:</strong> false positive structural claims (false equivalence / false admissibility) are much more damaging than conservative false negatives. OARL classification should therefore be precision-first and allow abstention.</p>
<h2>100-seed shape sweeps</h2>{html_table(summary)}
<h2>500-seed paired bootstrap differences</h2>{html_table(ci)}
</body></html>"""
    (OUT / "v04_dashboard.html").write_text(dashboard)

    print(summary.to_string(index=False))
    print("\nHEADLINE\n", json.dumps(headline, indent=2))

if __name__ == "__main__":
    main()
