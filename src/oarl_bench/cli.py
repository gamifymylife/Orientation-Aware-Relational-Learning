import argparse
from pathlib import Path
import pandas as pd

from .config import BenchmarkConfig
from .runner import run_grid, POLICIES
from .analysis import summarize, paired_cost_advantage, bootstrap_median_ci


def _run(args):
    cfg = BenchmarkConfig(
        n_orientations=args.orientations,
        n_interventions=args.interventions,
        budget=args.budget,
        ig_mode=args.ig_mode,
        lambda_stability=args.lambda_stability,
        gamma_cost=args.gamma_cost,
    )
    df = run_grid(
        cfg,
        seeds=range(args.seeds),
        mechanism_counts=args.mechanisms,
        noise_levels=args.noise,
        perturbation_levels=args.perturbation,
        policies=args.policies,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    summary_out = out.with_name(out.stem + "_summary.csv")
    summarize(df).to_csv(summary_out, index=False)
    advantage = paired_cost_advantage(df)
    adv_out = out.with_name(out.stem + "_paired_advantage.csv")
    advantage.to_csv(adv_out, index=False)
    med, lo, hi = bootstrap_median_ci(advantage["relative_cost_reduction"])
    print(f"Wrote {out}")
    print(f"Wrote {summary_out}")
    print(f"Wrote {adv_out}")
    print(f"Full OARL median paired C95 reduction vs generic OED: {med:.1%} [95% bootstrap CI {lo:.1%}, {hi:.1%}]")


def _summarize(args):
    df = pd.read_csv(args.path)
    print(summarize(df).to_string(index=False))
    advantage = paired_cost_advantage(df)
    med, lo, hi = bootstrap_median_ci(advantage["relative_cost_reduction"])
    print()
    print(f"Full OARL median paired C95 reduction vs generic OED: {med:.1%} [95% bootstrap CI {lo:.1%}, {hi:.1%}]")


def main():
    parser = argparse.ArgumentParser(prog="oarl-bench")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--seeds", type=int, default=100)
    p.add_argument("--mechanisms", type=int, nargs="+", default=[8, 16, 32])
    p.add_argument("--noise", type=float, nargs="+", default=[0.5, 1.0, 2.0])
    p.add_argument("--perturbation", type=float, nargs="+", default=[0.0, 0.35])
    p.add_argument("--orientations", type=int, default=12)
    p.add_argument("--interventions", type=int, default=16)
    p.add_argument("--budget", type=int, default=60)
    p.add_argument("--ig-mode", choices=["proxy", "quadrature"], default="proxy")
    p.add_argument("--lambda-stability", type=float, default=0.15)
    p.add_argument("--gamma-cost", type=float, default=0.05)
    p.add_argument("--policies", nargs="+", default=POLICIES)
    p.add_argument("--output", default="outputs/full_results.csv")
    p.set_defaults(func=_run)
    p = sub.add_parser("summarize")
    p.add_argument("path")
    p.set_defaults(func=_summarize)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
