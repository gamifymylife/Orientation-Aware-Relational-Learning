from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
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
ROTATION_STEP = 1e-4
MECHANISM_AMPLITUDES = (0.0025, 0.0050, 0.0100)
SHOTS_PER_SPLIT = 50_000
SHORTLIST_NEIGHBOURS = 4
ALPHA = 1e-3
RESPONSE_EQUIV_TOL = 0.020
RESPONSE_DISTINCT_MARGIN = 0.030
TASK_EQUIV_REL_FROB_TOL = 1e-8
DOPT_RIDGE = 1e-9
DOPT_SELECTIONS = 8
VIEW_SHUFFLE_SEED = 6303
SPLIT1_SEED = 631_001
SPLIT2_SEED = 631_002


@dataclass(frozen=True)
class PhysicalExperiment:
    index: int
    circuit: pygsti.circuits.Circuit
    depth: int
    label: str
    exact_probe_probabilities: np.ndarray
    fim: np.ndarray


@dataclass(frozen=True)
class View:
    index: int
    physical_index: int
    complemented: bool
    depth: int
    label: str
    exact_probe_probabilities: np.ndarray
    fim: np.ndarray


def circuits_of_depths(min_depth: int, max_depth: int):
    for depth in range(min_depth, max_depth + 1):
        for sequence in itertools.product(GATES, repeat=depth):
            circuit = pygsti.circuits.Circuit([(gate, 0) for gate in sequence])
            yield circuit, depth, ".".join(sequence)


def success_probability(model, circuit: pygsti.circuits.Circuit) -> float:
    probs = model.probabilities(circuit)
    outcome = sorted(probs, key=str)[0]
    value = float(probs[outcome])
    if not np.isfinite(value) or value < -1e-10 or value > 1.0 + 1e-10:
        raise ValueError(f"invalid pyGSTi probability {value} for {circuit}")
    return float(np.clip(value, 0.0, 1.0))


def rotated_model(axis: int, amount: float):
    rotation = [0.0, 0.0, 0.0]
    rotation[axis] = float(amount)
    return std.target_model().rotate(rotate=tuple(rotation))


def mechanism_probe_models() -> list:
    models = [std.target_model()]
    for axis in range(PARAMETER_DIM):
        for amplitude in MECHANISM_AMPLITUDES:
            models.append(rotated_model(axis, +amplitude))
            models.append(rotated_model(axis, -amplitude))
    return models


def local_fim(circuit: pygsti.circuits.Circuit) -> np.ndarray:
    target = std.target_model()
    p = success_probability(target, circuit)
    variance = max(p * (1.0 - p), 1e-10)
    sensitivity = []
    for axis in range(PARAMETER_DIM):
        plus = success_probability(rotated_model(axis, +ROTATION_STEP), circuit)
        minus = success_probability(rotated_model(axis, -ROTATION_STEP), circuit)
        sensitivity.append((plus - minus) / (2.0 * ROTATION_STEP))
    s = np.asarray(sensitivity, dtype=float)
    fim = np.outer(s, s) / variance
    return 0.5 * (fim + fim.T)


def build_views() -> tuple[list[PhysicalExperiment], list[View]]:
    probes = mechanism_probe_models()
    physical: list[PhysicalExperiment] = []
    raw_views: list[View] = []

    for pidx, (circuit, depth, label) in enumerate(circuits_of_depths(1, MAX_DEPTH)):
        exact = np.asarray([success_probability(model, circuit) for model in probes], dtype=float)
        fim = local_fim(circuit)
        experiment = PhysicalExperiment(pidx, circuit, depth, label, exact, fim)
        physical.append(experiment)
        raw_views.append(View(-1, pidx, False, depth, f"view::{pidx}::a", exact, fim))
        raw_views.append(View(-1, pidx, True, depth, f"view::{pidx}::b", 1.0 - exact, fim))

    rng = np.random.default_rng(VIEW_SHUFFLE_SEED)
    order = rng.permutation(len(raw_views))
    views: list[View] = []
    for new_index, old_index in enumerate(order):
        old = raw_views[int(old_index)]
        # Public method inputs use only new_index, depth and finite evidence. The
        # physical/complement metadata remains evaluator-side.
        views.append(
            View(
                index=new_index,
                physical_index=old.physical_index,
                complemented=old.complemented,
                depth=old.depth,
                label=f"candidate_{new_index:04d}",
                exact_probe_probabilities=old.exact_probe_probabilities,
                fim=old.fim,
            )
        )
    return physical, views


