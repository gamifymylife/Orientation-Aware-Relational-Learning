from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pygsti
from pygsti.modelpacks import smq1Q_XYI as std


GATES = ("Gxpi2", "Gypi2")
ROTATION_STEP = 1e-4
VARIANCE_FLOOR = 1e-9
RANK_REL_TOL = 1e-9
RANK_ABS_TOL = 1e-12
DOPT_RIDGE = 1e-9
RANDOM_SEED = 6202
MAX_DEPTH = 6
PARAMETER_DIM = 3


@dataclass(frozen=True)
class Probe:
    index: int
    circuit: pygsti.circuits.Circuit
    depth: int
    label: str
    probability: float
    sensitivity: np.ndarray
    weighted_sensitivity: np.ndarray
    information: np.ndarray


def circuits_of_depths(min_depth: int, max_depth: int) -> list[tuple[pygsti.circuits.Circuit, int, str]]:
    rows: list[tuple[pygsti.circuits.Circuit, int, str]] = []
    for depth in range(min_depth, max_depth + 1):
        for sequence in itertools.product(GATES, repeat=depth):
            circuit = pygsti.circuits.Circuit([(gate, 0) for gate in sequence])
            rows.append((circuit, depth, ".".join(sequence)))
    return rows


def success_probability(model, circuit: pygsti.circuits.Circuit) -> float:
    probs = model.probabilities(circuit)
    outcome = sorted(probs, key=str)[0]
    value = float(probs[outcome])
    if value < -1e-10 or value > 1.0 + 1e-10 or not np.isfinite(value):
        raise ValueError(f"invalid pyGSTi probability {value} for {circuit}")
    return float(np.clip(value, 0.0, 1.0))


def rotated_model(axis: int, amount: float):
    rotation = [0.0, 0.0, 0.0]
    rotation[axis] = float(amount)
    return std.target_model().rotate(rotate=tuple(rotation))


def build_probes() -> list[Probe]:
    target = std.target_model()
    plus_models = [rotated_model(axis, ROTATION_STEP) for axis in range(PARAMETER_DIM)]
    minus_models = [rotated_model(axis, -ROTATION_STEP) for axis in range(PARAMETER_DIM)]

    probes: list[Probe] = []
    for index, (circuit, depth, label) in enumerate(circuits_of_depths(1, MAX_DEPTH)):
        p = success_probability(target, circuit)
        sensitivity = np.asarray(
            [
                (success_probability(plus_models[axis], circuit) - success_probability(minus_models[axis], circuit))
                / (2.0 * ROTATION_STEP)
                for axis in range(PARAMETER_DIM)
            ],
            dtype=float,
        )
        variance = max(p * (1.0 - p), VARIANCE_FLOOR)
        weighted = sensitivity / np.sqrt(variance)
        information = np.outer(weighted, weighted)
        probes.append(
            Probe(
                index=index,
                circuit=circuit,
                depth=depth,
                label=label,
                probability=p,
                sensitivity=sensitivity,
                weighted_sensitivity=weighted,
                information=information,
            )
        )
    return probes


def fim_from_indices(probes: list[Probe], indices: list[int]) -> np.ndarray:
    fim = np.zeros((PARAMETER_DIM, PARAMETER_DIM), dtype=float)
    for index in indices:
        fim += probes[index].information
    return 0.5 * (fim + fim.T)


def eigensystem(fim: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, int]:
    values, vectors = np.linalg.eigh(0.5 * (fim + fim.T))
    max_eig = max(float(np.max(values)), 0.0)
    threshold = max(RANK_ABS_TOL, RANK_REL_TOL * max_eig)
    rank = int(np.sum(values > threshold))
    return values, vectors, threshold, rank


