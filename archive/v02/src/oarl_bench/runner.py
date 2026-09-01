from dataclasses import replace
import time
from typing import Iterable
import numpy as np
import pandas as pd

from .config import BenchmarkConfig
from .world import generate_world
from .inference import update_posterior
from .policies import choose_experiment

POLICIES = [
    "passive",
    "fixed_oed",
    "random_orientation",
    "generic_oed",
    "oarl_no_stability",
    "full_oarl",
    "oracle",
]

def run_episode(cfg: BenchmarkConfig, seed: int, policy: str) -> dict:
    world = generate_world(cfg, seed)
    # Common random numbers: observation noise is shared across policies.
    # Policy randomness remains separate so random baselines are still random.
    obs_rng = np.random.default_rng(seed * 10007 + 12345)
    policy_rng = np.random.default_rng(seed * 10007 + sum(map(ord, policy)))
    posterior = np.full(world.n_mechanisms, 1.0 / world.n_mechanisms)

    cumulative_cost = 0.0
    score_evals = 0
    orientation_switches = 0
    prev_o = None
    t0 = time.perf_counter()
    reached = False
    step = 0

    for step in range(1, cfg.budget + 1):
        choice = choose_experiment(policy, world, posterior, cfg, policy_rng)
        score_evals += choice.score_evals
        if prev_o is not None and choice.orientation != prev_o:
            orientation_switches += 1
        prev_o = choice.orientation

        y = world.observe(choice.orientation, choice.intervention, obs_rng)
        posterior = update_posterior(
            posterior,
            world.means[:, choice.orientation, choice.intervention],
            float(world.nominal_sigma[choice.orientation, choice.intervention]),
            y,
        )
        cumulative_cost += float(world.cost[choice.orientation, choice.intervention])
        if posterior[world.true_h] >= cfg.posterior_threshold:
            reached = True
            break

    elapsed = time.perf_counter() - t0
    predicted_h = int(np.argmax(posterior))
    median_unit_cost = float(np.median(world.cost))
    failure_penalty = cfg.failure_penalty_budget_equivalents * cfg.budget * median_unit_cost
    penalized_c95 = cumulative_cost if reached else cumulative_cost + failure_penalty

    return {
        "seed": seed,
        "policy": policy,
        "regime": cfg.world_regime,
        "n_mechanisms": cfg.n_mechanisms,
        "n_orientations": cfg.n_orientations,
        "n_interventions": cfg.n_interventions,
        "base_noise": cfg.base_noise,
        "perturbation_scale": cfg.perturbation_scale,
        "lambda_stability": cfg.lambda_stability,
        "gamma_cost": cfg.gamma_cost,
        "ig_mode": cfg.ig_mode,
        "budget": cfg.budget,
        "success_95": int(reached),
        "correct_argmax": int(predicted_h == world.true_h),
        "n95": step if reached else cfg.budget + 1,
        "c95": cumulative_cost if reached else np.nan,
        "total_cost": cumulative_cost,
        "penalized_c95": penalized_c95,
        "posterior_true": float(posterior[world.true_h]),
        "score_evals": int(score_evals),
        "orientation_switches": int(orientation_switches),
        "runtime_s": float(elapsed),
        "true_h": int(world.true_h),
    }

def run_grid(
    base_cfg: BenchmarkConfig,
    seeds: Iterable[int],
    mechanism_counts: Iterable[int],
    noise_levels: Iterable[float],
    perturbation_levels: Iterable[float] = (0.0,),
    regimes: Iterable[str] | None = None,
    policies: Iterable[str] = POLICIES,
) -> pd.DataFrame:
    rows = []
    regimes = list(regimes) if regimes is not None else [base_cfg.world_regime]
    for regime in regimes:
        for h in mechanism_counts:
            for noise in noise_levels:
                for perturb in perturbation_levels:
                    cfg = replace(
                        base_cfg,
                        world_regime=str(regime),
                        n_mechanisms=int(h),
                        base_noise=float(noise),
                        perturbation_scale=float(perturb),
                    )
                    for seed in seeds:
                        for policy in policies:
                            rows.append(run_episode(cfg, int(seed), policy))
    return pd.DataFrame(rows)
