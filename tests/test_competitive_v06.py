import pytest

from oarl_bench.competitive import (
    PairDecision,
    PairPrediction,
    PairTruth,
    evaluate_pair_predictions,
    exact_duplicate_baseline,
    similarity_baseline,
)


def test_pair_metrics_treat_unknown_as_abstention_not_false_merge():
    truth = [
        PairTruth("a", "b", True),
        PairTruth("a", "c", False),
        PairTruth("b", "c", False),
    ]
    predictions = [
        PairPrediction("a", "b", PairDecision.UNKNOWN),
        PairPrediction("a", "c", PairDecision.DISTINCT),
        PairPrediction("b", "c", PairDecision.EQUIVALENT),
    ]

    metrics = evaluate_pair_predictions(truth, predictions)

    assert metrics.false_positive == 1
    assert metrics.unknown_equivalent == 1
    assert metrics.false_merge_rate == pytest.approx(0.5)
    assert metrics.abstention_rate == pytest.approx(1.0 / 3.0)
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0


def test_exact_duplicate_baseline_only_merges_identity():
    predictions = exact_duplicate_baseline(
        {
            "a": [0.0, 1.0, 2.0],
            "b": [0.0, 1.0, 2.0],
            "c": [0.0, 1.0, 2.0001],
        }
    )
    decisions = {(p.left, p.right): p.decision for p in predictions}

    assert decisions[("a", "b")] is PairDecision.EQUIVALENT
    assert decisions[("a", "c")] is PairDecision.DISTINCT
    assert decisions[("b", "c")] is PairDecision.DISTINCT


def test_similarity_baseline_has_frozen_abstention_band():
    predictions = similarity_baseline(
        {
            "a": [0.0, 1.0, 2.0],
            "b": [0.0, 1.0, 2.01],
            "c": [0.0, 1.0, 4.0],
        },
        max_normalized_rmse=0.02,
        abstention_band=0.01,
    )
    decisions = {(p.left, p.right): p.decision for p in predictions}

    assert decisions[("a", "b")] in {
        PairDecision.EQUIVALENT,
        PairDecision.UNKNOWN,
    }
    assert decisions[("a", "c")] is PairDecision.DISTINCT
    assert decisions[("b", "c")] is PairDecision.DISTINCT


def test_metric_evaluator_rejects_missing_predictions():
    truth = [PairTruth("a", "b", False), PairTruth("a", "c", False)]
    predictions = [PairPrediction("a", "b", PairDecision.DISTINCT)]

    with pytest.raises(ValueError, match="prediction pair mismatch"):
        evaluate_pair_predictions(truth, predictions)