def smoothed_probability(counts: np.ndarray, n: int) -> np.ndarray:
    return (counts.astype(float) + 0.5) / (float(n) + 1.0)


def sample_evidence(views: list[View]) -> tuple[np.ndarray, np.ndarray]:
    exact = np.stack([view.exact_probe_probabilities for view in views], axis=0)
    rng1 = np.random.default_rng(SPLIT1_SEED)
    rng2 = np.random.default_rng(SPLIT2_SEED)
    return (
        rng1.binomial(SHOTS_PER_SPLIT, exact),
        rng2.binomial(SHOTS_PER_SPLIT, exact),
    )


def relative_fim_distance(a: np.ndarray, b: np.ndarray) -> float:
    denom = max(float(np.linalg.norm(a)), float(np.linalg.norm(b)), 1e-12)
    return float(np.linalg.norm(a - b) / denom)


def oracle_truth_matrix(views: list[View]) -> np.ndarray:
    n = len(views)
    truth = np.eye(n, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            eq = relative_fim_distance(views[i].fim, views[j].fim) <= TASK_EQUIV_REL_FROB_TOL
            truth[i, j] = truth[j, i] = eq
    return truth


def canonical_signature(p: np.ndarray) -> np.ndarray:
    return np.abs(np.asarray(p, dtype=float) - 0.5)


def normalized_rmse(a: np.ndarray, b: np.ndarray) -> float:
    scale = max(float(np.sqrt(np.mean(a * a))), float(np.sqrt(np.mean(b * b))), 1e-6)
    return float(np.sqrt(np.mean((a - b) ** 2)) / scale)


def shortlist_pairs(pooled: np.ndarray) -> tuple[set[tuple[int, int]], int]:
    signatures = np.stack([canonical_signature(row) for row in pooled], axis=0)
    n = signatures.shape[0]
    pairs: set[tuple[int, int]] = set()
    distance_evals = 0
    for i in range(n):
        scored = []
        for j in range(n):
            if i == j:
                continue
            scored.append((normalized_rmse(signatures[i], signatures[j]), j))
            if j > i:
                distance_evals += 1
        scored.sort(key=lambda item: (item[0], item[1]))
        for _, j in scored[:SHORTLIST_NEIGHBOURS]:
            pairs.add((min(i, j), max(i, j)))
    return pairs, distance_evals


def choose_transform(a: np.ndarray, b: np.ndarray) -> tuple[str, np.ndarray, float]:
    d_identity = np.abs(a - b)
    d_flip = np.abs(a - (1.0 - b))
    key_identity = (float(np.max(d_identity)), float(np.mean(d_identity)), 0)
    key_flip = (float(np.max(d_flip)), float(np.mean(d_flip)), 1)
    if key_identity <= key_flip:
        return "identity", b, float(np.max(d_identity))
    return "flip", 1.0 - b, float(np.max(d_flip))


def simultaneous_bounds(a: np.ndarray, b: np.ndarray, n: int, transform: str):
    bt = b if transform == "identity" else (1.0 - b)
    diff = np.abs(a - bt)
    se = np.sqrt(
        np.maximum(a * (1.0 - a), 0.0) / n
        + np.maximum(b * (1.0 - b), 0.0) / n
    )
    z = NormalDist().inv_cdf(1.0 - ALPHA / (2.0 * len(diff)))
    upper = diff + z * se
    lower = np.maximum(diff - z * se, 0.0)
    return diff, lower, upper


def classify_point(pooled_a: np.ndarray, pooled_b: np.ndarray) -> tuple[str, str]:
    transform, _, maxdiff = choose_transform(pooled_a, pooled_b)
    return ("EQUIVALENT" if maxdiff <= RESPONSE_EQUIV_TOL else "DISTINCT"), transform


def classify_ucb(pooled_a: np.ndarray, pooled_b: np.ndarray, pooled_n: int) -> tuple[str, str]:
    transform, _, _ = choose_transform(pooled_a, pooled_b)
    _, lower, upper = simultaneous_bounds(pooled_a, pooled_b, pooled_n, transform)
    if np.all(upper <= RESPONSE_EQUIV_TOL):
        return "EQUIVALENT", transform
    if np.any(lower > RESPONSE_DISTINCT_MARGIN):
        return "DISTINCT", transform
    return "UNKNOWN", transform


def classify_oarl_xfit(
    split1_a: np.ndarray,
    split1_b: np.ndarray,
    split2_a: np.ndarray,
    split2_b: np.ndarray,
) -> tuple[str, str]:
    transform1, _, _ = choose_transform(split1_a, split1_b)
    transform2, _, _ = choose_transform(split2_a, split2_b)

    pooled_a = 0.5 * (split1_a + split2_a)
    pooled_b = 0.5 * (split1_b + split2_b)
    pooled_transform, _, _ = choose_transform(pooled_a, pooled_b)
    _, pooled_lower, _ = simultaneous_bounds(
        pooled_a, pooled_b, 2 * SHOTS_PER_SPLIT, pooled_transform
    )
    if np.any(pooled_lower > RESPONSE_DISTINCT_MARGIN):
        return "DISTINCT", pooled_transform

    if transform1 != transform2:
        return "UNKNOWN", "unstable"

    _, _, upper1 = simultaneous_bounds(split1_a, split1_b, SHOTS_PER_SPLIT, transform1)
    _, _, upper2 = simultaneous_bounds(split2_a, split2_b, SHOTS_PER_SPLIT, transform2)
    if np.all(upper1 <= RESPONSE_EQUIV_TOL) and np.all(upper2 <= RESPONSE_EQUIV_TOL):
        return "EQUIVALENT", transform1
    return "UNKNOWN", transform1


def classify_shortlist(
    pairs: set[tuple[int, int]],
    split1: np.ndarray,
    split2: np.ndarray,
    method: str,
) -> tuple[dict[tuple[int, int], str], dict[tuple[int, int], str]]:
    p1 = smoothed_probability(split1, SHOTS_PER_SPLIT)
    p2 = smoothed_probability(split2, SHOTS_PER_SPLIT)
    pooled = smoothed_probability(split1 + split2, 2 * SHOTS_PER_SPLIT)
    relation: dict[tuple[int, int], str] = {}
    transport: dict[tuple[int, int], str] = {}
    for i, j in sorted(pairs):
        if method == "POINT":
            status, t = classify_point(pooled[i], pooled[j])
        elif method == "UCB":
            status, t = classify_ucb(pooled[i], pooled[j], 2 * SHOTS_PER_SPLIT)
        elif method == "OARL-XFIT":
            status, t = classify_oarl_xfit(p1[i], p1[j], p2[i], p2[j])
        else:
            raise ValueError(method)
        relation[(i, j)] = status
        transport[(i, j)] = t
    return relation, transport


def get_relation(relation: dict[tuple[int, int], str], i: int, j: int) -> str:
    if i == j:
        return "EQUIVALENT"
    return relation.get((min(i, j), max(i, j)), "UNKNOWN")


def complete_link_classes(n: int, relation: dict[tuple[int, int], str], views: list[View]) -> list[list[int]]:
    order = sorted(range(n), key=lambda idx: (views[idx].depth, idx))
    classes: list[list[int]] = []
    for idx in order:
        placed = False
        for cls in classes:
            if all(get_relation(relation, idx, member) == "EQUIVALENT" for member in cls):
                cls.append(idx)
                placed = True
                break
        if not placed:
            classes.append([idx])
    return classes


def complete_link_oracle_classes(truth: np.ndarray, views: list[View]) -> list[list[int]]:
    order = sorted(range(len(views)), key=lambda idx: (views[idx].depth, idx))
    classes: list[list[int]] = []
    for idx in order:
        placed = False
        for cls in classes:
            if all(bool(truth[idx, member]) for member in cls):
                cls.append(idx)
                placed = True
                break
        if not placed:
            classes.append([idx])
    return classes


def class_representatives(classes: list[list[int]], views: list[View]) -> list[int]:
    return [min(cls, key=lambda idx: (views[idx].depth, idx)) for cls in classes]


def safe_logdet(fim: np.ndarray) -> float:
    sign, value = np.linalg.slogdet(fim + DOPT_RIDGE * np.eye(PARAMETER_DIM))
    if sign <= 0:
        raise ValueError("non-positive regularized determinant")
    return float(value)


def greedy_d_opt_with_replacement(representatives: list[int], views: list[View]) -> dict:
    current = np.zeros((PARAMETER_DIM, PARAMETER_DIM), dtype=float)
    selected: list[int] = []
    score_evals = 0
    for _ in range(DOPT_SELECTIONS):
        scored = []
        for idx in representatives:
            score = safe_logdet(current + views[idx].fim)
            scored.append((score, -views[idx].depth, -idx, idx))
            score_evals += 1
        choice = max(scored)[3]
        selected.append(choice)
        current = current + views[choice].fim
    return {
        "selected": selected,
        "selected_labels": [views[idx].label for idx in selected],
        "selected_depths": [views[idx].depth for idx in selected],
        "selected_total_depth_cost": int(sum(views[idx].depth for idx in selected)),
        "score_evaluations": score_evals,
        "final_logdet": safe_logdet(current),
        "final_fim": [[float(x) for x in row] for row in current],
    }


def pair_metrics(
    relation: dict[tuple[int, int], str],
    truth: np.ndarray,
    shortlisted: set[tuple[int, int]],
) -> dict:
    n = truth.shape[0]
    total_true = 0
    shortlisted_true = 0
    for i in range(n):
        for j in range(i + 1, n):
            if bool(truth[i, j]):
                total_true += 1
                if (i, j) in shortlisted:
                    shortlisted_true += 1

    accepted = [pair for pair, status in relation.items() if status == "EQUIVALENT"]
    tp = sum(1 for i, j in accepted if bool(truth[i, j]))
    fp = len(accepted) - tp
    unknown = sum(1 for status in relation.values() if status == "UNKNOWN")
    distinct = sum(1 for status in relation.values() if status == "DISTINCT")
    return {
        "oracle_equivalent_pairs": total_true,
        "shortlisted_oracle_equivalent_pairs": shortlisted_true,
        "shortlist_pair_recall": shortlisted_true / total_true if total_true else None,
        "accepted_equivalent_pairs": len(accepted),
        "true_accepted_pairs": tp,
        "false_task_merges": fp,
        "pair_precision": tp / len(accepted) if accepted else None,
        "pair_recall_global": tp / total_true if total_true else None,
        "unknown_shortlisted_pairs": unknown,
        "distinct_shortlisted_pairs": distinct,
        "abstention_rate_shortlist": unknown / len(relation) if relation else None,
    }


def class_false_pairs(classes: list[list[int]], truth: np.ndarray) -> int:
    count = 0
    for cls in classes:
        for a_pos, i in enumerate(cls):
            for j in cls[a_pos + 1 :]:
                if not bool(truth[i, j]):
                    count += 1
    return count


def method_summary(
    name: str,
    classes: list[list[int]],
    views: list[View],
    truth: np.ndarray,
    relation: dict[tuple[int, int], str] | None,
    shortlisted: set[tuple[int, int]],
    shortlist_distance_evals: int,
    runtime_s: float,
) -> dict:
    reps = class_representatives(classes, views)
    downstream = greedy_d_opt_with_replacement(reps, views)
    compression = 1.0 - len(classes) / len(views)
    out = {
        "method": name,
        "n_classes": len(classes),
        "compression_fraction": compression,
        "class_false_task_pairs": class_false_pairs(classes, truth),
        "downstream": downstream,
        "runtime_s": runtime_s,
    }
    if relation is not None:
        pm = pair_metrics(relation, truth, shortlisted)
        out["pair_metrics"] = pm
        pair_checks = len(relation)
        factor = 6 if name == "OARL-XFIT" else 2
        cell_uses = shortlist_distance_evals * len(views[0].exact_probe_probabilities) + pair_checks * factor * len(views[0].exact_probe_probabilities)
        out["structural_work"] = {
            "shortlist_distance_evaluations": shortlist_distance_evals,
            "certificate_pair_checks": pair_checks,
            "probability_cell_uses_proxy": int(cell_uses),
        }
    return out


def dominates(a: dict, b: dict, raw_score_evals: int) -> bool:
    """Return True if method a weakly dominates b on the frozen utility axes."""
    a_false = int(a.get("pair_metrics", {}).get("false_task_merges", 0))
    b_false = int(b.get("pair_metrics", {}).get("false_task_merges", 0))
    a_comp = float(a["compression_fraction"])
    b_comp = float(b["compression_fraction"])
    a_logdet = float(a["downstream"]["final_logdet"])
    b_logdet = float(b["downstream"]["final_logdet"])

    def be(method: dict) -> float:
        savings = raw_score_evals - int(method["downstream"]["score_evaluations"])
        work = int(method.get("structural_work", {}).get("probability_cell_uses_proxy", 0))
        return float("inf") if savings <= 0 else work / savings

    weak = (
        a_false <= b_false
        and a_comp >= b_comp - 1e-15
        and a_logdet >= b_logdet - 1e-8
        and be(a) <= be(b) + 1e-12
    )
    strict = (
        a_false < b_false
        or a_comp > b_comp + 1e-15
        or a_logdet > b_logdet + 1e-8
        or be(a) < be(b) - 1e-12
    )
    return bool(weak and strict)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v0.6.3 finite-evidence safe quotient gate")
    parser.add_argument("--out", type=Path, default=Path("evidence/v063/outputs"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    total_start = time.perf_counter()
    physical, views = build_views()
    truth = oracle_truth_matrix(views)
    split1, split2 = sample_evidence(views)
    pooled = smoothed_probability(split1 + split2, 2 * SHOTS_PER_SPLIT)
    shortlisted, shortlist_distance_evals = shortlist_pairs(pooled)

    raw_classes = [[idx] for idx in range(len(views))]
    oracle_classes = complete_link_oracle_classes(truth, views)

    raw = method_summary("RAW", raw_classes, views, truth, None, shortlisted, shortlist_distance_evals, 0.0)
    oracle = method_summary("ORACLE", oracle_classes, views, truth, None, shortlisted, shortlist_distance_evals, 0.0)

    learned: dict[str, dict] = {}
    pair_rows: list[dict] = []
    for method in ("POINT", "UCB", "OARL-XFIT"):
        start = time.perf_counter()
        relation, transport = classify_shortlist(shortlisted, split1, split2, method)
        classes = complete_link_classes(len(views), relation, views)
        elapsed = time.perf_counter() - start
        summary = method_summary(
            method, classes, views, truth, relation, shortlisted, shortlist_distance_evals, elapsed
        )
        learned[method] = summary
        for i, j in sorted(shortlisted):
            pair_rows.append(
                {
                    "method": method,
                    "i": i,
                    "j": j,
                    "status": relation[(i, j)],
                    "transport": transport[(i, j)],
                    "task_equivalent": bool(truth[i, j]),
                    "fim_relative_distance": relative_fim_distance(views[i].fim, views[j].fim),
                }
            )

    raw_score_evals = int(raw["downstream"]["score_evaluations"])
    for summary in learned.values():
        savings = raw_score_evals - int(summary["downstream"]["score_evaluations"])
        work = int(summary["structural_work"]["probability_cell_uses_proxy"])
        summary["economics"] = {
            "downstream_score_eval_savings": savings,
            "break_even_downstream_score_cost_in_probability_cell_ops": (
                None if savings <= 0 else work / savings
            ),
        }

    oarl = learned["OARL-XFIT"]
    primary_checks = {
        "zero_accepted_task_false_merges": int(oarl["pair_metrics"]["false_task_merges"]) == 0,
        "downstream_logdet_preserved": float(oarl["downstream"]["final_logdet"]) >= float(raw["downstream"]["final_logdet"]) - 1e-8,
        "selected_depth_cost_no_greater_than_raw": int(oarl["downstream"]["selected_total_depth_cost"]) <= int(raw["downstream"]["selected_total_depth_cost"]),
        "compression_ge_20pct": float(oarl["compression_fraction"]) >= 0.20,
    }
    primary_pass = all(primary_checks.values())
    dominated_by = [
        name for name in ("POINT", "UCB")
        if dominates(learned[name], oarl, raw_score_evals)
    ]
    strict_oarl_advantage = any(
        dominates(oarl, learned[name], raw_score_evals) for name in ("POINT", "UCB")
    )
    incremental_utility_observed = bool(primary_pass and not dominated_by and strict_oarl_advantage)

    summary = {
        "version": "v0.6.3-safe-quotient-gate",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "model_pack": "smq1Q_XYI",
        "physical_circuits": len(physical),
        "candidate_views": len(views),
        "mechanism_probe_count": len(views[0].exact_probe_probabilities),
        "shots_per_split": SHOTS_PER_SPLIT,
        "shortlist_neighbours": SHORTLIST_NEIGHBOURS,
        "shortlisted_pairs": len(shortlisted),
        "oracle_classes": len(oracle_classes),
        "oracle_compression_fraction": 1.0 - len(oracle_classes) / len(views),
        "raw": raw,
        "oracle": oracle,
        "learned": learned,
        "primary_checks": primary_checks,
        "primary_safety_gate_pass": primary_pass,
        "oarl_dominated_by": dominated_by,
        "oarl_strictly_dominates_any_generic_baseline": strict_oarl_advantage,
        "incremental_utility_observed": incremental_utility_observed,
        "total_runtime_s": time.perf_counter() - total_start,
        "claim_boundary": (
            "Task-relative compression before a fixed D-optimal optimizer in an external pyGSTi circuit family. "
            "Outcome relabeling supplies genuine experiment isomorphisms; Fisher/D-optimality and Blackwell/Le Cam "
            "comparison are prior art. The gate tests finite-evidence structure learning, abstention and safe quotienting."
        ),
    }

    with (args.out / "pair_predictions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pair_rows[0].keys()))
        writer.writeheader()
        writer.writerows(pair_rows)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    compact = {
        "version": summary["version"],
        "candidate_views": summary["candidate_views"],
        "oracle_classes": summary["oracle_classes"],
        "oracle_compression_fraction": summary["oracle_compression_fraction"],
        "primary_checks": primary_checks,
        "primary_safety_gate_pass": primary_pass,
        "oarl_dominated_by": dominated_by,
        "incremental_utility_observed": incremental_utility_observed,
        "methods": {
            name: {
                "n_classes": data["n_classes"],
                "compression_fraction": data["compression_fraction"],
                "false_task_merges": data.get("pair_metrics", {}).get("false_task_merges"),
                "pair_precision": data.get("pair_metrics", {}).get("pair_precision"),
                "pair_recall_global": data.get("pair_metrics", {}).get("pair_recall_global"),
                "downstream_logdet": data["downstream"]["final_logdet"],
                "downstream_score_evaluations": data["downstream"]["score_evaluations"],
                "selected_total_depth_cost": data["downstream"]["selected_total_depth_cost"],
                "break_even_score_cost": data.get("economics", {}).get("break_even_downstream_score_cost_in_probability_cell_ops"),
            }
            for name, data in {"RAW": raw, "ORACLE": oracle, **learned}.items()
        },
    }
    (args.out / "summary_compact.json").write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    print(json.dumps(compact, indent=2, sort_keys=True))

    # Scientific failure is valid output. CI failure is reserved for execution/integrity errors.


if __name__ == "__main__":
    main()
