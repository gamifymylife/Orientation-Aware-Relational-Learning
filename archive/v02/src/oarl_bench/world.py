from dataclasses import dataclass
import numpy as np
from .config import BenchmarkConfig

@dataclass
class RelationalWorld:
    means: np.ndarray
    nominal_sigma: np.ndarray
    stability: np.ndarray
    cost: np.ndarray
    exposure: np.ndarray
    true_h: int
    perturbation_scale: float
    seed: int
    regime: str

    @property
    def n_mechanisms(self) -> int:
        return self.means.shape[0]

    @property
    def n_orientations(self) -> int:
        return self.means.shape[1]

    @property
    def n_interventions(self) -> int:
        return self.means.shape[2]

    def observe(self, orientation: int, intervention: int, rng: np.random.Generator) -> float:
        mu = self.means[self.true_h, orientation, intervention]
        sigma = self.nominal_sigma[orientation, intervention]
        if self.perturbation_scale > 0:
            mu = mu + rng.normal(
                0.0,
                self.perturbation_scale * self.stability[orientation] * sigma,
            )
        return float(rng.normal(mu, sigma))


def _base_components(cfg: BenchmarkConfig, rng: np.random.Generator):
    H, O, A, D = cfg.n_mechanisms, cfg.n_orientations, cfg.n_interventions, cfg.latent_dim
    mech = rng.normal(size=(H, D))
    mech -= mech.mean(axis=0, keepdims=True)
    mech /= mech.std(axis=0, keepdims=True) + 1e-9
    orient_vec = rng.normal(size=(O, D))
    orient_vec /= np.linalg.norm(orient_vec, axis=1, keepdims=True) + 1e-12
    intervention_vec = rng.normal(size=(A, D))
    intervention_vec /= np.linalg.norm(intervention_vec, axis=1, keepdims=True) + 1e-12
    baseline = rng.normal(0.0, 0.5, size=(O, A))
    return mech, orient_vec, intervention_vec, baseline


def _costs(cfg: BenchmarkConfig, rng: np.random.Generator, O: int, A: int):
    orientation_cost = rng.lognormal(mean=0.0, sigma=cfg.cost_spread, size=O)
    intervention_cost = rng.lognormal(mean=-0.2, sigma=0.35, size=A)
    cost = orientation_cost[:, None] * intervention_cost[None, :]
    return cost / np.median(cost)


def generate_world(cfg: BenchmarkConfig, seed: int) -> RelationalWorld:
    cfg.validate()
    rng = np.random.default_rng(seed)
    H, O, A = cfg.n_mechanisms, cfg.n_orientations, cfg.n_interventions
    mech, orient_vec, intervention_vec, baseline = _base_components(cfg, rng)

    raw_exposure = rng.beta(1.4, 1.4, size=O)
    raw_exposure[0] = 0.0
    exposure = cfg.exposure_scale * raw_exposure
    means = np.empty((H, O, A), dtype=float)

    for o in range(O):
        for a in range(A):
            probe = orient_vec[o] * (0.35 + 0.65 * np.abs(intervention_vec[a]))
            means[:, o, a] = baseline[o, a] + exposure[o] * (mech @ probe)

    exp_norm = exposure / (exposure.max() + 1e-12)
    independent = rng.lognormal(mean=-0.3, sigma=0.55, size=O)
    stability = (
        cfg.exposure_instability_correlation * (0.2 + 2.2 * exp_norm)
        + (1.0 - cfg.exposure_instability_correlation) * independent
    )
    stability = np.clip(stability, 0.05, None)
    nominal_sigma = np.full((O, A), cfg.base_noise, dtype=float)
    cost = _costs(cfg, rng, O, A)

    if cfg.world_regime == "standard":
        # Exact projection equivalence at default boundary.
        means[:, 0, :] = baseline[0, :][None, :]
        stability[0] = min(stability[0], 0.25)

    elif cfg.world_regime == "no_orientation_value":
        # Every orientation contains exactly the same likelihood geometry and
        # has the same cost/stability. Orientation itself adds no information.
        template = means[:, 1 if O > 1 else 0, :].copy()
        for o in range(O):
            means[:, o, :] = template
        exposure[:] = float(np.mean(exposure[1:])) if O > 1 else 1.0
        stability[:] = 1.0
        cost[:] = 1.0

    elif cfg.world_regime == "informative_unstable":
        # Default view is non-identifying. Orientation 1 is intentionally the
        # strongest nominal discriminator but is highly unstable. Remaining
        # orientations are weaker and safer. Under perturbation this is a
        # direct kill-test of whether K protects rather than merely suppresses.
        means[:, 0, :] = baseline[0, :][None, :]
        stability[0] = 0.2
        if O > 1:
            # amplify orientation 1 discrimination relative to the rest
            center = means[:, 1, :].mean(axis=0, keepdims=True)
            means[:, 1, :] = center + 3.5 * (means[:, 1, :] - center)
            exposure[1] = max(exposure.max(), cfg.exposure_scale * 2.5)
            stability[1] = 8.0
        if O > 2:
            stability[2:] = np.clip(stability[2:], 0.2, 1.4)

    elif cfg.world_regime == "orientation_exclusive":
        # The default boundary identifies only a coarse mechanism group:
        # adjacent mechanism pairs are exactly indistinguishable for every a.
        # Orientation 1 is guaranteed to separate members of each pair.
        groups = np.arange(H) // 2
        group_signal = rng.normal(size=(groups.max() + 1, A))
        means[:, 0, :] = group_signal[groups]
        exposure[0] = 0.5
        stability[0] = 0.3
        if O > 1:
            # Guaranteed within-pair separation across all interventions.
            pair_sign = np.where(np.arange(H) % 2 == 0, -1.0, 1.0)[:, None]
            group_base = rng.normal(0.0, 0.4, size=(groups.max() + 1, A))[groups]
            sep = (1.25 + 0.25 * np.arange(A)[None, :] / max(1, A - 1))
            means[:, 1, :] = group_base + pair_sign * sep
            exposure[1] = max(exposure[1], cfg.exposure_scale)
            stability[1] = min(stability[1], 0.8)

    true_h = int(rng.integers(H))
    return RelationalWorld(
        means=means,
        nominal_sigma=nominal_sigma,
        stability=stability,
        cost=cost,
        exposure=exposure,
        true_h=true_h,
        perturbation_scale=cfg.perturbation_scale,
        seed=seed,
        regime=cfg.world_regime,
    )
