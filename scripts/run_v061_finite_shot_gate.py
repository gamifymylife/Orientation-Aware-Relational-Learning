from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pygsti
from pygsti.modelpacks import smq1Q_XYI as std
from pygsti.models.gaugegroup import FullGaugeGroupElement


GATES = ("Gxpi2", "Gypi2")
OP_NOISE_LEVELS = (0.002, 0.005, 0.010, 0.020, 0.030, 0.050, 0.080)
SHOT_BUDGETS = (50_000, 100_000, 250_000, 500_000)
SEEDS = range(1000, 1300)
EPSILON = 0.020
ALPHA = 0.01
RAW_DISTANCE_THRESHOLD = 0.10
DEPTH_SLOPE_LIMIT = EPSILON / 10.0


def circuits_of_lengths(lengths: range) -> tuple[list[pygsti.circuits.Circuit], np.ndarray]:
    circuits: list[pygsti.circuits.Circuit] = []
    depths: list[int] = []
    for length in lengths:
        if length == 0:
            circuits.append(pygsti.circuits.Circuit([]))
            depths.append(0)
            continue
        for sequence in itertools.product(GATES, repeat=length):
            circuits.append(pygsti.circuits.Circuit([(gate, 0) for gate in sequence]))
            depths.append(length)
    return circuits, np.asarray(depths, dtype=int)


def success_probability_vector(model, circuits: list[pygsti.circuits.Circuit]) -> np.ndarray:
    values: list[float] = []
    for circuit in circuits:
        probs = model.probabilities(circuit)
        outcome = sorted(probs, key=str)[0]
        values.append(float(probs[outcome]))
    vector = np.asarray(values, dtype=float)
    # pyGSTi may return ideal probabilities a few ulps outside [0, 1]. Preserve
    # the scientific model but remove numerical roundoff before binomial draws.
    if float(np.min(vector)) < -1e-10 or float(np.max(vector)) > 1.0 + 1e-10:
        raise ValueError("model produced materially invalid circuit probabilities")
    return np.clip(vector, 0.0, 1.0)


def random_gauge_matrix(rng: np.random.Generator) -> np.ndarray:
    for _ in range(100):
        matrix = np.eye(4)
        matrix[1:, 1:] += rng.normal(scale=0.08, size=(3, 3))
        matrix[1:, 0] += rng.normal(scale=0.03, size=3)
        if abs(np.linalg.det(matrix)) > 0.2 and np.linalg.cond(matrix) < 5.0:
            return matrix
    raise RuntimeError("failed to draw a stable invertible gauge matrix")


def gauge_copy(model, rng: np.random.Generator):
    transformed = model.copy()
    transformed.transform_inplace(FullGaugeGroupElement(random_gauge_matrix(rng)))
    return transformed


