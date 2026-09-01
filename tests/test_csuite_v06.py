from __future__ import annotations

import json

import numpy as np

from oarl_bench.csuite import (
    all_oracle_pair_scores,
    discovery_signatures,
    load_csuite_interventions,
    oracle_pair_score,
    response_signature,
)


def _env(effect_scale: float) -> dict[str, object]:
    reference = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.1, -0.1, 0.0],
            [-0.1, 0.1, 0.0],
            [0.2, -0.2, 0.1],
            [-0.2, 0.2, -0.1],
            [0.05, -0.05, 0.02],
            [-0.05, 0.05, -0.02],
            [0.15, -0.15, 0.05],
        ]
    )
    shift = np.array([1.0, 2.0, -1.0]) * effect_scale
    primary = reference + shift
    return {
        "conditioning_idxs": [],
        "effect_idxs": [1],
        "intervention_idxs": [0],
        "intervention_values": [1.0],
        "intervention_reference": [0.0],
        "test_data": primary.tolist(),
        "reference_data": reference.tolist(),
    }


def test_loader_keeps_holdout_behind_deterministic_split(tmp_path):
    path = tmp_path / "interventions.json"
    path.write_text(json.dumps({"environments": [_env(1.0), _env(2.0)]}))

    first = load_csuite_interventions(path, system_id="fixture")
    second = load_csuite_interventions(path, system_id="fixture")

    assert len(first) == 2
    assert first[0].view_id == "fixture:env:0000"
    assert first[0].discovery_primary.shape[0] == 4
    assert first[0].holdout_primary.shape[0] == 4
    np.testing.assert_array_equal(first[0].discovery_primary, second[0].discovery_primary)
    np.testing.assert_array_equal(first[0].holdout_primary, second[0].holdout_primary)


def test_response_signature_uses_intervention_minus_reference():
    reference = np.arange(24, dtype=float).reshape(8, 3)
    primary = reference + np.array([1.0, 2.0, -3.0])
    effect, uncertainty = response_signature(primary, reference)

    assert effect.shape == (3,)
    assert uncertainty.shape == (3,)
    assert effect[0] > 0
    assert effect[1] > 0
    assert effect[2] < 0


def test_discovery_signatures_do_not_require_graph_or_sem_metadata(tmp_path):
    path = tmp_path / "interventions.json"
    path.write_text(json.dumps({"environments": [_env(1.0), _env(2.0)]}))
    views = load_csuite_interventions(path, system_id="fixture")
    signatures = discovery_signatures(views)
    assert sorted(signatures) == ["fixture:env:0000", "fixture:env:0001"]
    assert len(signatures["fixture:env:0000"]) == 3


def test_oracle_score_recovers_positive_affine_transport(tmp_path):
    path = tmp_path / "interventions.json"
    path.write_text(json.dumps({"environments": [_env(1.0), _env(2.0)]}))
    views = load_csuite_interventions(path, system_id="fixture")
    score = oracle_pair_score(views[0], views[1])

    assert score.scale > 0
    assert score.nrmse < 1e-8
    assert score.correlation > 0.999999


def test_pair_score_count(tmp_path):
    path = tmp_path / "interventions.json"
    path.write_text(json.dumps({"environments": [_env(1.0), _env(2.0), _env(3.0)]}))
    views = load_csuite_interventions(path, system_id="fixture")
    assert len(all_oracle_pair_scores(views)) == 3
