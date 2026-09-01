from dataclasses import dataclass
import numpy as np
from .config import BenchmarkConfig

@dataclass
class RelationalWorld:
    means: np.ndarray              # [H, O, A], canonical aligned readout
    nominal_sigma: np.ndarray      # [O, A]
    stability: np.ndarray          # [O]
    cost: np.ndarray               # [O, A]
    exposure: np.ndarray           # [O]
    true_h: int
    perturbation_scale: float
    seed: int

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

        # Unmodelled orientation-conditioned perturbation.
        # This is zero in clean experiments. In robustness tests it produces
        # a misspecification whose magnitude grows with instability.
        if self.perturbation_scale > 0:
            mu = mu + rng.normal(
                0.0,
                self.perturbation_scale * self.stability[orientation] * sigma
            )

        return float(rng.normal(mu, sigma))


def generate_world(cfg: BenchmarkConfig, seed: int) -> RelationalWorld:
    """
    Generate a ground-truth synthetic relational mechanism family.

    Design constraints:
    - orientation 0 is deliberately non-discriminating;
    - alternative orientations have heterogeneous mechanism exposure;
    - interventions modulate how strongly latent mechanism differences appear;
    - informative orientations are often, but not always, less stable;
    - experiment costs vary independently enough to create real tradeoffs.
    """
    cfg.validate()
    rng = np.random.default_rng(seed)

    H, O, A, D = (
        cfg.n_mechanisms,
        cfg.n_orientations,
        cfg.n_interventions,
        cfg.latent_dim,
    )

    # Latent mechanism fingerprints.
    mech = rng.normal(size=(H, D))
    mech -= mech.mean(axis=0, keepdims=True)
    mech /= mech.std(axis=0, keepdims=True) + 1e-9

    # Orientation exposure: default orientation is exactly uninformative.
    raw_exposure = rng.beta(1.4, 1.4, size=O)
    raw_exposure[0] = 0.0
    exposure = cfg.exposure_scale * raw_exposure

    # Orientation-specific projections of latent mechanism differences.
    orient_vec = rng.normal(size=(O, D))
    orient_vec /= np.linalg.norm(orient_vec, axis=1, keepdims=True) + 1e-12

    # Intervention-specific latent probes.
    intervention_vec = rng.normal(size=(A, D))
    intervention_vec /= np.linalg.norm(intervention_vec, axis=1, keepdims=True) + 1e-12

    # Common baseline signal unrelated to hidden mechanism.
    baseline = rng.normal(0.0, 0.5, size=(O, A))

    means = np.empty((H, O, A), dtype=float)
    for o in range(O):
        for a in range(A):
            probe = orient_vec[o] * (0.35 + 0.65 * np.abs(intervention_vec[a]))
            discrim = mech @ probe
            means[:, o, a] = baseline[o, a] + exposure[o] * discrim

    # Enforce exact projection equivalence at the declared training orientation.
    means[:, 0, :] = baseline[0, :][None, :]

    # Stability is partly correlated with exposure, but has independent variation.
    exp_norm = exposure / (exposure.max() + 1e-12)
    independent = rng.lognormal(mean=-0.3, sigma=0.55, size=O)
    stability = (
        cfg.exposure_instability_correlation * (0.2 + 2.2 * exp_norm)
        + (1.0 - cfg.exposure_instability_correlation) * independent
    )
    stability = np.clip(stability, 0.05, None)
    stability[0] = min(stability[0], 0.25)

    # Nominal observation noise is known to all policies.
    nominal_sigma = np.full((O, A), cfg.base_noise, dtype=float)

    # Experimental cost varies by orientation and intervention.
    orientation_cost = rng.lognormal(mean=0.0, sigma=cfg.cost_spread, size=O)
    intervention_cost = rng.lognormal(mean=-0.2, sigma=0.35, size=A)
    cost = orientation_cost[:, None] * intervention_cost[None, :]
    cost = cost / np.median(cost)

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
    )
