import numpy as np
from oarl_bench.config import BenchmarkConfig
from oarl_bench.world import generate_world


def test_no_orientation_value_has_identical_likelihood_geometry():
    cfg = BenchmarkConfig(world_regime="no_orientation_value", n_orientations=6)
    w = generate_world(cfg, 10)
    for o in range(1, w.n_orientations):
        assert np.allclose(w.means[:, o, :], w.means[:, 0, :])
    assert np.allclose(w.cost, 1.0)
    assert np.allclose(w.stability, 1.0)


def test_informative_unstable_has_high_k_probe():
    cfg = BenchmarkConfig(world_regime="informative_unstable", n_orientations=6)
    w = generate_world(cfg, 11)
    assert w.stability[1] >= 8.0
    assert np.var(w.means[:, 1, :]) > np.var(w.means[:, 0, :])


def test_orientation_exclusive_default_pairs_identical_and_alt_separates():
    cfg = BenchmarkConfig(world_regime="orientation_exclusive", n_mechanisms=8, n_orientations=5)
    w = generate_world(cfg, 12)
    for h in range(0, 8, 2):
        assert np.allclose(w.means[h, 0, :], w.means[h + 1, 0, :])
        assert not np.allclose(w.means[h, 1, :], w.means[h + 1, 1, :])
