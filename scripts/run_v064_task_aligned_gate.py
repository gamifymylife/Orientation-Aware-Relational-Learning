from __future__ import annotations

import argparse
import csv
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pygsti
from pygsti.modelpacks import smq1Q_XYI as std


GATES = ("Gxpi2", "Gypi2")
MAX_DEPTH = 7
PARAMETER_DIM = 3
TRUE_FD_STEP = 1e-4
PROBE_SCALES = (0.0025, 0.0050, 0.0100)
SHOTS_PER_SPLIT = 100_000
SEED_A = 640401
SEED_B = 640402
SHORTLIST_K = 8
BOOTSTRAP_DRAWS = 128
BOOTSTRAP_LO = 0.01
BOOTSTRAP_HI = 0.99
BOOTSTRAP_SEED_A = 640411
BOOTSTRAP_SEED_B = 640412
BOOTSTRAP_SEED_POOLED = 640413
FIM_EQ_TOL = 0.20
FIM_DISTINCT_MARGIN = 0.30
DECISION_EQ_TOL = 0.05
DECISION_DISTINCT_MARGIN = 0.10
TV_EQ_TOL = 0.020
TV_DISTINCT_MARGIN = 0.030
TV_ALPHA = 0.001
DOPT_STEPS = 8
DOPT_RIDGE = 1e-9
MAX_LOGDET_LOSS = 0.005
MIN_COMPRESSION = 0.20
VARIANCE_FLOOR = 1e-8
NORM_FLOOR = 1e-12


@dataclass(frozen=True)
class PhysicalCircuit:
    index: int
    circuit: pygsti.circuits.Circuit
    depth: int
    label: str


@dataclass(frozen=True)
class View:
    index: int
    physical_index: int
    complement: bool
    depth: int
    label: str


def physical_circuits() -> list[PhysicalCircuit]:
    rows: list[PhysicalCircuit] = []
    index = 0
    for depth in range(1, MAX_DEPTH + 1):
        for sequence in itertools.product(GATES, repeat=depth):
            circuit = pygsti.circuits.Circuit([(gate, 0) for gate in sequence])
            rows.append(
                PhysicalCircuit(
                    index=index,
                    circuit=circuit,
                    depth=depth,
                    label=".".join(sequence),
                )
            )
            index += 1
    return rows


def views_from_circuits(circuits: list[PhysicalCircuit]) -> list[View]:
    views: list[View] = []
    for row in circuits:
        views.append(
            View(
                index=len(views),
                physical_index=row.index,
                complement=False,
                depth=row.depth,
                label=f"{row.label}|ordinary",
            )
        )
        views.append(
            View(
                index=len(views),
                physical_index=row.index,
                complement=True,
                depth=row.depth,
                label=f"{row.label}|complement",
            )
        )
    return views


def success_probability(model, circuit: pygsti.circuits.Circuit) -> float:
    probs = model.probabilities(circuit)
    outcome = sorted(probs, key=str)[0]
    value = float(probs[outcome])
    if not np.isfinite(value) or value < -1e-10 or value > 1.0 + 1e-10:
        raise ValueError(f"invalid probability {value} for {circuit}")
    return float(np.clip(value, 0.0, 1.0))


def rotated_model(axis: int, amount: float):
    rotation = [0.0, 0.0, 0.0]
    rotation[axis] = float(amount)
    return std.target_model().rotate(rotate=tuple(rotation))


def mechanism_probe_library() -> tuple[np.ndarray, list]:
    theta = [np.zeros(PARAMETER_DIM, dtype=float)]
    models = [std.target_model()]
    for axis in range(PARAMETER_DIM):
        for scale in PROBE_SCALES:
            for sign in (-1.0, 1.0):
                vector = np.zeros(PARAMETER_DIM, dtype=float)
                vector[axis] = sign * scale
                theta.append(vector)
                models.append(rotated_model(axis, sign * scale))
    return np.asarray(theta, dtype=float), models


