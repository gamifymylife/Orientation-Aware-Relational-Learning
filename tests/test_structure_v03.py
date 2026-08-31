from dataclasses import replace
import numpy as np

from oarl_bench.config import BenchmarkConfig
from oarl_bench.world import generate_world
from oarl_bench.inference import update_posterior
from oarl_bench.runner import run_episode


def test_equivalent_orientations_preserve_likelihood_geometry():
    cfg = BenchmarkConfig(world_regime="equivalent_redundancy", n_orientations=12, n_equivalence_classes=3, n_interventions=7)
    w = generate_world(cfg, 7)
    for o in range(w.n_orientations):
        rep = w.class_representative[w.orientation_class[o]]
        for a in range(w.n_interventions):
            ca = w.to_canonical_intervention[o, a]
            s = w.transform_scale[o]
            b = w.transform_offset[o]
            assert np.allclose(w.means[:, o, a], b + s * w.means[:, rep, ca])
            assert np.isclose(w.nominal_sigma[o, a], abs(s) * w.nominal_sigma[rep, ca])


def test_transport_update_matches_raw_update():
    cfg = BenchmarkConfig(world_regime="equivalent_redundancy", n_orientations=12, n_equivalence_classes=3, n_interventions=7)
    w = generate_world(cfg, 11)
    o = 8; a = 3
    y = float(w.means[w.true_h, o, a] + 0.37 * w.nominal_sigma[o, a])
    p = np.full(w.n_mechanisms, 1.0 / w.n_mechanisms)
    raw = update_posterior(p, w.means[:, o, a], float(w.nominal_sigma[o, a]), y)
    rep, ca, y_can, sigma_can = w.transport_observation(o, a, y)
    transported = update_posterior(p, w.means[:, rep, ca], sigma_can, y_can)
    assert np.allclose(raw, transported, atol=1e-12)


def test_structured_quotient_reduces_score_evaluations():
    cfg = BenchmarkConfig(world_regime="equivalent_redundancy", n_mechanisms=10, n_orientations=16, n_equivalence_classes=4, n_interventions=10, budget=15)
    g = run_episode(cfg, 3, "generic_cost_tiebreak")
    s = run_episode(cfg, 3, "structured_oarl")
    assert s["score_evals"] < g["score_evals"]
    assert s["score_evals"] <= g["score_evals"] // 3


def test_asymmetry_gate_never_queries_invalid_orientation():
    cfg = BenchmarkConfig(world_regime="asymmetric_invalid", n_orientations=12, invalid_orientation_fraction=0.25, budget=12)
    s = run_episode(cfg, 5, "structured_oarl")
    assert s["inadmissible_queries"] == 0


def test_unique_structure_has_no_quotient_compression():
    cfg = BenchmarkConfig(world_regime="standard", n_orientations=8, n_interventions=6, budget=4)
    g = run_episode(cfg, 9, "generic_cost_tiebreak")
    s = run_episode(cfg, 9, "structured_oarl")
    assert s["n_equivalence_classes"] == s["n_orientations"]
    assert s["score_evals"] == g["score_evals"]
