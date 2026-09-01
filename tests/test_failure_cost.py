import numpy as np
from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode


def test_failure_penalized_cost_is_not_less_than_raw_total_cost():
    cfg = BenchmarkConfig(
        n_mechanisms=20,
        n_orientations=4,
        n_interventions=2,
        budget=1,
        world_regime="standard",
    )
    row = run_episode(cfg, seed=99, policy="passive")
    assert row["penalized_c95"] >= row["total_cost"]
    if not row["success_95"]:
        assert np.isnan(row["c95"])
        assert row["penalized_c95"] > row["total_cost"]
