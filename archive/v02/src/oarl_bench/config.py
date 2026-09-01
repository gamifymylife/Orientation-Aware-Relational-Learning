from dataclasses import dataclass

VALID_REGIMES = {
    "standard",
    "no_orientation_value",
    "informative_unstable",
    "orientation_exclusive",
}

@dataclass(frozen=True)
class BenchmarkConfig:
    n_mechanisms: int = 12
    n_orientations: int = 10
    n_interventions: int = 12
    latent_dim: int = 4

    base_noise: float = 1.0
    exposure_scale: float = 2.0
    perturbation_scale: float = 0.0
    cost_spread: float = 0.6
    exposure_instability_correlation: float = 0.65
    world_regime: str = "standard"

    posterior_threshold: float = 0.95
    budget: int = 40

    lambda_stability: float = 0.15
    gamma_cost: float = 0.05

    # Failed 95%-identification is penalized in calibration/comparison rather
    # than being allowed to look artificially cheap.
    failure_penalty_budget_equivalents: float = 1.0

    ig_mode: str = "proxy"
    quadrature_points: int = 12

    def validate(self) -> None:
        if self.n_mechanisms < 2:
            raise ValueError("n_mechanisms must be >= 2")
        if self.n_orientations < 2:
            raise ValueError("n_orientations must be >= 2")
        if self.n_interventions < 1:
            raise ValueError("n_interventions must be >= 1")
        if self.base_noise <= 0:
            raise ValueError("base_noise must be > 0")
        if not (0.5 < self.posterior_threshold < 1.0):
            raise ValueError("posterior_threshold must be in (0.5, 1)")
        if self.ig_mode not in {"proxy", "quadrature"}:
            raise ValueError("ig_mode must be 'proxy' or 'quadrature'")
        if self.world_regime not in VALID_REGIMES:
            raise ValueError(f"world_regime must be one of {sorted(VALID_REGIMES)}")
        if self.lambda_stability < 0 or self.gamma_cost < 0:
            raise ValueError("lambda_stability and gamma_cost must be >= 0")
