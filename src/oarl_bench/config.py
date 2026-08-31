from dataclasses import dataclass

VALID_REGIMES = {
    "standard",
    "no_orientation_value",
    "informative_unstable",
    "orientation_exclusive",
    "equivalent_redundancy",
    "asymmetric_invalid",
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

    n_equivalence_classes: int = 4
    invalid_orientation_fraction: float = 0.25
    transform_scale_spread: float = 0.55
    transform_offset_scale: float = 1.0

    metadata_false_merge_rate: float = 0.0
    metadata_false_split_rate: float = 0.0
    admissibility_false_positive_rate: float = 0.0
    admissibility_false_negative_rate: float = 0.0
    transport_metadata_noise: float = 0.0

    posterior_threshold: float = 0.95
    budget: int = 40

    lambda_stability: float = 0.0
    gamma_cost: float = 0.0

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
        if self.n_equivalence_classes < 1:
            raise ValueError("n_equivalence_classes must be >= 1")
        if not (0.0 <= self.invalid_orientation_fraction < 1.0):
            raise ValueError("invalid_orientation_fraction must be in [0,1)")
        if self.transform_scale_spread < 0 or self.transform_offset_scale < 0:
            raise ValueError("transform scales must be >= 0")
        for name, value in [
            ("metadata_false_merge_rate", self.metadata_false_merge_rate),
            ("metadata_false_split_rate", self.metadata_false_split_rate),
            ("admissibility_false_positive_rate", self.admissibility_false_positive_rate),
            ("admissibility_false_negative_rate", self.admissibility_false_negative_rate),
        ]:
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be in [0,1]")
        if self.transport_metadata_noise < 0:
            raise ValueError("transport_metadata_noise must be >= 0")
