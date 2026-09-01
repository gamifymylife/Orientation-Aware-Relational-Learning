from dataclasses import dataclass
import numpy as np
from .inference import information_gain
from .config import BenchmarkConfig
from .world import RelationalWorld

@dataclass
class Choice:
    orientation: int
    intervention: int
    score: float
    score_evals: int

def _ig(world, posterior, o, a, cfg):
    return information_gain(
        posterior,
        world.means[:, o, a],
        float(world.nominal_sigma[o, a]),
        mode=cfg.ig_mode,
        quadrature_points=cfg.quadrature_points,
    )

def choose_experiment(
    policy: str,
    world: RelationalWorld,
    posterior: np.ndarray,
    cfg: BenchmarkConfig,
    rng: np.random.Generator,
) -> Choice:
    O, A = world.n_orientations, world.n_interventions

    if policy == "passive":
        return Choice(0, int(rng.integers(A)), 0.0, 0)

    if policy == "random_orientation":
        return Choice(int(rng.integers(O)), int(rng.integers(A)), 0.0, 0)

    candidates = []

    if policy == "fixed_oed":
        for a in range(A):
            ig = _ig(world, posterior, 0, a, cfg)
            candidates.append((ig, 0, a))
        score, o, a = max(candidates, key=lambda x: x[0])
        return Choice(o, a, float(score), len(candidates))

    if policy == "generic_oed":
        for o in range(O):
            for a in range(A):
                ig = _ig(world, posterior, o, a, cfg)
                candidates.append((ig, o, a))
        score, o, a = max(candidates, key=lambda x: x[0])
        return Choice(o, a, float(score), len(candidates))

    if policy == "oarl_no_stability":
        for o in range(O):
            for a in range(A):
                ig = _ig(world, posterior, o, a, cfg)
                score = ig - cfg.gamma_cost * float(world.cost[o, a])
                candidates.append((score, o, a))
        score, o, a = max(candidates, key=lambda x: x[0])
        return Choice(o, a, float(score), len(candidates))

    if policy == "full_oarl":
        for o in range(O):
            k_penalty = cfg.lambda_stability * np.log1p(world.stability[o])
            for a in range(A):
                ig = _ig(world, posterior, o, a, cfg)
                score = (
                    ig
                    - k_penalty
                    - cfg.gamma_cost * float(world.cost[o, a])
                )
                candidates.append((score, o, a))
        score, o, a = max(candidates, key=lambda x: x[0])
        return Choice(o, a, float(score), len(candidates))

    if policy == "oracle":
        # Oracle knows H*. Score the expected log-likelihood separation
        # between the true mechanism and posterior-weighted alternatives.
        hstar = world.true_h
        for o in range(O):
            for a in range(A):
                mu_true = world.means[hstar, o, a]
                sigma = float(world.nominal_sigma[o, a])
                sq = (world.means[:, o, a] - mu_true) ** 2 / (2.0 * sigma * sigma)
                mask = np.ones(world.n_mechanisms, dtype=bool)
                mask[hstar] = False
                alt_p = posterior[mask]
                if alt_p.sum() <= 1e-15:
                    sep = 0.0
                else:
                    alt_p = alt_p / alt_p.sum()
                    sep = float(np.sum(alt_p * sq[mask]))
                score = (
                    sep
                    - cfg.lambda_stability * np.log1p(world.stability[o])
                    - cfg.gamma_cost * float(world.cost[o, a])
                )
                candidates.append((score, o, a))
        score, o, a = max(candidates, key=lambda x: x[0])
        return Choice(o, a, float(score), len(candidates))

    raise ValueError(f"Unknown policy: {policy}")
