from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode

def test_episode_runs():
    cfg = BenchmarkConfig(
        n_mechanisms=6,
        n_orientations=5,
        n_interventions=4,
        budget=8,
    )
    row = run_episode(cfg, seed=1, policy="generic_oed")
    assert 1 <= row["n95"] <= cfg.budget + 1
    assert row["c95"] > 0
    assert row["score_evals"] > 0
