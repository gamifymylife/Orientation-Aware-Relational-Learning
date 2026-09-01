from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode


def test_full_equals_generic_when_penalties_zero_with_common_random_numbers():
    cfg = BenchmarkConfig(
        n_mechanisms=8,
        n_orientations=6,
        n_interventions=5,
        budget=12,
        lambda_stability=0.0,
        gamma_cost=0.0,
    )
    a = run_episode(cfg, seed=42, policy="generic_oed")
    b = run_episode(cfg, seed=42, policy="full_oarl")
    for key in ["success_95", "correct_argmax", "n95", "total_cost", "penalized_c95", "posterior_true"]:
        assert a[key] == b[key]
