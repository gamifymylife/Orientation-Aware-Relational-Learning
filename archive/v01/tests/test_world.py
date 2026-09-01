import numpy as np
from oarl_bench.config import BenchmarkConfig
from oarl_bench.world import generate_world

def test_default_orientation_is_uninformative():
    cfg = BenchmarkConfig(n_mechanisms=8, n_orientations=6, n_interventions=5)
    world = generate_world(cfg, seed=3)
    # For each intervention at orientation zero, every mechanism must have the same mean.
    assert np.allclose(
        world.means[:, 0, :],
        world.means[0:1, 0, :],
    )

def test_alternative_orientation_exists():
    cfg = BenchmarkConfig(n_mechanisms=8, n_orientations=6, n_interventions=5)
    world = generate_world(cfg, seed=4)
    variances = np.var(world.means[:, 1:, :], axis=0)
    assert np.max(variances) > 0

def test_positive_cost_and_stability():
    cfg = BenchmarkConfig()
    world = generate_world(cfg, seed=1)
    assert np.all(world.cost > 0)
    assert np.all(world.stability > 0)