def simultaneous_bounds(
    counts_a: np.ndarray,
    counts_b: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pa = counts_a.astype(float) / n
    pb = counts_b.astype(float) / n
    diff = np.abs(pa - pb)
    se = np.sqrt(
        np.maximum(pa * (1.0 - pa), 0.0) / n
        + np.maximum(pb * (1.0 - pb), 0.0) / n
    )
    z = NormalDist().inv_cdf(1.0 - ALPHA / (2.0 * len(diff)))
    upper = diff + z * se
    lower = np.maximum(diff - z * se, 0.0)
    return diff, lower, upper


def classify_generic(
    counts_a: np.ndarray,
    counts_b: np.ndarray,
    n: int,
) -> str:
    _, lower, upper = simultaneous_bounds(counts_a, counts_b, n)
    if np.all(upper <= EPSILON):
        return "EQUIVALENT"
    if np.any(lower > EPSILON):
        return "DISTINCT"
    return "UNKNOWN"


def depth_slope(
    counts_a: np.ndarray,
    counts_b: np.ndarray,
    n: int,
    depths: np.ndarray,
) -> float:
    pa = counts_a.astype(float) / n
    pb = counts_b.astype(float) / n
    abs_diff = np.abs(pa - pb)
    means = np.asarray(
        [float(np.mean(abs_diff[depths == depth])) for depth in range(4)],
        dtype=float,
    )
    return float(np.polyfit(np.arange(4, dtype=float), means, 1)[0])


def classify_oarl(
    a1: np.ndarray,
    b1: np.ndarray,
    a2: np.ndarray,
    b2: np.ndarray,
    n_half: int,
    depths: np.ndarray,
) -> tuple[str, float, float]:
    full_a = a1 + a2
    full_b = b1 + b2
    _, lower_full, _ = simultaneous_bounds(full_a, full_b, 2 * n_half)
    if np.any(lower_full > EPSILON):
        return "DISTINCT", float("nan"), float("nan")

    _, _, upper1 = simultaneous_bounds(a1, b1, n_half)
    _, _, upper2 = simultaneous_bounds(a2, b2, n_half)
    slope1 = depth_slope(a1, b1, n_half, depths)
    slope2 = depth_slope(a2, b2, n_half, depths)

    equivalent = (
        np.all(upper1 <= EPSILON)
        and np.all(upper2 <= EPSILON)
        and slope1 <= DEPTH_SLOPE_LIMIT
        and slope2 <= DEPTH_SLOPE_LIMIT
    )
    if equivalent:
        return "EQUIVALENT", slope1, slope2
    return "UNKNOWN", slope1, slope2


def sample_pair(
    rng: np.random.Generator,
    p_a: np.ndarray,
    p_b: np.ndarray,
    budget: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_half = budget // 2
    a1 = rng.binomial(n_half, p_a)
    b1 = rng.binomial(n_half, p_b)
    a2 = rng.binomial(n_half, p_a)
    b2 = rng.binomial(n_half, p_b)
    return a1, b1, a2, b2


def classification_metrics(rows: list[dict], method: str) -> dict:
    pred_key = f"{method}_prediction"
    tp = fp = fn = tn = unknown = accepted = 0
    physical_false_merges = 0
    for row in rows:
        truth = bool(row["operational_equivalent"])
        pred = row[pred_key]
        if pred == "UNKNOWN":
            unknown += 1
        elif pred == "EQUIVALENT":
            accepted += 1
            if truth:
                tp += 1
            else:
                fp += 1
            if not bool(row["physical_equivalent"]):
                physical_false_merges += 1
        else:
            if truth:
                fn += 1
            else:
                tn += 1
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn + sum(
        1 for row in rows
        if bool(row["operational_equivalent"]) and row[pred_key] == "UNKNOWN"
    ))
    return {
        "tp_equivalent": tp,
        "fp_operational_false_merge": fp,
        "fn_equivalent_called_distinct": fn,
        "tn_distinct": tn,
        "unknown": unknown,
        "accepted_equivalent": accepted,
        "physical_false_merges": physical_false_merges,
        "operational_precision": precision,
        "operational_recall": recall,
        "abstention_rate": unknown / len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v0.6.1 finite-shot competitive external gate")
    parser.add_argument("--out", type=Path, default=Path("evidence/v061/finite_shot_outputs"))
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--seed-end", type=int, default=1299)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    discovery, depths = circuits_of_lengths(range(0, 4))
    sealed, _ = circuits_of_lengths(range(4, 7))
    target = std.target_model()

    target_discovery = success_probability_vector(target, discovery)
    target_sealed = success_probability_vector(target, sealed)

    physical_models = {
        noise: target.depolarize(op_noise=noise, spam_noise=0.0)
        for noise in OP_NOISE_LEVELS
    }
    physical_discovery = {
        noise: success_probability_vector(model, discovery)
        for noise, model in physical_models.items()
    }
    physical_sealed = {
        noise: success_probability_vector(model, sealed)
        for noise, model in physical_models.items()
    }

    sealed_differences = {
        str(noise): float(np.max(np.abs(target_sealed - physical_sealed[noise])))
        for noise in OP_NOISE_LEVELS
    }

    rows: list[dict] = []
    for seed in range(args.seed_start, args.seed_end + 1):
        gauge_rng = np.random.default_rng(seed * 1009 + 17)
        target_left = gauge_copy(target, gauge_rng)
        target_right = gauge_copy(target, gauge_rng)
        eq_raw_distance = float(np.linalg.norm(
            np.asarray(target_left.to_vector(), dtype=float)
            - np.asarray(target_right.to_vector(), dtype=float)
        ))

        cases = [{
            "case": "gauge",
            "op_noise": 0.0,
            "p_b": target_discovery,
            "sealed_max_abs": 0.0,
            "physical_equivalent": True,
            "raw_distance": eq_raw_distance,
        }]

        for noise in OP_NOISE_LEVELS:
            left = gauge_copy(target, gauge_rng)
            right = gauge_copy(physical_models[noise], gauge_rng)
            raw_distance = float(np.linalg.norm(
                np.asarray(left.to_vector(), dtype=float)
                - np.asarray(right.to_vector(), dtype=float)
            ))
            cases.append({
                "case": "physical",
                "op_noise": noise,
                "p_b": physical_discovery[noise],
                "sealed_max_abs": sealed_differences[str(noise)],
                "physical_equivalent": False,
                "raw_distance": raw_distance,
            })

        for case_index, case in enumerate(cases):
            operational_equivalent = bool(case["sealed_max_abs"] <= EPSILON)
            for budget in SHOT_BUDGETS:
                sample_rng = np.random.default_rng(
                    seed * 1_000_003 + case_index * 10_007 + budget
                )
                a1, b1, a2, b2 = sample_pair(
                    sample_rng, target_discovery, case["p_b"], budget
                )
                full_a = a1 + a2
                full_b = b1 + b2
                generic = classify_generic(full_a, full_b, budget)
                oarl, slope1, slope2 = classify_oarl(
                    a1, b1, a2, b2, budget // 2, depths
                )
                raw_prediction = (
                    "EQUIVALENT"
                    if case["raw_distance"] <= RAW_DISTANCE_THRESHOLD
                    else "DISTINCT"
                )
                rows.append({
                    "seed": seed,
                    "case": case["case"],
                    "op_noise": case["op_noise"],
                    "shot_budget": budget,
                    "physical_equivalent": case["physical_equivalent"],
                    "operational_equivalent": operational_equivalent,
                    "sealed_max_abs": case["sealed_max_abs"],
                    "raw_distance": case["raw_distance"],
                    "raw_prediction": raw_prediction,
                    "generic_prediction": generic,
                    "oarl_prediction": oarl,
                    "oarl_depth_slope_split1": slope1,
                    "oarl_depth_slope_split2": slope2,
                })

    methods = ("raw", "generic", "oarl")
    aggregate = {method: classification_metrics(rows, method) for method in methods}
    by_budget = {}
    for budget in SHOT_BUDGETS:
        subset = [row for row in rows if row["shot_budget"] == budget]
        by_budget[str(budget)] = {
            method: classification_metrics(subset, method) for method in methods
        }

    oarl_metrics = aggregate["oarl"]
    generic_metrics = aggregate["generic"]
    both_accept_enough = any(
        by_budget[str(b)]["oarl"]["tp_equivalent"] >= 25
        and by_budget[str(b)]["generic"]["tp_equivalent"] >= 25
        for b in SHOT_BUDGETS
    )
    strict_precision_gain = any(
        by_budget[str(b)]["oarl"]["tp_equivalent"] >= 25
        and by_budget[str(b)]["generic"]["tp_equivalent"] >= 25
        and (by_budget[str(b)]["oarl"]["operational_precision"] or 0.0)
            > (by_budget[str(b)]["generic"]["operational_precision"] or 0.0)
        for b in SHOT_BUDGETS
    )
    checks = {
        "oarl_zero_operational_false_merges": oarl_metrics["fp_operational_false_merge"] == 0,
        "oarl_operational_recall_ge_0_20": (oarl_metrics["operational_recall"] or 0.0) >= 0.20,
        "oarl_all_accepted_respect_sealed_epsilon": oarl_metrics["fp_operational_false_merge"] == 0,
        "competitive_advantage_observed": (
            generic_metrics["fp_operational_false_merge"] > 0 or strict_precision_gain
        ),
        "competitive_comparison_has_accepts": both_accept_enough,
    }
    gate_pass = all(checks.values())

    summary = {
        "version": "v0.6.1-finite-shot",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "seed_range": [args.seed_start, args.seed_end],
        "n_rows": len(rows),
        "shot_budgets": list(SHOT_BUDGETS),
        "epsilon": EPSILON,
        "alpha": ALPHA,
        "depth_slope_limit": DEPTH_SLOPE_LIMIT,
        "discovery_circuits": len(discovery),
        "sealed_circuits": len(sealed),
        "sealed_max_abs_by_op_noise": sealed_differences,
        "aggregate": aggregate,
        "by_budget": by_budget,
        "checks": checks,
        "gate_pass": gate_pass,
        "claim_boundary": (
            "Operational epsilon-equivalence under finite-shot shallow-circuit evidence; "
            "not proof of physical identity or a new GST result."
        ),
    }

    fieldnames = list(rows[0].keys())
    with (args.out / "classifications.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))

    # A failed scientific gate is a valid result. Do not make the workflow fail merely
    # because the competitive hypothesis was falsified; CI failure is reserved for
    # execution/integrity failures. The JSON gate_pass field carries the science result.


if __name__ == "__main__":
    main()