def exact_view_probabilities(
    circuits: list[PhysicalCircuit],
    views: list[View],
    models: list,
) -> np.ndarray:
    physical = np.asarray(
        [[success_probability(model, row.circuit) for model in models] for row in circuits],
        dtype=float,
    )
    result = np.empty((len(views), len(models)), dtype=float)
    for view in views:
        base = physical[view.physical_index]
        result[view.index] = 1.0 - base if view.complement else base
    return result


def exact_true_fims(circuits: list[PhysicalCircuit], views: list[View]) -> np.ndarray:
    target = std.target_model()
    plus = [rotated_model(axis, TRUE_FD_STEP) for axis in range(PARAMETER_DIM)]
    minus = [rotated_model(axis, -TRUE_FD_STEP) for axis in range(PARAMETER_DIM)]
    physical = np.empty((len(circuits), PARAMETER_DIM, PARAMETER_DIM), dtype=float)
    for row in circuits:
        p0 = success_probability(target, row.circuit)
        gradient = np.asarray(
            [
                (success_probability(plus[axis], row.circuit) - success_probability(minus[axis], row.circuit))
                / (2.0 * TRUE_FD_STEP)
                for axis in range(PARAMETER_DIM)
            ],
            dtype=float,
        )
        variance = max(p0 * (1.0 - p0), VARIANCE_FLOOR)
        physical[row.index] = np.outer(gradient, gradient) / variance
    result = np.empty((len(views), PARAMETER_DIM, PARAMETER_DIM), dtype=float)
    for view in views:
        result[view.index] = physical[view.physical_index]
    return result


def slope_coefficients(theta: np.ndarray) -> np.ndarray:
    coeff = np.zeros((PARAMETER_DIM, theta.shape[0]), dtype=float)
    for axis in range(PARAMETER_DIM):
        x = theta[:, axis]
        denom = float(np.dot(x, x))
        if denom <= 0.0:
            raise ValueError("probe library lacks slope support")
        coeff[axis] = x / denom
    return coeff


def estimate_fims(probabilities: np.ndarray, coeff: np.ndarray) -> np.ndarray:
    p = np.asarray(probabilities, dtype=float)
    gradient = np.einsum("...p,ap->...a", p, coeff)
    p0 = p[..., 0]
    variance = np.maximum(p0 * (1.0 - p0), VARIANCE_FLOOR)
    fim = gradient[..., :, None] * gradient[..., None, :] / variance[..., None, None]
    return 0.5 * (fim + np.swapaxes(fim, -1, -2))