def matrix_metrics(fim: np.ndarray) -> dict[str, float | int | None]:
    values, _, threshold, rank = eigensystem(fim)
    positive = values[values > threshold]
    if positive.size:
        min_positive = float(np.min(positive))
        max_positive = float(np.max(positive))
        condition = float(max_positive / min_positive)
    else:
        min_positive = None
        condition = None
    return {
        "rank": rank,
        "nullity": PARAMETER_DIM - rank,
        "eigenvalues": [float(x) for x in values],
        "rank_threshold": threshold,
        "min_positive_eigenvalue": min_positive,
        "min_eigenvalue": float(np.min(values)),
        "max_eigenvalue": float(np.max(values)),
        "condition_positive": condition,
    }


def nullspace_projector(fim: np.ndarray) -> np.ndarray:
    values, vectors, threshold, _ = eigensystem(fim)
    mask = values <= threshold
    if not np.any(mask):
        return np.zeros_like(fim)
    basis = vectors[:, mask]
    return basis @ basis.T


def safe_logdet(fim: np.ndarray) -> float:
    sign, value = np.linalg.slogdet(fim + DOPT_RIDGE * np.eye(PARAMETER_DIM))
    if sign <= 0:
        raise ValueError("regularized information matrix has non-positive determinant")
    return float(value)


def candidate_cosine_novelty(probe: Probe, selected: list[Probe]) -> float:
    vector = probe.weighted_sensitivity
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-15:
        return 0.0
    unit = vector / norm
    existing_units = []
    for chosen in selected:
        chosen_norm = float(np.linalg.norm(chosen.weighted_sensitivity))
        if chosen_norm > 1e-15:
            existing_units.append(chosen.weighted_sensitivity / chosen_norm)
    if not existing_units:
        return 1.0
    max_abs_cos = max(abs(float(np.dot(unit, other))) for other in existing_units)
    return float(max(0.0, 1.0 - max_abs_cos))


