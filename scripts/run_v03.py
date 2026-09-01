from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json
import numpy as np
import pandas as pd

from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def run_block(name: str, cfg: BenchmarkConfig, seeds, policies):
    rows = []
    for seed in seeds:
        for policy in policies:
            r = run_episode(cfg, int(seed), policy)
            r["block"] = name
            rows.append(r)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["block", "policy"], as_index=False)
        .agg(
            success_rate=("success_95", "mean"),
            correct_rate=("correct_argmax", "mean"),
            false_high_conf_rate=("false_high_confidence", "mean"),
            median_n95=("n95", "median"),
            median_penalized_c95=("penalized_c95", "median"),
            mean_score_evals=("score_evals", "mean"),
            median_runtime_s=("runtime_s", "median"),
            mean_inadmissible_queries=("inadmissible_queries", "mean"),
            mean_transported_updates=("transported_updates", "mean"),
        )
    )


def paired_reduction(df: pd.DataFrame, baseline: str, method: str, metric: str):
    w = df.pivot(index="seed", columns="policy", values=metric).dropna()
    a, b = w[baseline], w[method]
    denom = a.replace(0, np.nan)
    return ((a - b) / denom).dropna()


def main():
    blocks = []

    quotient_cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=12,
        n_orientations=24,
        n_equivalence_classes=4,
        n_interventions=12,
        budget=30,
        base_noise=1.0,
    )
    quotient = run_block(
        "quotient_exact",
        quotient_cfg,
        range(0, 100),
        ["generic_oed", "generic_cost_tiebreak", "structured_rep_oed", "structured_oarl"],
    )
    blocks.append(quotient)

    asym_cfg = BenchmarkConfig(
        world_regime="asymmetric_invalid",
        n_mechanisms=12,
        n_orientations=16,
        n_interventions=12,
        budget=30,
        base_noise=1.0,
        invalid_orientation_fraction=0.25,
    )
    asym = run_block(
        "asymmetry_gate",
        asym_cfg,
        range(1000, 1100),
        ["generic_oed", "generic_gated_oed", "generic_cost_tiebreak", "structured_oarl"],
    )
    blocks.append(asym)

    control_cfg = BenchmarkConfig(
        world_regime="standard",
        n_mechanisms=12,
        n_orientations=16,
        n_interventions=12,
        budget=30,
        base_noise=1.0,
    )
    control = run_block(
        "no_structure_control",
        control_cfg,
        range(2000, 2100),
        ["generic_cost_tiebreak", "structured_oarl"],
    )
    blocks.append(control)

    all_main = pd.concat(blocks, ignore_index=True)
    all_main.to_csv(OUT / "v03_confirmatory_results.csv", index=False)
    summary = summarize(all_main)
    summary.to_csv(OUT / "v03_confirmatory_summary.csv", index=False)

    # Proxy scaling: fixed four equivalence classes while raw orientations grow.
    scaling_rows = []
    for O in [8, 16, 32, 64, 128, 256]:
        cfg = BenchmarkConfig(
            world_regime="equivalent_redundancy",
            n_mechanisms=16,
            n_orientations=O,
            n_equivalence_classes=4,
            n_interventions=24,
            budget=12,
            base_noise=1.0,
        )
        d = run_block(
            f"scale_{O}", cfg, range(3000, 3020),
            ["generic_cost_tiebreak", "structured_oarl"],
        )
        d["scale_O"] = O
        scaling_rows.append(d)
    scaling = pd.concat(scaling_rows, ignore_index=True)
    scaling.to_csv(OUT / "v03_scaling_raw.csv", index=False)
    scaling_summary = (
        scaling.groupby(["scale_O", "policy"], as_index=False)
        .agg(
            mean_score_evals=("score_evals", "mean"),
            median_runtime_s=("runtime_s", "median"),
            success_rate=("success_95", "mean"),
            correct_rate=("correct_argmax", "mean"),
        )
    )
    scaling_summary.to_csv(OUT / "v03_scaling_summary.csv", index=False)

    # Expensive numerical MI scaling: fewer seeds because quadrature is slow.
    quad_rows = []
    for O in [16, 32, 64]:
        cfg = BenchmarkConfig(
            world_regime="equivalent_redundancy",
            n_mechanisms=12,
            n_orientations=O,
            n_equivalence_classes=4,
            n_interventions=10,
            budget=8,
            base_noise=1.0,
            ig_mode="quadrature",
            quadrature_points=12,
        )
        d = run_block(
            f"quadrature_{O}", cfg, range(4000, 4005),
            ["generic_cost_tiebreak", "structured_oarl"],
        )
        d["scale_O"] = O
        quad_rows.append(d)
    quad = pd.concat(quad_rows, ignore_index=True)
    quad.to_csv(OUT / "v03_quadrature_scaling_raw.csv", index=False)
    quad_summary = (
        quad.groupby(["scale_O", "policy"], as_index=False)
        .agg(
            mean_score_evals=("score_evals", "mean"),
            median_runtime_s=("runtime_s", "median"),
            correct_rate=("correct_argmax", "mean"),
        )
    )
    quad_summary.to_csv(OUT / "v03_quadrature_scaling_summary.csv", index=False)

    q_eval = paired_reduction(quotient, "generic_cost_tiebreak", "structured_oarl", "score_evals")
    q_cost = quotient.pivot(index="seed", columns="policy", values="penalized_c95")
    q_n95 = quotient.pivot(index="seed", columns="policy", values="n95")
    q_correct = quotient.pivot(index="seed", columns="policy", values="correct_argmax")

    headline = {
        "quotient_score_eval_reduction_median": float(q_eval.median()),
        "quotient_cost_identical_fraction": float((q_cost["generic_cost_tiebreak"] == q_cost["structured_oarl"]).mean()),
        "quotient_n95_identical_fraction": float((q_n95["generic_cost_tiebreak"] == q_n95["structured_oarl"]).mean()),
        "quotient_correct_identical_fraction": float((q_correct["generic_cost_tiebreak"] == q_correct["structured_oarl"]).mean()),
        "asymmetry_generic_correct": float(asym[asym.policy == "generic_oed"].correct_argmax.mean()),
        "asymmetry_structured_correct": float(asym[asym.policy == "structured_oarl"].correct_argmax.mean()),
        "asymmetry_generic_false_high_conf": float(asym[asym.policy == "generic_oed"].false_high_confidence.mean()),
        "asymmetry_structured_false_high_conf": float(asym[asym.policy == "structured_oarl"].false_high_confidence.mean()),
    }
    (OUT / "v03_headline.json").write_text(json.dumps(headline, indent=2))

    # Compact standalone dashboard, no external dependencies.
    def table_html(frame: pd.DataFrame) -> str:
        return frame.to_html(index=False, float_format=lambda x: f"{x:.4f}", border=0, classes="data")

    dashboard = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>OARL v0.3 Gate-2 Dashboard</title>
