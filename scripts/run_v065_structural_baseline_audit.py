from __future__ import annotations

import argparse
import csv
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pygsti
from pygsti.modelpacks import smq1Q_XYI as std

from oarl_bench.structural_transport import (
    GATE_X,
    GATE_Y,
    analytic_orientation_transport,
    anchor_states,
    class_false_pairs,
    decision_distance,
    doptimal_design,
    exact_fisher_signature,
    exact_relation,
    greedy_complete_link,
    operational_relation,
    relation_axioms,
    relation_components,
    relative_fisher_distance,
)


CONFIRMATORY_DEPTH = 8
DEVELOPMENT_DEPTHS = tuple(range(1, 8))
GATES = (GATE_X, GATE_Y)
PARAMETER_DIM = 3
FINITE_DIFFERENCE_STEPS = (1e-3, 1e-4, 1e-5)
LEGACY_FINITE_DIFFERENCE_STEP = 1e-4
FIM_EQ_TOL = 0.20
DECISION_EQ_TOL = 0.05
DOPT_STEPS = 8
DOPT_RIDGE = 1e-9
MAX_LOGDET_LOSS = 0.005
MIN_STRUCTURAL_COMPRESSION = 0.20
MIN_RESIDUAL_COMPRESSION = 0.20
ORDER_AUDIT_DRAWS = 256
ORDER_AUDIT_SEED = 650501
MECHANISM_PROBES = 19
V064_SHOTS_PER_SPLIT = 100_000
V064_SPLITS = 2
V064_PHYSICAL_CIRCUITS = 254
V064_CANDIDATE_VIEWS = 508


@dataclass(frozen=True)
class CircuitRow:
    index: int
    word: tuple[str, ...]
    depth: int
    label: str
    circuit: pygsti.circuits.Circuit


def circuits_for_depths(depths: tuple[int, ...]) -> list[CircuitRow]:
    rows: list[CircuitRow] = []
    for depth in depths:
        for word in itertools.product(GATES, repeat=depth):
            rows.append(
                CircuitRow(
                    index=len(rows),
                    word=tuple(word),
                    depth=depth,
                    label=".".join(word),
                    circuit=pygsti.circuits.Circuit([(gate, 0) for gate in word]),
                )
            )
    return rows


def success_probability(model, circuit: pygsti.circuits.Circuit) -> float:
    probabilities = model.probabilities(circuit)
    outcome = sorted(probabilities, key=str)[0]
    value = float(probabilities[outcome])
    if not np.isfinite(value) or value < -1e-10 or value > 1.0 + 1e-10:
        raise ValueError(f"invalid probability {value} for {circuit}")
    return float(np.clip(value, 0.0, 1.0))


def rotated_model(axis: int, amount: float):
    rotation = [0.0, 0.0, 0.0]
    rotation[axis] = float(amount)
    return std.target_model().rotate(rotate=tuple(rotation))


def analytic_fisher_family(
    circuits: list[CircuitRow],
) -> tuple[np.ndarray, list[tuple[int, ...]], np.ndarray, np.ndarray]:
    probabilities: list[float] = []
    gradients: list[np.ndarray] = []
    fishers: list[np.ndarray] = []
    signatures: list[tuple[int, ...]] = []
    for row in circuits:
        probability, gradient, fisher = analytic_orientation_transport(row.word)
        probabilities.append(probability)
        gradients.append(gradient)
        fishers.append(fisher)
        signatures.append(exact_fisher_signature(fisher))
    return (
        np.asarray(fishers, dtype=float),
        signatures,
        np.asarray(probabilities, dtype=float),
        np.asarray(gradients, dtype=float),
    )


def pygsti_fisher_family(
    circuits: list[CircuitRow],
    finite_difference_step: float,
) -> np.ndarray:
    target = std.target_model()
    plus = [rotated_model(axis, finite_difference_step) for axis in range(PARAMETER_DIM)]
    minus = [rotated_model(axis, -finite_difference_step) for axis in range(PARAMETER_DIM)]
    fishers = np.empty((len(circuits), PARAMETER_DIM, PARAMETER_DIM), dtype=float)

    for row in circuits:
        probability = success_probability(target, row.circuit)
        gradient = np.asarray(
            [
                (
                    success_probability(plus[axis], row.circuit)
                    - success_probability(minus[axis], row.circuit)
                )
                / (2.0 * finite_difference_step)
                for axis in range(PARAMETER_DIM)
            ],
            dtype=float,
        )
        variance = max(probability * (1.0 - probability), 1e-8)
        fisher = np.outer(gradient, gradient) / variance
        fishers[row.index] = 0.5 * (fisher + fisher.T)
    return fishers


