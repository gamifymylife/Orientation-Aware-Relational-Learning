import numpy as np
from oarl_bench.config import BenchmarkConfig
from oarl_bench.world import generate_world


def test_false_splits_only_increase_declared_class_count():
    base = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_orientations=16,
        n_equivalence_classes=4,
        n_interventions=8,
    )
    clean = generate_world(base, 42)
    split = generate_world(BenchmarkConfig(**{**base.__dict__, "metadata_false_split_rate": 1.0}), 42)
    assert split.n_true_equivalence_classes == clean.n_true_equivalence_classes == 4
    assert split.n_equivalence_classes == 16


def test_false_merge_reduces_declared_class_count_below_truth():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_orientations=24,
        n_equivalence_classes=6,
        n_interventions=8,
        metadata_false_merge_rate=0.5,
    )
    w = generate_world(cfg, 43)
    assert w.n_true_equivalence_classes == 6
    assert w.n_equivalence_classes < 6


def test_false_positive_admissibility_reopens_some_invalid_orientations():
    cfg = BenchmarkConfig(
        world_regime="asymmetric_invalid",
        n_orientations=16,
        invalid_orientation_fraction=0.25,
        admissibility_false_positive_rate=0.5,
    )
    w = generate_world(cfg, 44)
    assert np.sum(w.admissible & ~w.true_admissible) > 0


def test_false_negative_admissibility_closes_some_valid_orientations():
    cfg = BenchmarkConfig(
        world_regime="standard",
        n_orientations=16,
        admissibility_false_negative_rate=0.5,
    )
    w = generate_world(cfg, 45)
    assert np.sum((~w.admissible) & w.true_admissible) > 0


def test_zero_metadata_noise_preserves_true_structure():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_orientations=16,
        n_equivalence_classes=4,
    )
    w = generate_world(cfg, 46)
    assert np.array_equal(w.orientation_class, w.true_orientation_class)
    assert np.array_equal(w.class_representative, w.true_class_representative)
    assert np.array_equal(w.admissible, w.true_admissible)