<style>
body{{font-family:system-ui,-apple-system,sans-serif;max-width:1180px;margin:36px auto;padding:0 20px;line-height:1.45;color:#171717}}
h1,h2{{line-height:1.15}} .kpi{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0}}
.card{{border:1px solid #ddd;border-radius:10px;padding:16px}} .big{{font-size:2rem;font-weight:700}}
table.data{{border-collapse:collapse;width:100%;font-size:13px}} table.data th,table.data td{{padding:7px;border-bottom:1px solid #e8e8e8;text-align:right}} table.data th:first-child,table.data td:first-child{{text-align:left}}
code{{background:#f4f4f4;padding:2px 5px;border-radius:4px}} .note{{background:#f5f5f5;padding:14px;border-radius:8px}}
</style></head><body>
<h1>Orientation-Aware Benchmark v0.3</h1>
<p>Gate-2 test: can relational orientation structure reduce search or prevent invalid interrogation beyond exhaustive generic OED?</p>
<div class='kpi'>
<div class='card'><div class='big'>{100*headline['quotient_score_eval_reduction_median']:.1f}%</div><div>median score-evaluation reduction under exact quotienting</div></div>
<div class='card'><div class='big'>{100*headline['quotient_correct_identical_fraction']:.0f}%</div><div>paired quotient worlds with identical final correctness</div></div>
<div class='card'><div class='big'>{100*headline['asymmetry_generic_correct']:.0f}%</div><div>unrestricted Generic OED correctness on invalid-orientation stress test</div></div>
<div class='card'><div class='big'>{100*headline['asymmetry_structured_correct']:.0f}%</div><div>structured OARL correctness with admissibility gate</div></div>
</div>
<h2>Confirmatory summary</h2>{table_html(summary)}
<h2>Proxy scaling</h2>{table_html(scaling_summary)}
<h2>Quadrature scaling</h2>{table_html(quad_summary)}
<p class='note'><strong>Interpretation:</strong> quotienting is a computational result, not a sample-efficiency result. On exact equivalence classes, structured OARL is required to preserve Generic OED's posterior/decisions while avoiding redundant acquisition scoring. The admissibility stress test separately evaluates whether relational structure can prevent semantically invalid reverse queries.</p>
</body></html>"""
    (OUT / "v03_dashboard.html").write_text(dashboard)

    print(summary.to_string(index=False))
    print("\nHEADLINE", json.dumps(headline, indent=2))


if __name__ == "__main__":
    main()
