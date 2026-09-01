from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_grid
from oarl_bench.analysis import summarize, paired_cost_advantage, bootstrap_median_ci

def main():
    cfg = BenchmarkConfig(
        n_orientations=8,
        n_interventions=10,
        budget=35,
        ig_mode="proxy",
        lambda_stability=0.15,
        gamma_cost=0.05,
    )

    df = run_grid(
        cfg,
        seeds=range(8),
        mechanism_counts=[8, 16],
        noise_levels=[0.75, 1.5],
        perturbation_levels=[0.0, 0.35],
    )

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)

    df.to_csv(out_dir / "quick_results.csv", index=False)
    summary = summarize(df)
    summary.to_csv(out_dir / "quick_summary.csv", index=False)

    advantage = paired_cost_advantage(df)
    advantage.to_csv(out_dir / "quick_paired_advantage.csv", index=False)

    med, lo, hi = bootstrap_median_ci(
        advantage["relative_cost_reduction"], draws=2000
    )

    print(summary.to_string(index=False))
    print()
    print(
        "Full OARL median paired C95 reduction vs generic OED: "
        f"{med:.1%} [95% bootstrap CI {lo:.1%}, {hi:.1%}]"
    )

if __name__ == "__main__":
    main()
