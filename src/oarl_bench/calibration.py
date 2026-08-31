from dataclasses import replace
import itertools
import numpy as np
import pandas as pd

from .config import BenchmarkConfig
from .runner import run_episode

DEFAULT_LAMBDAS = (0.0, 0.02, 0.05, 0.10, 0.20, 0.40)
DEFAULT_GAMMAS = (0.0, 0.01, 0.03, 0.05, 0.10)


def calibration_conditions():
    return [
        ("standard", 0.0),
        ("standard", 0.35),
        ("no_orientation_value", 0.0),
        ("informative_unstable", 0.35),
    ]


def calibrate(base_cfg: BenchmarkConfig, seeds, lambdas=DEFAULT_LAMBDAS, gammas=DEFAULT_GAMMAS):
    seeds = list(seeds)
    conditions = calibration_conditions()
    baseline_rows = []
    for regime, perturb in conditions:
        cfg = replace(base_cfg, world_regime=regime, perturbation_scale=perturb)
        for seed in seeds:
            baseline_rows.append(run_episode(cfg, seed, "generic_oed"))
    baseline = pd.DataFrame(baseline_rows)
    bkey = {(r.seed, r.regime, r.perturbation_scale): r for r in baseline.itertuples(index=False)}

    rows = []
    raw = []
    for lam, gam in itertools.product(lambdas, gammas):
        cand_rows = []
        for regime, perturb in conditions:
            cfg = replace(base_cfg, world_regime=regime, perturbation_scale=perturb, lambda_stability=float(lam), gamma_cost=float(gam))
            for seed in seeds:
                row = run_episode(cfg, seed, "full_oarl")
                cand_rows.append(row)
                raw.append(row)
        cand = pd.DataFrame(cand_rows)
        paired_reductions = []
        success_delta = []
        correct_delta = []
        for r in cand.itertuples(index=False):
            b = bkey[(r.seed, r.regime, r.perturbation_scale)]
            paired_reductions.append((b.penalized_c95 - r.penalized_c95) / b.penalized_c95)
            success_delta.append(r.success_95 - b.success_95)
            correct_delta.append(r.correct_argmax - b.correct_argmax)
        med_adv = float(np.median(paired_reductions))
        mean_adv = float(np.mean(paired_reductions))
        succ_d = float(np.mean(success_delta))
        corr_d = float(np.mean(correct_delta))
        feasible = (succ_d >= -0.02) and (corr_d >= -0.02)
        objective = med_adv if feasible else -1e9
        rows.append({
            "lambda_stability": lam,
            "gamma_cost": gam,
            "objective": objective,
            "feasible_reliability_gate": int(feasible),
            "median_paired_penalized_cost_reduction": med_adv,
            "mean_paired_penalized_cost_reduction": mean_adv,
            "success_delta_vs_generic": succ_d,
            "correct_delta_vs_generic": corr_d,
            "full_success_rate": float(cand.success_95.mean()),
            "full_correct_rate": float(cand.correct_argmax.mean()),
            "full_median_penalized_c95": float(cand.penalized_c95.median()),
        })
    table = pd.DataFrame(rows).sort_values(["objective", "median_paired_penalized_cost_reduction"], ascending=False).reset_index(drop=True)
    best = table.iloc[0].to_dict()
    return best, table, baseline, pd.DataFrame(raw)