def bootstrap_fims(
    p_hat: np.ndarray,
    n_shots: int,
    coeff: np.ndarray,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    se = np.sqrt(np.maximum(p_hat * (1.0 - p_hat), 1e-12) / float(n_shots))
    draws = rng.normal(
        loc=p_hat[None, :, :],
        scale=se[None, :, :],
        size=(BOOTSTRAP_DRAWS, p_hat.shape[0], p_hat.shape[1]),
    )
    draws = np.clip(draws, 1e-8, 1.0 - 1e-8)
    return estimate_fims(draws, coeff)


def relative_fim_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    diff = np.linalg.norm(a - b, axis=(-2, -1))
    na = np.linalg.norm(a, axis=(-2, -1))
    nb = np.linalg.norm(b, axis=(-2, -1))
    denom = np.maximum(np.maximum(na, nb), NORM_FLOOR)
    return diff / denom


def anchor_states() -> np.ndarray:
    anchors = [0.1 * np.eye(PARAMETER_DIM), np.eye(PARAMETER_DIM), 10.0 * np.eye(PARAMETER_DIM)]
    for perm in itertools.permutations((0.1, 1.0, 10.0)):
        anchors.append(np.diag(np.asarray(perm, dtype=float)))
    return np.asarray(anchors, dtype=float)


def dopt_gains(fims: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    arr = np.asarray(fims, dtype=float)
    base = np.linalg.slogdet(anchors)[1]
    expanded = anchors.reshape((1,) * (arr.ndim - 2) + anchors.shape)
    fim_expanded = np.expand_dims(arr, axis=-3)
    values = np.linalg.slogdet(expanded + fim_expanded)[1]
    return values - base


def decision_distance(a: np.ndarray, b: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    ga = dopt_gains(a, anchors)
    gb = dopt_gains(b, anchors)
    return np.max(np.abs(ga - gb), axis=-1)


def simulate_split(probabilities: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    counts = rng.binomial(SHOTS_PER_SPLIT, probabilities)
    return counts.astype(float) / float(SHOTS_PER_SPLIT)


def shortlist_pairs(fims: np.ndarray) -> list[tuple[int, int]]:
    n = fims.shape[0]
    pairs: set[tuple[int, int]] = set()
    for i in range(n):
        distances = np.asarray([relative_fim_distance(fims[i], fims[j]) if i != j else np.inf for j in range(n)])
        nearest = np.argsort(distances)[:SHORTLIST_K]
        for j in nearest:
            a, b = sorted((i, int(j)))
            pairs.add((a, b))
    return sorted(pairs)


def task_truth_matrices(true_fims: np.ndarray, anchors: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = true_fims.shape[0]
    equivalent = np.eye(n, dtype=bool)
    fim_distance = np.zeros((n, n), dtype=float)
    dec_distance = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            df = float(relative_fim_distance(true_fims[i], true_fims[j]))
            dd = float(decision_distance(true_fims[i], true_fims[j], anchors))
            fim_distance[i, j] = fim_distance[j, i] = df
            dec_distance[i, j] = dec_distance[j, i] = dd
            ok = df <= FIM_EQ_TOL and dd <= DECISION_EQ_TOL
            equivalent[i, j] = equivalent[j, i] = ok
    return equivalent, fim_distance, dec_distance


def complete_link_oracle(equivalent: np.ndarray) -> list[list[int]]:
    classes: list[list[int]] = []
    for i in range(equivalent.shape[0]):
        placed = False
        for group in classes:
            if all(bool(equivalent[i, j]) for j in group):
                group.append(i)
                placed = True
                break
        if not placed:
            classes.append([i])
    return classes


def complete_link_learned(n: int, predictions: dict[tuple[int, int], str]) -> list[list[int]]:
    classes: list[list[int]] = []
    for i in range(n):
        placed = False
        for group in classes:
            if all(predictions.get(tuple(sorted((i, j)))) == "EQUIVALENT" for j in group):
                group.append(i)
                placed = True
                break
        if not placed:
            classes.append([i])
    return classes


def bootstrap_pair_bounds(
    boots: np.ndarray,
    i: int,
    j: int,
    anchors: np.ndarray,
) -> tuple[float, float, float, float]:
    df = relative_fim_distance(boots[:, i], boots[:, j])
    dd = decision_distance(boots[:, i], boots[:, j], anchors)
    return (
        float(np.quantile(df, BOOTSTRAP_LO)),
        float(np.quantile(df, BOOTSTRAP_HI)),
        float(np.quantile(dd, BOOTSTRAP_LO)),
        float(np.quantile(dd, BOOTSTRAP_HI)),
    )


def point_pair_metrics(fims: np.ndarray, i: int, j: int, anchors: np.ndarray) -> tuple[float, float]:
    return (
        float(relative_fim_distance(fims[i], fims[j])),
        float(decision_distance(fims[i], fims[j], anchors)),
    )


def tv_bounds(
    p: np.ndarray,
    n_shots: int,
    i: int,
    j: int,
    flip: bool,
) -> tuple[float, float]:
    left = p[i]
    right = 1.0 - p[j] if flip else p[j]
    diff = np.abs(left - right)
    se = np.sqrt(
        np.maximum(left * (1.0 - left), 1e-12) / float(n_shots)
        + np.maximum(right * (1.0 - right), 1e-12) / float(n_shots)
    )
    z = NormalDist().inv_cdf(1.0 - TV_ALPHA / (2.0 * p.shape[1]))
    upper = float(np.max(diff + z * se))
    lower = float(np.max(np.maximum(diff - z * se, 0.0)))
    return lower, upper


def classify_pairs(
    pairs: list[tuple[int, int]],
    p_a: np.ndarray,
    p_b: np.ndarray,
    p_pool: np.ndarray,
    fim_a: np.ndarray,
    fim_b: np.ndarray,
    fim_pool: np.ndarray,
    boot_a: np.ndarray,
    boot_b: np.ndarray,
    boot_pool: np.ndarray,
    anchors: np.ndarray,
    truth: np.ndarray,
    true_df: np.ndarray,
    true_dd: np.ndarray,
) -> tuple[dict[str, dict[tuple[int, int], str]], list[dict]]:
    methods = {name: {} for name in ("TV-UCB", "FIM-POINT", "FIM-UCB", "OARL-TASK-XFIT")}
    rows: list[dict] = []

    for i, j in pairs:
        identity_error = float(np.max(np.abs(p_pool[i] - p_pool[j])))
        flip_error = float(np.max(np.abs(p_pool[i] - (1.0 - p_pool[j]))))
        flip = flip_error < identity_error
        tv_lo, tv_hi = tv_bounds(p_pool, 2 * SHOTS_PER_SPLIT, i, j, flip)
        if tv_hi <= TV_EQ_TOL:
            tv_status = "EQUIVALENT"
        elif tv_lo >= TV_DISTINCT_MARGIN:
            tv_status = "DISTINCT"
        else:
            tv_status = "UNKNOWN"
        methods["TV-UCB"][(i, j)] = tv_status

        point_df, point_dd = point_pair_metrics(fim_pool, i, j, anchors)
        fim_point_status = "EQUIVALENT" if (point_df <= FIM_EQ_TOL and point_dd <= DECISION_EQ_TOL) else "DISTINCT"
        methods["FIM-POINT"][(i, j)] = fim_point_status

        pool_lo_df, pool_hi_df, pool_lo_dd, pool_hi_dd = bootstrap_pair_bounds(boot_pool, i, j, anchors)
        if pool_hi_df <= FIM_EQ_TOL and pool_hi_dd <= DECISION_EQ_TOL:
            fim_ucb_status = "EQUIVALENT"
        elif pool_lo_df >= FIM_DISTINCT_MARGIN or pool_lo_dd >= DECISION_DISTINCT_MARGIN:
            fim_ucb_status = "DISTINCT"
        else:
            fim_ucb_status = "UNKNOWN"
        methods["FIM-UCB"][(i, j)] = fim_ucb_status

        a_lo_df, a_hi_df, a_lo_dd, a_hi_dd = bootstrap_pair_bounds(boot_a, i, j, anchors)
        b_lo_df, b_hi_df, b_lo_dd, b_hi_dd = bootstrap_pair_bounds(boot_b, i, j, anchors)
        if (
            a_hi_df <= FIM_EQ_TOL
            and b_hi_df <= FIM_EQ_TOL
            and pool_hi_df <= FIM_EQ_TOL
            and a_hi_dd <= DECISION_EQ_TOL
            and b_hi_dd <= DECISION_EQ_TOL
            and pool_hi_dd <= DECISION_EQ_TOL
        ):
            oarl_status = "EQUIVALENT"
        elif pool_lo_df >= FIM_DISTINCT_MARGIN or pool_lo_dd >= DECISION_DISTINCT_MARGIN:
            oarl_status = "DISTINCT"
        else:
            oarl_status = "UNKNOWN"
        methods["OARL-TASK-XFIT"][(i, j)] = oarl_status

        for method, status in (
            ("TV-UCB", tv_status),
            ("FIM-POINT", fim_point_status),
            ("FIM-UCB", fim_ucb_status),
            ("OARL-TASK-XFIT", oarl_status),
        ):
            rows.append(
                {
                    "method": method,
                    "i": i,
                    "j": j,
                    "status": status,
                    "task_equivalent": bool(truth[i, j]),
                    "true_fim_distance": float(true_df[i, j]),
                    "true_decision_distance": float(true_dd[i, j]),
                    "point_fim_distance": point_df,
                    "point_decision_distance": point_dd,
                    "pooled_fim_lcb": pool_lo_df,
                    "pooled_fim_ucb": pool_hi_df,
                    "pooled_decision_lcb": pool_lo_dd,
                    "pooled_decision_ucb": pool_hi_dd,
                    "split_a_fim_ucb": a_hi_df,
                    "split_b_fim_ucb": b_hi_df,
                    "split_a_decision_ucb": a_hi_dd,
                    "split_b_decision_ucb": b_hi_dd,
                    "tv_lcb": tv_lo,
                    "tv_ucb": tv_hi,
                    "transport": "flip" if flip else "identity",
                }
            )
    return methods, rows


def class_false_pairs(classes: list[list[int]], truth: np.ndarray) -> int:
    count = 0
    for group in classes:
        for a, b in itertools.combinations(group, 2):
            if not bool(truth[a, b]):
                count += 1
    return count


def representative_indices(classes: list[list[int]], views: list[View]) -> list[int]:
    return [min(group, key=lambda idx: (views[idx].depth, idx)) for group in classes]


def doptimal_design(classes: list[list[int]], views: list[View], true_fims: np.ndarray) -> dict:
    reps = representative_indices(classes, views)
    current = DOPT_RIDGE * np.eye(PARAMETER_DIM)
    selected: list[int] = []
    for _ in range(DOPT_STEPS):
        scored = []
        for idx in reps:
            score = float(np.linalg.slogdet(current + true_fims[idx])[1])
            scored.append((score, -views[idx].depth, -idx, idx))
        chosen = max(scored)[-1]
        selected.append(chosen)
        current = current + true_fims[chosen]
    return {
        "logdet": float(np.linalg.slogdet(current)[1]),
        "score_evaluations": int(len(reps) * DOPT_STEPS),
        "selected_total_depth_cost": int(sum(views[idx].depth for idx in selected)),
        "selected": [views[idx].label for idx in selected],
        "representatives": len(reps),
    }


def method_pair_metrics(
    predictions: dict[tuple[int, int], str],
    truth: np.ndarray,
    total_truth_pairs: int,
) -> dict:
    equivalent_pairs = [pair for pair, status in predictions.items() if status == "EQUIVALENT"]
    true_accepts = sum(bool(truth[i, j]) for i, j in equivalent_pairs)
    false_accepts = len(equivalent_pairs) - true_accepts
    unknown = sum(status == "UNKNOWN" for status in predictions.values())
    precision = float(true_accepts / len(equivalent_pairs)) if equivalent_pairs else None
    recall = float(true_accepts / total_truth_pairs) if total_truth_pairs else None
    return {
        "certified_pairs": len(predictions),
        "accepted_equivalent_pairs": len(equivalent_pairs),
        "true_equivalent_accepts": int(true_accepts),
        "false_task_merges": int(false_accepts),
        "pair_precision": precision,
        "pair_recall_global": recall,
        "unknown_pairs": int(unknown),
        "abstention_fraction": float(unknown / len(predictions)) if predictions else 0.0,
    }


def dominates(a: dict, b: dict) -> bool:
    a_break = float(a.get("break_even_score_cost_shots") or np.inf)
    b_break = float(b.get("break_even_score_cost_shots") or np.inf)
    a_loss = float(a["downstream_logdet_loss_vs_raw"])
    b_loss = float(b["downstream_logdet_loss_vs_raw"])
    conditions = (
        a["false_task_merges"] <= b["false_task_merges"],
        a_loss <= b_loss + 1e-12,
        a["compression_fraction"] >= b["compression_fraction"] - 1e-12,
        a_break <= b_break + 1e-12,
    )
    strict = (
        a["false_task_merges"] < b["false_task_merges"]
        or a_loss < b_loss - 1e-12
        or a["compression_fraction"] > b["compression_fraction"] + 1e-12
        or a_break < b_break - 1e-12
    )
    return all(conditions) and strict


def main() -> None:
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description="Run OARL v0.6.4 task-aligned equivalence gate")
    parser.add_argument("--out", type=Path, default=Path("evidence/v064/outputs"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    circuits = physical_circuits()
    views = views_from_circuits(circuits)
    theta, probe_models = mechanism_probe_library()
    coeff = slope_coefficients(theta)
    anchors = anchor_states()

    true_fims = exact_true_fims(circuits, views)
    truth, true_df, true_dd = task_truth_matrices(true_fims, anchors)
    oracle_classes = complete_link_oracle(truth)

    exact_probs = exact_view_probabilities(circuits, views, probe_models)
    p_a = simulate_split(exact_probs, SEED_A)
    p_b = simulate_split(exact_probs, SEED_B)
    p_pool = 0.5 * (p_a + p_b)

    fim_a = estimate_fims(p_a, coeff)
    fim_b = estimate_fims(p_b, coeff)
    fim_pool = estimate_fims(p_pool, coeff)

    boot_a = bootstrap_fims(p_a, SHOTS_PER_SPLIT, coeff, BOOTSTRAP_SEED_A)
    boot_b = bootstrap_fims(p_b, SHOTS_PER_SPLIT, coeff, BOOTSTRAP_SEED_B)
    boot_pool = bootstrap_fims(p_pool, 2 * SHOTS_PER_SPLIT, coeff, BOOTSTRAP_SEED_POOLED)

    pairs = shortlist_pairs(fim_pool)
    methods, prediction_rows = classify_pairs(
        pairs,
        p_a,
        p_b,
        p_pool,
        fim_a,
        fim_b,
        fim_pool,
        boot_a,
        boot_b,
        boot_pool,
        anchors,
        truth,
        true_df,
        true_dd,
    )

    raw_classes = [[i] for i in range(len(views))]
    classes_by_method = {
        "RAW": raw_classes,
        "ORACLE": oracle_classes,
        **{name: complete_link_learned(len(views), predictions) for name, predictions in methods.items()},
    }

    total_truth_pairs = int(np.sum(np.triu(truth, 1)))
    shortlist_truth_pairs = sum(bool(truth[i, j]) for i, j in pairs)
    shortlist_recall = float(shortlist_truth_pairs / total_truth_pairs) if total_truth_pairs else None

    designs = {name: doptimal_design(classes, views, true_fims) for name, classes in classes_by_method.items()}
    raw_logdet = designs["RAW"]["logdet"]
    raw_score_evals = designs["RAW"]["score_evaluations"]
    finite_evidence_shots = int(len(views) * len(probe_models) * 2 * SHOTS_PER_SPLIT)

    metrics: dict[str, dict] = {}
    for name, classes in classes_by_method.items():
        compression = 1.0 - len(classes) / len(views)
        design = designs[name]
        row = {
            "n_classes": len(classes),
            "compression_fraction": float(compression),
            "class_false_pairs": class_false_pairs(classes, truth) if name not in ("RAW", "ORACLE") else (0 if name == "ORACLE" else None),
            "downstream_logdet": design["logdet"],
            "downstream_logdet_loss_vs_raw": float(raw_logdet - design["logdet"]),
            "downstream_score_evaluations": design["score_evaluations"],
            "selected_total_depth_cost": design["selected_total_depth_cost"],
            "selected": design["selected"],
        }
        if name in methods:
            pair = method_pair_metrics(methods[name], truth, total_truth_pairs)
            row.update(pair)
            saved = raw_score_evals - design["score_evaluations"]
            row["finite_evidence_shots"] = finite_evidence_shots
            row["break_even_score_cost_shots"] = float(finite_evidence_shots / saved) if saved > 0 else None
            if name == "TV-UCB":
                row["certification_work_units"] = int(len(pairs) * len(probe_models))
            elif name == "FIM-POINT":
                row["certification_work_units"] = int(len(pairs))
            elif name == "FIM-UCB":
                row["certification_work_units"] = int(len(pairs) * BOOTSTRAP_DRAWS)
            else:
                row["certification_work_units"] = int(len(pairs) * BOOTSTRAP_DRAWS * 3)
        else:
            row.update(
                {
                    "certified_pairs": None,
                    "accepted_equivalent_pairs": None,
                    "true_equivalent_accepts": None,
                    "false_task_merges": 0 if name == "ORACLE" else None,
                    "pair_precision": None,
                    "pair_recall_global": None,
                    "unknown_pairs": None,
                    "abstention_fraction": None,
                    "finite_evidence_shots": 0,
                    "break_even_score_cost_shots": None,
                    "certification_work_units": 0,
                }
            )
        metrics[name] = row

    oracle_preserved = metrics["ORACLE"]["downstream_logdet_loss_vs_raw"] <= MAX_LOGDET_LOSS
    oarl = metrics["OARL-TASK-XFIT"]
    primary_checks = {
        "oracle_operational_quotient_preserves_raw": bool(oracle_preserved),
        "zero_accepted_task_false_merges": oarl["false_task_merges"] == 0,
        "downstream_logdet_preserved": oarl["downstream_logdet_loss_vs_raw"] <= MAX_LOGDET_LOSS,
        "selected_depth_cost_no_greater_than_raw": oarl["selected_total_depth_cost"] <= metrics["RAW"]["selected_total_depth_cost"],
        "compression_ge_20pct": oarl["compression_fraction"] >= MIN_COMPRESSION,
    }
    primary_pass = all(primary_checks.values())

    dominated_by = [
        name for name in ("TV-UCB", "FIM-UCB") if dominates(metrics[name], oarl)
    ]
    incremental_utility = primary_pass and not dominated_by

    compact_methods = {
        name: {
            "n_classes": row["n_classes"],
            "compression_fraction": row["compression_fraction"],
            "false_task_merges": row["false_task_merges"],
            "pair_precision": row["pair_precision"],
            "pair_recall_global": row["pair_recall_global"],
            "abstention_fraction": row["abstention_fraction"],
            "downstream_logdet": row["downstream_logdet"],
            "downstream_logdet_loss_vs_raw": row["downstream_logdet_loss_vs_raw"],
            "downstream_score_evaluations": row["downstream_score_evaluations"],
            "selected_total_depth_cost": row["selected_total_depth_cost"],
            "break_even_score_cost_shots": row["break_even_score_cost_shots"],
        }
        for name, row in metrics.items()
    }

    summary = {
        "version": "v0.6.4-task-aligned-equivalence",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "model_pack": "smq1Q_XYI",
        "physical_circuits": len(circuits),
        "candidate_views": len(views),
        "mechanism_probe_count": len(probe_models),
        "shots_per_split": SHOTS_PER_SPLIT,
        "finite_evidence_shots_per_learned_method": finite_evidence_shots,
        "shortlist_neighbours": SHORTLIST_K,
        "shortlisted_pairs": len(pairs),
        "task_equivalent_pairs_global": total_truth_pairs,
        "task_equivalent_pairs_in_shortlist": shortlist_truth_pairs,
        "shortlist_recall": shortlist_recall,
        "oracle_classes": len(oracle_classes),
        "oracle_compression_fraction": 1.0 - len(oracle_classes) / len(views),
        "thresholds": {
            "fim_equivalence": FIM_EQ_TOL,
            "fim_distinct": FIM_DISTINCT_MARGIN,
            "decision_equivalence": DECISION_EQ_TOL,
            "decision_distinct": DECISION_DISTINCT_MARGIN,
            "tv_equivalence": TV_EQ_TOL,
            "tv_distinct": TV_DISTINCT_MARGIN,
            "max_logdet_loss": MAX_LOGDET_LOSS,
        },
        "methods": metrics,
        "primary_checks": primary_checks,
        "primary_safety_gate_pass": primary_pass,
        "oarl_dominated_by": dominated_by,
        "incremental_utility_observed": incremental_utility,
        "runtime_s": float(time.perf_counter() - started),
        "claim_boundary": (
            "Prospective same-family fresh-seed test of task-aligned finite-evidence quotienting. "
            "Fisher/D-optimal equivalence and Blackwell-style experiment comparison are prior art; "
            "only learned safe quotienting/abstention utility is under test."
        ),
    }

    compact = {
        "version": summary["version"],
        "candidate_views": len(views),
        "oracle_classes": len(oracle_classes),
        "oracle_compression_fraction": summary["oracle_compression_fraction"],
        "shortlist_recall": shortlist_recall,
        "methods": compact_methods,
        "primary_checks": primary_checks,
        "primary_safety_gate_pass": primary_pass,
        "oarl_dominated_by": dominated_by,
        "incremental_utility_observed": incremental_utility,
    }

    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (args.out / "summary_compact.json").write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")

    with (args.out / "pair_predictions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(prediction_rows[0].keys()))
        writer.writeheader()
        writer.writerows(prediction_rows)

    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