def upper_pair_count(relation: np.ndarray) -> int:
    return int(np.sum(np.triu(np.asarray(relation, dtype=bool), 1)))


def compare_relations(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> dict[str, int]:
    upper = np.triu(np.ones(reference.shape, dtype=bool), 1)
    missed = reference & ~candidate & upper
    added = ~reference & candidate & upper
    return {
        "reference_pairs": int(np.sum(reference & upper)),
        "candidate_pairs": int(np.sum(candidate & upper)),
        "reference_pairs_missed": int(np.sum(missed)),
        "candidate_only_pairs": int(np.sum(added)),
        "pair_disagreements": int(np.sum(missed) + np.sum(added)),
    }


def numerical_audit(
    circuits: list[CircuitRow],
    analytic_fishers: np.ndarray,
    analytic_operational_relation: np.ndarray,
    anchors: np.ndarray,
) -> tuple[list[dict[str, float | int]], dict[float, np.ndarray]]:
    rows: list[dict[str, float | int]] = []
    matrices_by_step: dict[float, np.ndarray] = {}
    analytic_norms = np.linalg.norm(analytic_fishers, axis=(1, 2))
    nonzero = analytic_norms > 1e-9
    zero = ~nonzero

    for step in FINITE_DIFFERENCE_STEPS:
        numerical = pygsti_fisher_family(circuits, step)
        matrices_by_step[step] = numerical
        errors = np.linalg.norm(numerical - analytic_fishers, axis=(1, 2))
        numerical_norms = np.linalg.norm(numerical, axis=(1, 2))
        relative = errors[nonzero] / analytic_norms[nonzero]
        finite_relation, _, _ = operational_relation(
            numerical,
            anchors,
            FIM_EQ_TOL,
            DECISION_EQ_TOL,
        )
        comparison = compare_relations(analytic_operational_relation, finite_relation)
        rows.append(
            {
                "finite_difference_step": float(step),
                "median_absolute_fisher_error": float(np.median(errors)),
                "max_absolute_fisher_error": float(np.max(errors)),
                "median_relative_error_nonzero": float(np.median(relative)),
                "max_relative_error_nonzero": float(np.max(relative)),
                "analytic_zero_fisher_circuits": int(np.sum(zero)),
                "max_numerical_norm_on_analytic_zero": float(
                    np.max(numerical_norms[zero]) if np.any(zero) else 0.0
                ),
                **comparison,
            }
        )
    return rows, matrices_by_step


def order_dependence_audit(
    relation: np.ndarray,
    fishers: np.ndarray,
    labels: list[str],
    depths: list[int],
) -> dict[str, object]:
    rng = np.random.default_rng(ORDER_AUDIT_SEED)
    class_counts: list[int] = []
    logdets: list[float] = []
    depth_costs: list[int] = []

    orders = [list(range(len(labels)))]
    orders.extend(
        rng.permutation(len(labels)).astype(int).tolist()
        for _ in range(ORDER_AUDIT_DRAWS)
    )
    for order in orders:
        classes = greedy_complete_link(relation, order)
        design = doptimal_design(
            classes,
            fishers,
            labels,
            depths,
            DOPT_STEPS,
            DOPT_RIDGE,
        )
        class_counts.append(len(classes))
        logdets.append(float(design["logdet"]))
        depth_costs.append(int(design["selected_total_depth_cost"]))

    return {
        "orders_evaluated": len(orders),
        "class_count_min": min(class_counts),
        "class_count_max": max(class_counts),
        "class_count_unique": sorted(set(class_counts)),
        "logdet_min": min(logdets),
        "logdet_max": max(logdets),
        "logdet_span": max(logdets) - min(logdets),
        "depth_cost_min": min(depth_costs),
        "depth_cost_max": max(depth_costs),
    }


def method_row(
    classes: list[list[int]],
    fishers: np.ndarray,
    labels: list[str],
    depths: list[int],
    raw_view_count: int,
    physical_count: int,
    exact_truth: np.ndarray | None,
    operational_truth: np.ndarray | None,
) -> dict[str, object]:
    design = doptimal_design(
        classes,
        fishers,
        labels,
        depths,
        DOPT_STEPS,
        DOPT_RIDGE,
    )
    n_classes = len(classes)
    physical_compression = (
        float(1.0 - n_classes / physical_count)
        if fishers.shape[0] == physical_count
        else None
    )
    return {
        "n_classes": n_classes,
        "view_level_compression_fraction": float(1.0 - n_classes / raw_view_count),
        "compression_beyond_view_canonicalization": physical_compression,
        "exact_false_merges": (
            class_false_pairs(classes, exact_truth) if exact_truth is not None else None
        ),
        "operational_false_merges": (
            class_false_pairs(classes, operational_truth)
            if operational_truth is not None
            else None
        ),
        "bernoulli_evidence_shots": 0,
        **design,
    }


def development_correction_audit(anchors: np.ndarray) -> dict[str, object]:
    circuits = circuits_for_depths(DEVELOPMENT_DEPTHS)
    analytic, signatures, _, _ = analytic_fisher_family(circuits)
    exact = exact_relation(signatures)
    analytic_operational, _, _ = operational_relation(
        analytic,
        anchors,
        FIM_EQ_TOL,
        DECISION_EQ_TOL,
    )
    numerical = pygsti_fisher_family(circuits, LEGACY_FINITE_DIFFERENCE_STEP)
    numerical_operational, _, _ = operational_relation(
        numerical,
        anchors,
        FIM_EQ_TOL,
        DECISION_EQ_TOL,
    )

    exact_classes = relation_components(exact)
    analytic_operational_audit = relation_axioms(analytic_operational)
    numerical_operational_audit = relation_axioms(numerical_operational)
    analytic_operational_classes = (
        relation_components(analytic_operational)
        if bool(analytic_operational_audit["transitive"])
        else None
    )
    numerical_operational_classes = (
        relation_components(numerical_operational)
        if bool(numerical_operational_audit["transitive"])
        else None
    )

    exact_vs_numerical = compare_relations(exact, numerical_operational)
    analytic_vs_numerical = compare_relations(
        analytic_operational,
        numerical_operational,
    )
    nominal_shots = (
        V064_CANDIDATE_VIEWS
        * MECHANISM_PROBES
        * V064_SPLITS
        * V064_SHOTS_PER_SPLIT
    )
    shared_physical_shots = (
        V064_PHYSICAL_CIRCUITS
        * MECHANISM_PROBES
        * V064_SPLITS
        * V064_SHOTS_PER_SPLIT
    )

    return {
        "physical_circuits": len(circuits),
        "raw_views": 2 * len(circuits),
        "analytic_exact_classes": len(exact_classes),
        "analytic_operational_classes": (
            len(analytic_operational_classes)
            if analytic_operational_classes is not None
            else None
        ),
        "legacy_fd_operational_classes": (
            len(numerical_operational_classes)
            if numerical_operational_classes is not None
            else None
        ),
        "exact_relation_axioms": relation_axioms(exact),
        "analytic_operational_relation_axioms": analytic_operational_audit,
        "legacy_fd_operational_relation_axioms": numerical_operational_audit,
        "analytic_exact_vs_legacy_fd_operational": exact_vs_numerical,
        "analytic_operational_vs_legacy_fd_operational": analytic_vs_numerical,
        "v064_nominal_view_shot_units": nominal_shots,
        "v064_shared_physical_shot_units": shared_physical_shots,
        "view_accounting_overstatement_factor": float(
            nominal_shots / shared_physical_shots
        ),
    }


def main() -> None:
    started = time.perf_counter()
    parser = argparse.ArgumentParser(
        description="Run OARL v0.6.5 structural-baseline and evaluator audit"
    )
    parser.add_argument("--out", type=Path, default=Path("evidence/v065/outputs"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    circuits = circuits_for_depths((CONFIRMATORY_DEPTH,))
    labels = [row.label for row in circuits]
    depths = [row.depth for row in circuits]
    physical_count = len(circuits)
    raw_view_count = 2 * physical_count
    anchors = anchor_states()

    analytic_fishers, signatures, probabilities, gradients = analytic_fisher_family(circuits)
    exact = exact_relation(signatures)
    exact_audit = relation_axioms(exact)
    exact_classes = relation_components(exact)

    operational, fisher_distances, decision_distances = operational_relation(
        analytic_fishers,
        anchors,
        FIM_EQ_TOL,
        DECISION_EQ_TOL,
    )
    operational_audit = relation_axioms(operational)
    operational_classes = (
        relation_components(operational)
        if all(
            bool(operational_audit[name])
            for name in ("reflexive", "symmetric", "transitive")
        )
        else None
    )

    numerical_rows, numerical_matrices = numerical_audit(
        circuits,
        analytic_fishers,
        operational,
        anchors,
    )
    order_audit = order_dependence_audit(
        operational,
        analytic_fishers,
        labels,
        depths,
    )

    raw_fishers = np.repeat(analytic_fishers, 2, axis=0)
    raw_labels = [
        f"{row.label}|{convention}"
        for row in circuits
        for convention in ("ordinary", "complement")
    ]
    raw_depths = [row.depth for row in circuits for _ in range(2)]
    raw_classes = [[index] for index in range(raw_view_count)]
    view_canonical_classes = [[index] for index in range(physical_count)]

    methods: dict[str, dict[str, object]] = {
        "RAW-VIEWS": method_row(
            raw_classes,
            raw_fishers,
            raw_labels,
            raw_depths,
            raw_view_count,
            physical_count,
            None,
            None,
        ),
        "VIEW-CANONICAL": method_row(
            view_canonical_classes,
            analytic_fishers,
            labels,
            depths,
            raw_view_count,
            physical_count,
            exact,
            operational,
        ),
        "STRUCTURAL-TRANSPORT": method_row(
            exact_classes,
            analytic_fishers,
            labels,
            depths,
            raw_view_count,
            physical_count,
            exact,
            operational,
        ),
    }
    if operational_classes is not None:
        methods["OPERATIONAL-ORACLE"] = method_row(
            operational_classes,
            analytic_fishers,
            labels,
            depths,
            raw_view_count,
            physical_count,
            exact,
            operational,
        )

    view_baseline = methods["VIEW-CANONICAL"]
    structural = methods["STRUCTURAL-TRANSPORT"]
    structural_logdet_loss = float(view_baseline["logdet"] - structural["logdet"])
    structural_checks = {
        "zero_exact_false_merges": structural["exact_false_merges"] == 0,
        "compression_beyond_view_canonicalization_ge_20pct": (
            float(structural["compression_beyond_view_canonicalization"])
            >= MIN_STRUCTURAL_COMPRESSION
        ),
        "downstream_logdet_preserved": structural_logdet_loss <= MAX_LOGDET_LOSS,
        "selected_depth_cost_no_greater": (
            int(structural["selected_total_depth_cost"])
            <= int(view_baseline["selected_total_depth_cost"])
        ),
        "zero_bernoulli_evidence": structural["bernoulli_evidence_shots"] == 0,
    }
    structural_pass = all(structural_checks.values())

    if operational_classes is not None:
        oracle = methods["OPERATIONAL-ORACLE"]
        residual_compression = float(
            1.0 - int(oracle["n_classes"]) / int(structural["n_classes"])
        )
        oracle_logdet_loss = float(view_baseline["logdet"] - oracle["logdet"])
        learned_suitability_checks = {
            "operational_relation_is_equivalence": True,
            "operational_oracle_preserves_downstream": (
                oracle_logdet_loss <= MAX_LOGDET_LOSS
            ),
            "residual_compression_beyond_structural_ge_20pct": (
                residual_compression >= MIN_RESIDUAL_COMPRESSION
            ),
        }
    else:
        residual_compression = None
        oracle_logdet_loss = None
        learned_suitability_checks = {
            "operational_relation_is_equivalence": False,
            "operational_oracle_preserves_downstream": False,
            "residual_compression_beyond_structural_ge_20pct": False,
        }
    learned_suitability_pass = all(learned_suitability_checks.values())

    development_audit = development_correction_audit(anchors)

    class_payload = {
        "STRUCTURAL-TRANSPORT": [
            [labels[index] for index in group] for group in exact_classes
        ],
        "OPERATIONAL-ORACLE": (
            [[labels[index] for index in group] for group in operational_classes]
            if operational_classes is not None
            else None
        ),
    }
    (args.out / "classes.json").write_text(
        json.dumps(class_payload, indent=2, sort_keys=True) + "\n"
    )

    with (args.out / "numerical_audit.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(numerical_rows[0].keys()))
        writer.writeheader()
        writer.writerows(numerical_rows)

    structural_state_updates = physical_count * CONFIRMATORY_DEPTH
    structural_derivative_updates = PARAMETER_DIM * structural_state_updates
    summary = {
        "version": "v0.6.5-structural-baseline-audit",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "model_pack": "smq1Q_XYI",
        "development_depths": list(DEVELOPMENT_DEPTHS),
        "confirmatory_depth": CONFIRMATORY_DEPTH,
        "physical_circuits": physical_count,
        "raw_candidate_views": raw_view_count,
        "known_outcome_conventions": 2,
        "task_thresholds": {
            "fisher_equivalence": FIM_EQ_TOL,
            "decision_equivalence": DECISION_EQ_TOL,
            "max_logdet_loss": MAX_LOGDET_LOSS,
        },
        "analytic_probability_values": sorted(set(probabilities.tolist())),
        "analytic_gradient_values": sorted(set(gradients.ravel().tolist())),
        "exact_equivalent_pairs": upper_pair_count(exact),
        "operational_compatible_pairs": upper_pair_count(operational),
        "exact_relation_axioms": exact_audit,
        "operational_relation_axioms": operational_audit,
        "operational_max_fisher_distance_inside_relation": float(
            np.max(fisher_distances[operational])
        ),
        "operational_max_decision_distance_inside_relation": float(
            np.max(decision_distances[operational])
        ),
        "order_dependence_audit": order_audit,
        "numerical_audit": numerical_rows,
        "methods": methods,
        "structural_work": {
            "state_transport_updates": structural_state_updates,
            "derivative_transport_updates": structural_derivative_updates,
            "total_vector_updates": (
                structural_state_updates + structural_derivative_updates
            ),
            "bernoulli_evidence_shots": 0,
        },
        "structural_baseline_checks": structural_checks,
        "structural_baseline_utility_pass": structural_pass,
        "residual_operational_compression_beyond_structural": residual_compression,
        "operational_oracle_logdet_loss_vs_view_canonical": oracle_logdet_loss,
        "learned_discovery_suitability_checks": learned_suitability_checks,
        "learned_discovery_suitability_pass": learned_suitability_pass,
        "adaptive_stage_status": (
            "WARRANTED_BUT_REQUIRES_SEPARATE_PREREGISTRATION"
            if learned_suitability_pass
            else "NOT_WARRANTED_ON_THIS_FAMILY"
        ),
        "oarl_specific_utility_observed": False,
        "development_v064_correction_audit": development_audit,
        "runtime_s": float(time.perf_counter() - started),
        "claim_boundary": (
            "Prospective held-out-depth audit of known structural transport and "
            "legacy evaluator stability. Structural/Fisher canonicalization is "
            "prior art; no OARL-specific learned-discovery advantage is claimed."
        ),
    }

    compact_methods = {
        name: {
            "n_classes": row["n_classes"],
            "view_level_compression_fraction": row[
                "view_level_compression_fraction"
            ],
            "compression_beyond_view_canonicalization": row[
                "compression_beyond_view_canonicalization"
            ],
            "exact_false_merges": row["exact_false_merges"],
            "operational_false_merges": row["operational_false_merges"],
            "logdet": row["logdet"],
            "score_evaluations": row["score_evaluations"],
            "selected_total_depth_cost": row["selected_total_depth_cost"],
            "bernoulli_evidence_shots": row["bernoulli_evidence_shots"],
        }
        for name, row in methods.items()
    }
    compact = {
        "version": summary["version"],
        "confirmatory_depth": CONFIRMATORY_DEPTH,
        "physical_circuits": physical_count,
        "raw_candidate_views": raw_view_count,
        "exact_equivalent_pairs": summary["exact_equivalent_pairs"],
        "operational_compatible_pairs": summary["operational_compatible_pairs"],
        "exact_relation_axioms": exact_audit,
        "operational_relation_axioms": operational_audit,
        "methods": compact_methods,
        "structural_baseline_checks": structural_checks,
        "structural_baseline_utility_pass": structural_pass,
        "residual_operational_compression_beyond_structural": residual_compression,
        "learned_discovery_suitability_checks": learned_suitability_checks,
        "learned_discovery_suitability_pass": learned_suitability_pass,
        "adaptive_stage_status": summary["adaptive_stage_status"],
        "oarl_specific_utility_observed": False,
        "development_v064_correction_audit": development_audit,
    }
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (args.out / "summary_compact.json").write_text(
        json.dumps(compact, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
