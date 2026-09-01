from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class CSuiteView:
    """One independently supplied CSuite interventional environment.

    Discovery arrays are exposed to competing methods. Holdout arrays and semantic
    metadata are retained for evaluator/oracle use only.
    """

    system_id: str
    view_id: str
    discovery_primary: np.ndarray
    discovery_reference: np.ndarray
    holdout_primary: np.ndarray
    holdout_reference: np.ndarray
    intervention_idxs: tuple[int, ...]
    effect_idxs: tuple[int, ...]
    conditioning_idxs: tuple[int, ...]


@dataclass(frozen=True)
class ViewSignature:
    view_id: str
    effect: np.ndarray
    uncertainty: np.ndarray


@dataclass(frozen=True)
class OraclePairScore:
    left: str
    right: str
    nrmse: float
    correlation: float
    scale: float
    offset: float


def _as_2d_float(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a 2D numeric array")
    if array.shape[0] < 4:
        raise ValueError(f"{name} requires at least four rows for a discovery/holdout split")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values")
    return array


def _stable_row_split(n_rows: int, *, seed_material: str) -> tuple[np.ndarray, np.ndarray]:
    digest = hashlib.sha256(seed_material.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], "little", signed=False)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n_rows)
    cut = n_rows // 2
    return np.sort(order[:cut]), np.sort(order[cut:])


def load_csuite_interventions(
    path: str | Path,
    *,
    system_id: str,
) -> list[CSuiteView]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    environments = payload.get("environments")
    if not isinstance(environments, list) or not environments:
        raise ValueError("CSuite interventions.json has no environments")

    views: list[CSuiteView] = []
    for index, env in enumerate(environments):
        if not isinstance(env, dict):
            raise ValueError(f"environment {index} is not an object")
        primary = _as_2d_float(env.get("test_data"), name=f"environment[{index}].test_data")
        reference = _as_2d_float(
            env.get("reference_data"), name=f"environment[{index}].reference_data"
        )
        if primary.shape != reference.shape:
            raise ValueError(f"environment {index} primary/reference shapes differ")

        view_id = f"{system_id}:env:{index:04d}"
        discovery_rows, holdout_rows = _stable_row_split(
            primary.shape[0], seed_material=view_id
        )
        views.append(
            CSuiteView(
                system_id=system_id,
                view_id=view_id,
                discovery_primary=primary[discovery_rows],
                discovery_reference=reference[discovery_rows],
                holdout_primary=primary[holdout_rows],
                holdout_reference=reference[holdout_rows],
                intervention_idxs=tuple(int(v) for v in env.get("intervention_idxs", [])),
                effect_idxs=tuple(int(v) for v in env.get("effect_idxs", [])),
                conditioning_idxs=tuple(int(v) for v in env.get("conditioning_idxs", [])),
            )
        )
    return views


def response_signature(primary: np.ndarray, reference: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Intervention-minus-reference response and standard error in published coordinates.

    No graph/SEM metadata is used. Crucially, the response vector is not standardized
    independently by split- or view-specific coordinate variances: doing so can destroy
    a genuine global affine relation between two response vectors. Competitors may
    normalize a whole vector using their own frozen method, but the neutral adapter
    preserves CSuite's common node coordinate system.
    """

    if primary.shape != reference.shape or primary.ndim != 2:
        raise ValueError("primary and reference must be equally shaped 2D arrays")
    delta = primary.mean(axis=0) - reference.mean(axis=0)
    var = primary.var(axis=0, ddof=1) / primary.shape[0]
    var += reference.var(axis=0, ddof=1) / reference.shape[0]
    se = np.sqrt(np.maximum(var, 1e-18))
    return delta, se


def discovery_signatures(views: Iterable[CSuiteView]) -> dict[str, Sequence[float]]:
    result: dict[str, Sequence[float]] = {}
    for view in views:
        effect, _ = response_signature(view.discovery_primary, view.discovery_reference)
        result[view.view_id] = effect.tolist()
    return result


def holdout_signature(view: CSuiteView) -> ViewSignature:
    effect, uncertainty = response_signature(view.holdout_primary, view.holdout_reference)
    return ViewSignature(view_id=view.view_id, effect=effect, uncertainty=uncertainty)


def _fit_positive_affine(source: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    x = np.asarray(source, dtype=float)
    y = np.asarray(target, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("source/target signatures must be equally shaped vectors")
    xc = x - x.mean()
    denom = float(np.dot(xc, xc))
    if denom <= 1e-18:
        return 0.0, float(y.mean())
    scale = float(np.dot(xc, y - y.mean()) / denom)
    offset = float(y.mean() - scale * x.mean())
    return scale, offset


def oracle_pair_score(left: CSuiteView, right: CSuiteView) -> OraclePairScore:
    """Evaluator-only transport score computed on the disjoint holdout split.

    This is deliberately a score, not a hard equivalence label. Pilot work must freeze
    a threshold before any confirmatory systems are evaluated.
    """

    a = holdout_signature(left).effect
    b = holdout_signature(right).effect
    if a.shape != b.shape:
        return OraclePairScore(left.view_id, right.view_id, np.inf, -1.0, np.nan, np.nan)
    scale, offset = _fit_positive_affine(a, b)
    if scale <= 0.0:
        return OraclePairScore(left.view_id, right.view_id, np.inf, -1.0, scale, offset)
    fitted = offset + scale * a
    norm = max(float(np.std(b)), 1e-12)
    nrmse = float(np.sqrt(np.mean((fitted - b) ** 2)) / norm)
    if a.size < 2 or np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
        corr = 1.0 if nrmse <= 1e-12 else 0.0
    else:
        corr = float(np.corrcoef(a, b)[0, 1])
    return OraclePairScore(left.view_id, right.view_id, nrmse, corr, scale, offset)


def all_oracle_pair_scores(views: Sequence[CSuiteView]) -> list[OraclePairScore]:
    scores: list[OraclePairScore] = []
    for i, left in enumerate(views):
        for right in views[i + 1 :]:
            scores.append(oracle_pair_score(left, right))
    return scores
