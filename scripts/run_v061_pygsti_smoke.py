from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pygsti
from pygsti.modelpacks import smq1Q_XYI as std
from pygsti.models.gaugegroup import FullGaugeGroupElement


GATES = ("Gxpi2", "Gypi2")
GAUGE_MATRICES = (
    np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, -0.10, 0.0], [0.0, 0.10, 1.0, -0.10], [0.0, 0.0, 0.10, 1.0]]),
    np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.08, 0.0], [0.0, -0.06, 1.0, 0.07], [0.0, 0.0, -0.05, 1.0]]),
    np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.96, -0.07, 0.02], [0.0, 0.09, 1.03, -0.04], [0.0, -0.01, 0.06, 1.02]]),
)


def circuits_of_lengths(lengths: range) -> list[pygsti.circuits.Circuit]:
    circuits: list[pygsti.circuits.Circuit] = []
    for length in lengths:
        if length == 0:
            circuits.append(pygsti.circuits.Circuit([]))
            continue
        for sequence in itertools.product(GATES, repeat=length):
            circuits.append(pygsti.circuits.Circuit([(gate, 0) for gate in sequence]))
    return circuits


def probability_vector(model, circuits: list[pygsti.circuits.Circuit]) -> np.ndarray:
    values: list[float] = []
    for circuit in circuits:
        probs = model.probabilities(circuit)
        for outcome in sorted(probs, key=str):
            values.append(float(probs[outcome]))
    return np.asarray(values, dtype=float)


def l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run v0.6.1 pyGSTi gauge-equivalence smoke gate")
    parser.add_argument("--out", type=Path, default=Path("evidence/v061/smoke_outputs"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    discovery = circuits_of_lengths(range(0, 4))
    sealed = circuits_of_lengths(range(4, 7))

    target = std.target_model()
    target_discovery = probability_vector(target, discovery)
    target_sealed = probability_vector(target, sealed)
    target_params = np.asarray(target.to_vector(), dtype=float)

    equivalent_rows: list[dict[str, float | int]] = []
    for index, matrix in enumerate(GAUGE_MATRICES):
        transformed = target.copy()
        transformed.transform_inplace(FullGaugeGroupElement(matrix))
        equivalent_rows.append(
            {
                "case": index,
                "raw_parameter_l2": l2(target_params, transformed.to_vector()),
                "discovery_probability_max_abs": float(
                    np.max(np.abs(target_discovery - probability_vector(transformed, discovery)))
                ),
                "sealed_probability_max_abs": float(
                    np.max(np.abs(target_sealed - probability_vector(transformed, sealed)))
                ),
            }
        )

    distinct_rows: list[dict[str, float]] = []
    for op_noise in (0.002, 0.01, 0.03, 0.08):
        perturbed = target.depolarize(op_noise=op_noise, spam_noise=0.0)
        distinct_rows.append(
            {
                "op_noise": op_noise,
                "raw_parameter_l2": l2(target_params, perturbed.to_vector()),
                "discovery_probability_max_abs": float(
                    np.max(np.abs(target_discovery - probability_vector(perturbed, discovery)))
                ),
                "sealed_probability_max_abs": float(
                    np.max(np.abs(target_sealed - probability_vector(perturbed, sealed)))
                ),
            }
        )

    numerical_tol = 1e-10
    distinct_floor = 1e-6
    checks = {
        "gauge_changes_raw_representation": all(
            row["raw_parameter_l2"] > numerical_tol for row in equivalent_rows
        ),
        "gauge_preserves_discovery_probabilities": all(
            row["discovery_probability_max_abs"] <= numerical_tol for row in equivalent_rows
        ),
        "gauge_preserves_sealed_probabilities": all(
            row["sealed_probability_max_abs"] <= numerical_tol for row in equivalent_rows
        ),
        "physical_controls_change_sealed_probabilities": all(
            row["sealed_probability_max_abs"] > distinct_floor for row in distinct_rows
        ),
    }

    summary = {
        "version": "v0.6.1-smoke",
        "pygsti_version": getattr(pygsti, "__version__", "unknown"),
        "model_pack": "smq1Q_XYI",
        "discovery_circuits": len(discovery),
        "sealed_circuits": len(sealed),
        "equivalent_cases": equivalent_rows,
        "distinct_cases": distinct_rows,
        "checks": checks,
        "gate_pass": all(checks.values()),
        "claim_boundary": "Executable domain-transfer smoke test only; not evidence of distinctive OARL utility.",
    }

    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["gate_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
