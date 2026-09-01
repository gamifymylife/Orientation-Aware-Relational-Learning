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


def _ig_matrix(world: RelationalWorld, posterior: np.ndarray, cfg: BenchmarkConfig) -> np.ndarray:
    """Return IG for every (orientation, intervention).

    Proxy mode is fully vectorized because large calibration/confirmatory sweeps
    evaluate the same algebra thousands of times. Quadrature remains the exact
    slower confirmation path.
    """
    O, A = world.n_orientations, world.n_interventions
    if cfg.ig_mode == "proxy":
        m = np.tensordot(posterior, world.means, axes=(0, 0))  # [O,A]
        centered = world.means - m[None, :, :]
        var = np.tensordot(posterior, centered * centered, axes=(0, 0))
        return 0.5 * np.log1p(var / (world.nominal_sigma * world.nominal_sigma))

    out = np.empty((O, A), dtype=float)
    for o in range(O):
        for a in range(A):
            out[o, a] = _ig(world, posterior, o, a, cfg)
    return out


def _choice_from_scores(scores: np.ndarray) -> Choice:
    flat = int(np.argmax(scores))
    o, a = np.unravel_index(flat, scores.shape)
    return Choice(int(o), int(a), float(scores[o, a]), int(scores.size))


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

    if policy == "fixed_oed":
        ig = _ig_matrix(world, posterior, cfg)[0:1, :]
        c = _choice_from_scores(ig)
        return Choice(0, c.intervention, c.score, A)

    if policy in {"generic_oed", "oarl_no_stability", "full_oarl"}:
        ig = _ig_matrix(world, posterior, cfg)
        if policy == "generic_oed":
            scores = ig
        elif policy == "oarl_no_stability":
            scores = ig - cfg.gamma_cost * world.cost
        else:
            k_penalty = cfg.lambda_stability * np.log1p(world.stability)[:, None]
            scores = ig - k_penalty - cfg.gamma_cost * world.cost
        return _choice_from_scores(scores)

    if policy == "oracle":
        hstar = world.true_h
        mu_true = world.means[hstar]  # [O,A]
        sigma2 = world.nominal_sigma * world.nominal_sigma
        sq = (world.means - mu_true[None, :, :]) ** 2 / (2.0 * sigma2[None, :, :])
        alt_p = posterior.copy()
        alt_p[hstar] = 0.0
        if alt_p.sum() <= 1e-15:
            sep = np.zeros((O, A), dtype=float)
        else:
            alt_p /= alt_p.sum()
            sep = np.tensordot(alt_p, sq, axes=(0, 0))
        scores = (
            sep
            - cfg.lambda_stability * np.log1p(world.stability)[:, None]
            - cfg.gamma_cost * world.cost
        )
        return _choice_from_scores(scores)

    raise ValueError(f"Unknown policy: {policy}")
