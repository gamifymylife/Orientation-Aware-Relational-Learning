import numpy as np

from oarl_bench.certification import (
    CertificateStatus,
    apply_discovered_structure,
    certify_pair_exact,
    discover_exact_structure,
    pairwise_structure_metrics,
)
from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_episode_on_world
from oarl_bench.world import generate_world


def test_exact_pair_certificate_recovers_transport():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=12,
        n_orientations=12,
        n_equivalence_classes=3,
        n_interventions=7,
    )
    w = generate_world(cfg, 17)
    target = 8
    cls = int(w.true_orientation_class[target])
    rep = int(w.true_class_representative[cls])
    cert = certify_pair_exact(
        w.means[:, target, :], w.nominal_sigma[target],
        w.means[:, rep, :], w.nominal_sigma[rep],
        target=target, reference=rep,
    )
    assert cert.status is CertificateStatus.EQUIVALENT
    assert np.array_equal(cert.intervention_map, w.true_to_canonical_intervention[target])
    assert np.isclose(cert.scale, w.true_transform_scale[target])
    assert np.isclose(cert.offset, w.true_transform_offset[target])


def test_exact_structure_discovery_recovers_hidden_classes_without_truth_metadata():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=12,
        n_orientations=16,
        n_equivalence_classes=4,
        n_interventions=8,
    )
    w = generate_world(cfg, 23)
    d = discover_exact_structure(w)
    metrics = pairwise_structure_metrics(w, d)
    assert d.n_classes == w.n_true_equivalence_classes
    assert metrics["pair_precision"] == 1.0
    assert metrics["pair_recall"] == 1.0
    assert metrics["pair_fp"] == 0.0
    assert metrics["pair_fn"] == 0.0


def test_unique_world_does_not_false_merge():
    cfg = BenchmarkConfig(
        world_regime="standard",
        n_mechanisms=12,
        n_orientations=8,
        n_interventions=7,
    )
    w = generate_world(cfg, 29)
    d = discover_exact_structure(w)
    assert d.n_classes == w.n_orientations
    assert pairwise_structure_metrics(w, d)["pair_fp"] == 0.0


def test_discovered_quotient_matches_oracle_and_reduces_score_evals():
    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=10,
        n_orientations=16,
        n_equivalence_classes=4,
        n_interventions=8,
        budget=12,
    )
    seed = 31
    w = generate_world(cfg, seed)
    d = discover_exact_structure(w)
    dw = apply_discovered_structure(w, d)

    generic = run_episode_on_world(cfg, seed, "generic_cost_tiebreak", w)
    oracle = run_episode_on_world(cfg, seed, "structured_oarl", w)
    discovered = run_episode_on_world(cfg, seed, "structured_oarl", dw)

    assert discovered["correct_argmax"] == oracle["correct_argmax"]
    assert discovered["success_95"] == oracle["success_95"]
    assert discovered["score_evals"] == oracle["score_evals"]
    assert discovered["score_evals"] < generic["score_evals"]
