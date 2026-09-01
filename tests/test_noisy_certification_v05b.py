import numpy as np

from oarl_bench.certification import CertificateStatus
from oarl_bench.config import BenchmarkConfig
from oarl_bench.noisy_certification import (
    certify_pair_noisy,
    discover_noisy_structure,
    draw_predictive_summary,
    noisy_structure_metrics,
)
from oarl_bench.world import generate_world


def _summaries(world, seed, n_samples=2000):
    rng = np.random.default_rng(seed)
    return (
        draw_predictive_summary(world, n_samples, rng),
        draw_predictive_summary(world, n_samples, rng),
    )


def test_mechanism_flat_equivalent_pair_abstains_instead_of_guessing():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=12,
        n_orientations=8,
        n_equivalence_classes=4,
        n_interventions=7,
    )
    world = generate_world(cfg, 17)
    assert world.true_orientation_class[0] == world.true_orientation_class[4]
    fit, validation = _summaries(world, 170505)
    cert = certify_pair_noisy(fit, validation, 4, 0)
    assert cert.status is CertificateStatus.UNKNOWN
    assert "signal" in cert.reason


def test_heldout_unique_worlds_produce_zero_equivalence_certificates():
    # These seeds are intentionally separate from the initial v0.5B pilot.
    configs = [
        (8, 8, 6),
        (12, 8, 7),
        (16, 12, 8),
    ]
    equivalent_calls = 0
    pair_calls = 0
    for h, orientations, interventions in configs:
        cfg = BenchmarkConfig(
            world_regime="standard",
            n_mechanisms=h,
            n_orientations=orientations,
            n_interventions=interventions,
        )
        for seed in range(1000, 1030):
            world = generate_world(cfg, seed)
            fit, validation = _summaries(
                world,
                seed * 1000003 + h * 100 + orientations * 10 + interventions,
            )
            for i in range(orientations):
                for j in range(i):
                    cert = certify_pair_noisy(fit, validation, i, j)
                    pair_calls += 1
                    equivalent_calls += int(cert.status is CertificateStatus.EQUIVALENT)
    assert pair_calls > 4000
    assert equivalent_calls == 0


def test_heldout_equivalent_worlds_keep_perfect_precision_with_useful_coverage():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=12,
        n_orientations=8,
        n_equivalence_classes=4,
        n_interventions=7,
    )
    tp = fp = fn = 0.0
    compression = []
    for seed in range(2000, 2040):
        world = generate_world(cfg, seed)
        discovery = discover_noisy_structure(
            world,
            n_samples=2000,
            certificate_seed=seed * 1000003 + 505021,
        )
        metrics = noisy_structure_metrics(world, discovery)
        tp += metrics["pair_tp"]
        fp += metrics["pair_fp"]
        fn += metrics["pair_fn"]
        compression.append(metrics["compression_fraction"])

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn)
    assert fp == 0.0
    assert precision == 1.0
    # v0.5B is precision-first. Flat/ambiguous true pairs are expected to abstain.
    assert recall >= 0.25
    assert float(np.mean(compression)) >= 0.10


def test_unknown_pairs_never_create_a_quotient_merge():
    cfg = BenchmarkConfig(
        world_regime="standard",
        n_mechanisms=12,
        n_orientations=8,
        n_interventions=7,
    )
    world = generate_world(cfg, 2901)
    discovery = discover_noisy_structure(
        world,
        n_samples=2000,
        certificate_seed=2901505021,
    )
    metrics = noisy_structure_metrics(world, discovery)
    assert metrics["pair_fp"] == 0.0
    assert discovery.n_classes == world.n_orientations