def select_greedy(probes: list[Probe], policy: str) -> dict:
    initial = [probe.index for probe in probes if probe.depth == 1]
    candidates = [probe.index for probe in probes if probe.depth >= 2]
    selected = list(initial)
    added: list[int] = []
    rng = np.random.default_rng(RANDOM_SEED)

    while candidates:
        fim = fim_from_indices(probes, selected)
        current_metrics = matrix_metrics(fim)
        if int(current_metrics["rank"]) >= PARAMETER_DIM:
            break

        if policy == "random_new_view":
            choice = int(rng.choice(candidates))
        else:
            projector = nullspace_projector(fim)
            current_logdet = safe_logdet(fim)
            current_min = float(np.min(np.linalg.eigvalsh(fim)))
            scored: list[tuple[tuple[float, ...], int]] = []
            selected_probes = [probes[index] for index in selected]

            for index in candidates:
                probe = probes[index]
                new_fim = fim + probe.information
                new_rank = int(matrix_metrics(new_fim)["rank"])
                rank_gain = float(new_rank - int(current_metrics["rank"]))
                cost = float(probe.depth)

                if policy == "nullspace_coverage":
                    projected = projector @ probe.weighted_sensitivity
                    projected_energy = float(np.dot(projected, projected))
                    key = (rank_gain, projected_energy / cost, -cost, -float(index))
                elif policy == "d_optimal":
                    gain = safe_logdet(new_fim) - current_logdet
                    key = (gain / cost, rank_gain, -cost, -float(index))
                elif policy == "e_optimal":
                    new_min = float(np.min(np.linalg.eigvalsh(new_fim)))
                    gain = new_min - current_min
                    key = (gain / cost, rank_gain, -cost, -float(index))
                elif policy == "cosine_diversity":
                    novelty = candidate_cosine_novelty(probe, selected_probes)
                    key = (novelty / cost, rank_gain, -cost, -float(index))
                else:
                    raise ValueError(f"unknown policy: {policy}")
                scored.append((key, index))

            choice = max(scored, key=lambda item: item[0])[1]

        selected.append(choice)
        added.append(choice)
        candidates.remove(choice)

    final_fim = fim_from_indices(probes, selected)
    final_metrics = matrix_metrics(final_fim)
    return {
        "policy": policy,
        "full_rank": int(final_metrics["rank"]) == PARAMETER_DIM,
        "initial_circuits": len(initial),
        "new_circuits": len(added),
        "added_depth_cost": int(sum(probes[index].depth for index in added)),
        "total_depth_cost": int(sum(probes[index].depth for index in selected)),
        "final_metrics": final_metrics,
        "selected_new": [
            {
                "index": index,
                "depth": probes[index].depth,
                "label": probes[index].label,
                "weighted_sensitivity": [float(x) for x in probes[index].weighted_sensitivity],
            }
            for index in added
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v0.6.2 boundary information audit")
    parser.add_argument("--out", type=Path, default=Path("evidence/v062/outputs"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    probes = build_probes()
    initial_indices = [probe.index for probe in probes if probe.depth == 1]
    outside_indices = [probe.index for probe in probes if probe.depth >= 2]
    initial_fim = fim_from_indices(probes, initial_indices)
    initial_metrics = matrix_metrics(initial_fim)

    repetition_factors = (1, 10, 100, 1000)
    repetition = {
        str(factor): matrix_metrics(float(factor) * initial_fim)
        for factor in repetition_factors
    }
    repeat_ranks = [int(repetition[str(factor)]["rank"]) for factor in repetition_factors]
    repeat_nullities = [int(repetition[str(factor)]["nullity"]) for factor in repetition_factors]

    projector = nullspace_projector(initial_fim)
    outside_nullspace = []
    for index in outside_indices:
        vector = probes[index].weighted_sensitivity
        projected = projector @ vector
        outside_nullspace.append(
            {
                "index": index,
                "depth": probes[index].depth,
                "label": probes[index].label,
                "projected_energy": float(np.dot(projected, projected)),
            }
        )
    outside_nullspace.sort(key=lambda row: row["projected_energy"], reverse=True)

    all_fim = fim_from_indices(probes, [probe.index for probe in probes])
    all_metrics = matrix_metrics(all_fim)

    policies = [
        "random_new_view",
        "cosine_diversity",
        "d_optimal",
        "e_optimal",
        "nullspace_coverage",
    ]
    policy_results = {policy: select_greedy(probes, policy) for policy in policies}

    repeat_only = {
        "policy": "repeat_only_x1000",
        "full_rank": int(repetition["1000"]["rank"]) == PARAMETER_DIM,
        "new_circuits": 0,
        "added_depth_cost": int((1000 - 1) * sum(probes[index].depth for index in initial_indices)),
        "final_metrics": repetition["1000"],
        "selected_new": [],
    }

    best_outside_energy = float(outside_nullspace[0]["projected_energy"]) if outside_nullspace else 0.0
    checks = {
        "repeat_rank_invariant": len(set(repeat_ranks)) == 1,
        "repeat_nullity_invariant": len(set(repeat_nullities)) == 1,
        "new_boundary_has_nullspace_information": best_outside_energy > 1e-12,
        "full_rank_reachable_with_expanded_boundary": int(all_metrics["rank"]) == PARAMETER_DIM,
    }

    summary = {
        "version": "v0.6.2-boundary-information-audit",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "model_pack": "smq1Q_XYI",
        "rotation_step": ROTATION_STEP,
        "parameter_directions": ["uniform_rotation_x", "uniform_rotation_y", "uniform_rotation_z"],
        "max_depth": MAX_DEPTH,
        "probe_count": len(probes),
        "initial_boundary": {
            "depth": 1,
            "probe_count": len(initial_indices),
            "metrics": initial_metrics,
            "probes": [probes[index].label for index in initial_indices],
        },
        "repetition": repetition,
        "top_new_boundary_nullspace_contributions": outside_nullspace[:10],
        "all_probe_metrics": all_metrics,
        "repeat_only": repeat_only,
        "selection_policies": policy_results,
        "checks": checks,
        "gate_pass": all(checks.values()),
        "claim_boundary": (
            "Local Fisher/sensitivity audit of information span. Fixed-boundary rank invariance and "
            "classical optimal-design criteria are not OARL novelty claims."
        ),
    }

    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

    # A scientific gate failure is a valid result; workflow failure is reserved for execution/integrity errors.


if __name__ == "__main__":
    main()
