from dataclasses import replace
from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oarl_bench.config import BenchmarkConfig
from oarl_bench.calibration import calibrate
from oarl_bench.runner import run_grid
from oarl_bench.analysis import summarize, paired_cost_advantage, bootstrap_median_ci


def write_dashboard(summary, comparison, calibration, frozen, path):
    style = """
    <style>
    body{font-family:system-ui,-apple-system,sans-serif;max-width:1280px;margin:40px auto;padding:0 24px;line-height:1.45}
    h1,h2{letter-spacing:-.02em} table{border-collapse:collapse;width:100%;font-size:13px;margin:18px 0 30px}
    th,td{border:1px solid #ddd;padding:7px 8px;text-align:right} th:first-child,td:first-child{text-align:left}
    th{background:#f4f4f4}.callout{padding:16px;border:1px solid #bbb;border-radius:8px;background:#fafafa}
    code{background:#f2f2f2;padding:2px 5px;border-radius:4px}
    </style>"""
    html = ["<html><head><meta charset='utf-8'><title>OARL v0.2 confirmatory dashboard</title>", style, "</head><body>"]
    html += ["<h1>Orientation-Aware Benchmark v0.2</h1>",
             f"<div class='callout'><b>Frozen parameters:</b> λ={frozen['lambda_stability']}, γ={frozen['gamma_cost']}. "
             "Selected only on calibration seeds; held-out seeds were disjoint.</div>",
             "<h2>Held-out summary</h2>", summary.to_html(index=False, float_format=lambda x: f"{x:.4f}"),
             "<h2>Full OARL vs Generic OED</h2>", comparison.to_html(index=False, float_format=lambda x: f"{x:.4f}"),
             "<h2>Calibration sweep (top 20)</h2>", calibration.head(20).to_html(index=False, float_format=lambda x: f"{x:.4f}"),
             "</body></html>"]
    path.write_text("".join(html), encoding="utf-8")


def main():
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)

    base = BenchmarkConfig(
        n_mechanisms=12,
        n_orientations=8,
        n_interventions=10,
        budget=35,
        base_noise=1.0,
        ig_mode="proxy",
        lambda_stability=0.15,
        gamma_cost=0.05,
    )

    # Calibration seeds are isolated from all confirmatory seeds.
    calibration_seeds = range(0, 24)
    best, calibration_table, calibration_baseline, calibration_raw = calibrate(
        base, calibration_seeds
    )
    frozen = {
        "lambda_stability": float(best["lambda_stability"]),
        "gamma_cost": float(best["gamma_cost"]),
        "calibration_seed_start": 0,
        "calibration_seed_end": 23,
        "calibration_objective": float(best["objective"]),
    }
    (out / "frozen_parameters.json").write_text(json.dumps(frozen, indent=2))
    calibration_table.to_csv(out / "calibration_sweep.csv", index=False)
    calibration_baseline.to_csv(out / "calibration_generic_baseline.csv", index=False)
    calibration_raw.to_csv(out / "calibration_full_oarl_raw.csv", index=False)

    frozen_cfg = replace(
        base,
        lambda_stability=frozen["lambda_stability"],
        gamma_cost=frozen["gamma_cost"],
    )

    # Five disjoint confirmatory blocks: 100 fresh seeds each.
    blocks = [
        ("standard_clean", "standard", 0.0, range(1000, 1100)),
        ("standard_misspecified", "standard", 0.35, range(2000, 2100)),
        ("no_orientation_value", "no_orientation_value", 0.0, range(3000, 3100)),
        ("informative_unstable", "informative_unstable", 0.35, range(4000, 4100)),
        ("orientation_exclusive", "orientation_exclusive", 0.0, range(5000, 5100)),
    ]

    heldout_frames = []
    for label, regime, perturb, seeds in blocks:
        cfg = replace(frozen_cfg, world_regime=regime, perturbation_scale=perturb)
        df = run_grid(
            cfg,
            seeds=seeds,
            mechanism_counts=[cfg.n_mechanisms],
            noise_levels=[cfg.base_noise],
            perturbation_levels=[perturb],
            regimes=[regime],
        )
        df["condition"] = label
        heldout_frames.append(df)
    heldout = pd.concat(heldout_frames, ignore_index=True)
    heldout.to_csv(out / "heldout_results.csv", index=False)

    summary = (
        heldout.groupby(["condition", "policy"], dropna=False)
        .agg(
            runs=("seed", "count"),
            success_rate=("success_95", "mean"),
            correct_rate=("correct_argmax", "mean"),
            median_n95=("n95", "median"),
            median_c95=("c95", "median"),
            median_penalized_c95=("penalized_c95", "median"),
            mean_score_evals=("score_evals", "mean"),
            mean_runtime_s=("runtime_s", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(out / "heldout_summary.csv", index=False)

    comps = []
    for condition, sub in heldout.groupby("condition"):
        adv = paired_cost_advantage(sub, metric="penalized_c95")
        med, lo, hi = bootstrap_median_ci(adv.relative_cost_reduction, draws=5000, seed=17)
        comps.append({
            "condition": condition,
            "n_pairs": len(adv),
            "median_penalized_c95_reduction": med,
            "bootstrap_lo": lo,
            "bootstrap_hi": hi,
            "fraction_full_oarl_cheaper": float((adv.relative_cost_reduction > 0).mean()),
        })
    comparison = pd.DataFrame(comps)
    comparison.to_csv(out / "heldout_full_vs_generic.csv", index=False)

    # Aggregate across all held-out conditions.
    adv_all = paired_cost_advantage(heldout, metric="penalized_c95")
    med, lo, hi = bootstrap_median_ci(adv_all.relative_cost_reduction, draws=10000, seed=23)
    aggregate = {
        "heldout_pairs": int(len(adv_all)),
        "median_penalized_c95_reduction": med,
        "bootstrap_95_lo": lo,
        "bootstrap_95_hi": hi,
        "fraction_full_oarl_cheaper": float((adv_all.relative_cost_reduction > 0).mean()),
    }
    (out / "heldout_aggregate.json").write_text(json.dumps(aggregate, indent=2))

    write_dashboard(summary, comparison, calibration_table, frozen, out / "v02_dashboard.html")

    print("FROZEN", json.dumps(frozen))
    print("\nHELD-OUT COMPARISON")
    print(comparison.to_string(index=False))
    print("\nAGGREGATE", json.dumps(aggregate))

if __name__ == "__main__":
    main()
