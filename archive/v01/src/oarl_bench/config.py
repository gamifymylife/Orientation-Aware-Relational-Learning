from dataclasses import dataclass

@dataclass(frozen=True)
class BenchmarkConfig:
    n_mechanisms: int = 12
    n_orientations: int = 10
    n_interventions: int = 12
    latent_dim: int = 4

    base_noise: float = 1.0
    exposure_scale: float = 2.0

    # Larger values make the actually observed system deviate from the nominal
    # likelihood more strongly at unstable orientations.
    perturbation_scale: float = 0.0

    # Experimental cost heterogeneity.
    cost_spread: float = 0.6

    # Strength of correlation between discriminatory exposure and instability.
    # Positive values create informative-but-risky orientations.
    exposure_instability_correlation: float = 0.65

    posterior_threshold: float = 0.95
    budget: int = 40

    lambda_stability: float = 0.15
    gamma_cost: float = 0.05

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
