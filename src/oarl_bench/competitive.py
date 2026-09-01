from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

import numpy as np


class PairDecision(str, Enum):
    EQUIVALENT = "equivalent"
    DISTINCT = "distinct"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PairTruth:
    left: str
    right: str
    equivalent: bool


@dataclass(frozen=True)
class PairPrediction:
    left: str
    right: str
    decision: PairDecision


@dataclass(frozen=True)
class PairMetrics:
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int
    unknown_equivalent: int
    unknown_distinct: int
    precision: float
    recall: float
    false_merge_rate: float
    abstention_rate: float


def _key(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise ValueError("pair members must be different")
    return tuple(sorted((left, right)))


def evaluate_pair_predictions(
    truth: Iterable[PairTruth],
    predictions: Iterable[PairPrediction],
) -> PairMetrics:
    truth_map: dict[tuple[str, str], bool] = {
        _key(item.left, item.right): item.equivalent for item in truth
    }
    prediction_map: dict[tuple[str, str], PairDecision] = {
        _key(item.left, item.right): item.decision for item in predictions
    }

    if set(truth_map) != set(prediction_map):
        missing = sorted(set(truth_map) - set(prediction_map))
        extra = sorted(set(prediction_map) - set(truth_map))
        raise ValueError(f"prediction pair mismatch: missing={missing}, extra={extra}")

    tp = fp = fn = tn = unknown_equivalent = unknown_distinct = 0
    for pair, is_equivalent in truth_map.items():
        decision = prediction_map[pair]
        if decision is PairDecision.UNKNOWN:
            if is_equivalent:
                unknown_equivalent += 1
            else:
                unknown_distinct += 1
            continue
        predicted_equivalent = decision is PairDecision.EQUIVALENT
        if is_equivalent and predicted_equivalent:
            tp += 1
        elif not is_equivalent and predicted_equivalent:
            fp += 1
        elif is_equivalent and not predicted_equivalent:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn + unknown_equivalent) if tp + fn + unknown_equivalent else 1.0
    distinct_total = fp + tn + unknown_distinct
    false_merge_rate = fp / distinct_total if distinct_total else 0.0
    total = len(truth_map)
    abstention_rate = (unknown_equivalent + unknown_distinct) / total if total else 0.0

    return PairMetrics(
        true_positive=tp,
        false_positive=fp,
        false_negative=fn,
        true_negative=tn,
        unknown_equivalent=unknown_equivalent,
        unknown_distinct=unknown_distinct,
        precision=precision,
        recall=recall,
        false_merge_rate=false_merge_rate,
        abstention_rate=abstention_rate,
    )


def exact_duplicate_baseline(
    signatures: Mapping[str, Sequence[float]],
    *,
    atol: float = 0.0,
    rtol: float = 0.0,
) -> list[PairPrediction]:
    names = sorted(signatures)
    predictions: list[PairPrediction] = []
    for i, left in enumerate(names):
        a = np.asarray(signatures[left], dtype=float)
        for right in names[i + 1 :]:
            b = np.asarray(signatures[right], dtype=float)
            equivalent = a.shape == b.shape and np.allclose(a, b, atol=atol, rtol=rtol)
            predictions.append(
                PairPrediction(
                    left=left,
                    right=right,
                    decision=(
                        PairDecision.EQUIVALENT if equivalent else PairDecision.DISTINCT
                    ),
                )
            )
    return predictions


def similarity_baseline(
    signatures: Mapping[str, Sequence[float]],
    *,
    max_normalized_rmse: float,
    abstention_band: float = 0.0,
) -> list[PairPrediction]:
    if max_normalized_rmse < 0.0:
        raise ValueError("max_normalized_rmse must be non-negative")
    if abstention_band < 0.0:
        raise ValueError("abstention_band must be non-negative")

    names = sorted(signatures)
    predictions: list[PairPrediction] = []
    for i, left in enumerate(names):
        a = np.asarray(signatures[left], dtype=float)
        for right in names[i + 1 :]:
            b = np.asarray(signatures[right], dtype=float)
            if a.shape != b.shape:
                decision = PairDecision.DISTINCT
            else:
                scale = max(float(np.std(a)), float(np.std(b)), 1e-12)
                nrmse = float(np.sqrt(np.mean((a - b) ** 2)) / scale)
                lo = max_normalized_rmse - abstention_band
                hi = max_normalized_rmse + abstention_band
                if nrmse <= lo:
                    decision = PairDecision.EQUIVALENT
                elif nrmse >= hi:
                    decision = PairDecision.DISTINCT
                else:
                    decision = PairDecision.UNKNOWN
            predictions.append(PairPrediction(left=left, right=right, decision=decision))
    return predictions
