from __future__ import annotations

from collections.abc import Sequence

import numpy as np


GATE_X = "Gxpi2"
GATE_Y = "Gypi2"

ROTATION_X = np.asarray(
    [
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0],
    ],
    dtype=np.int64,
)
ROTATION_Y = np.asarray(
    [
        [0, 0, 1],
        [0, 1, 0],
        [-1, 0, 0],
    ],
    dtype=np.int64,
)
ROTATIONS = {GATE_X: ROTATION_X, GATE_Y: ROTATION_Y}

ROTATION_GENERATORS = np.asarray(
    [
        [
            [0, 0, 0],
            [0, 0, -1],
            [0, 1, 0],
        ],
        [
            [0, 0, 1],
            [0, 0, 0],
            [-1, 0, 0],
        ],
        [
            [0, -1, 0],
            [1, 0, 0],
            [0, 0, 0],
        ],
    ],
    dtype=np.int64,
)
Z_AXIS = np.asarray([0, 0, 1], dtype=np.int64)
UPPER_TRIANGLE = np.triu_indices(3)


def analytic_orientation_transport(
    word: Sequence[str],
    variance_floor: float = 1e-8,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return exact target probability, local gradient and Fisher matrix.

    The target gates and infinitesimal coherent-error transport are represented
    with integer SO(3) matrices. Only the final conversion to probability and
    Fisher information uses floating point.
    """

    state = Z_AXIS.copy()
    derivatives = np.zeros((3, 3), dtype=np.int64)

    for gate in word:
        if gate not in ROTATIONS:
            raise ValueError(f"unsupported gate {gate!r}")
        rotation = ROTATIONS[gate]
        next_state = rotation @ state
        derivatives = np.stack(
            [
                ROTATION_GENERATORS[axis] @ next_state
                + rotation @ derivatives[axis]
                for axis in range(3)
            ]
        )
        state = next_state

    probability = 0.5 * (1.0 + float(state[2]))
    gradient_twice = derivatives[:, 2]
    gradient = 0.5 * gradient_twice.astype(float)

    if probability in (0.0, 1.0) and np.any(gradient_twice != 0):
        raise RuntimeError(
            "an ideal boundary probability has a non-zero first derivative"
        )

    variance = max(probability * (1.0 - probability), variance_floor)
    fisher = np.outer(gradient, gradient) / variance
    fisher = 0.5 * (fisher + fisher.T)
    return probability, gradient, fisher


def exact_fisher_signature(fisher: np.ndarray) -> tuple[int, ...]:
    """Return the exact integer upper-triangle signature for this family."""

    values = np.asarray(fisher, dtype=float)[UPPER_TRIANGLE]
    rounded = np.rint(values).astype(np.int64)
    if not np.allclose(values, rounded, atol=1e-12, rtol=0.0):
        raise ValueError("Fisher matrix is not exactly integral in this family")
    return tuple(int(value) for value in rounded)


def relative_fisher_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    left = np.asarray(a, dtype=float)
    right = np.asarray(b, dtype=float)
    difference = np.linalg.norm(left - right, axis=(-2, -1))
    left_norm = np.linalg.norm(left, axis=(-2, -1))
    right_norm = np.linalg.norm(right, axis=(-2, -1))
    denominator = np.maximum(np.maximum(left_norm, right_norm), 1e-12)
    return difference / denominator


def anchor_states() -> np.ndarray:
    anchors = [0.1 * np.eye(3), np.eye(3), 10.0 * np.eye(3)]
    import itertools

    for permutation in itertools.permutations((0.1, 1.0, 10.0)):
        anchors.append(np.diag(np.asarray(permutation, dtype=float)))
    return np.asarray(anchors, dtype=float)


def doptimal_gains(fishers: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    matrices = np.asarray(fishers, dtype=float)
    states = np.asarray(anchors, dtype=float)
    base = np.linalg.slogdet(states)[1]
    expanded_states = states.reshape((1,) * (matrices.ndim - 2) + states.shape)
    expanded_fishers = np.expand_dims(matrices, axis=-3)
    return np.linalg.slogdet(expanded_states + expanded_fishers)[1] - base


def decision_distance(
    a: np.ndarray,
    b: np.ndarray,
    anchors: np.ndarray,
) -> np.ndarray:
    left = doptimal_gains(a, anchors)
    right = doptimal_gains(b, anchors)
    return np.max(np.abs(left - right), axis=-1)


def exact_relation(signatures: Sequence[tuple[int, ...]]) -> np.ndarray:
    n_items = len(signatures)
    relation = np.eye(n_items, dtype=bool)
    for i in range(n_items):
        for j in range(i + 1, n_items):
            same = signatures[i] == signatures[j]
            relation[i, j] = relation[j, i] = same
    return relation


def operational_relation(
    fishers: np.ndarray,
    anchors: np.ndarray,
    fisher_tolerance: float,
    decision_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matrices = np.asarray(fishers, dtype=float)
    n_items = matrices.shape[0]
    relation = np.eye(n_items, dtype=bool)
    fisher_distances = np.zeros((n_items, n_items), dtype=float)
    decision_distances = np.zeros((n_items, n_items), dtype=float)

    for i in range(n_items):
        for j in range(i + 1, n_items):
            fisher_distance = float(
                relative_fisher_distance(matrices[i], matrices[j])
            )
            task_distance = float(
                decision_distance(matrices[i], matrices[j], anchors)
            )
            fisher_distances[i, j] = fisher_distances[j, i] = fisher_distance
            decision_distances[i, j] = decision_distances[j, i] = task_distance
            compatible = (
                fisher_distance <= fisher_tolerance
                and task_distance <= decision_tolerance
            )
            relation[i, j] = relation[j, i] = compatible

    return relation, fisher_distances, decision_distances


def relation_axioms(relation: np.ndarray) -> dict[str, int | bool]:
    matrix = np.asarray(relation, dtype=bool)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("relation must be a square matrix")

    reflexive = bool(np.all(np.diag(matrix)))
    symmetric = bool(np.array_equal(matrix, matrix.T))
    two_step_paths = matrix.astype(np.int32) @ matrix.astype(np.int32)
    violating_endpoints = (two_step_paths > 0) & ~matrix
    witness_paths = int(np.sum(two_step_paths[~matrix]))
    transitive = not bool(np.any(violating_endpoints))
    return {
        "reflexive": reflexive,
        "symmetric": symmetric,
        "transitive": transitive,
        "nontransitive_endpoint_pairs": int(np.sum(violating_endpoints)),
        "nontransitive_witness_paths": witness_paths,
    }


def relation_components(relation: np.ndarray) -> list[list[int]]:
    audit = relation_axioms(relation)
    if not all(bool(audit[name]) for name in ("reflexive", "symmetric", "transitive")):
        raise ValueError("components are equivalence classes only for an equivalence relation")

    matrix = np.asarray(relation, dtype=bool)
    unseen = set(range(matrix.shape[0]))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        component = set(np.flatnonzero(matrix[start]).tolist())
        components.append(sorted(component))
        unseen.difference_update(component)
    return components


def greedy_complete_link(
    relation: np.ndarray,
    order: Sequence[int],
) -> list[list[int]]:
    matrix = np.asarray(relation, dtype=bool)
    classes: list[list[int]] = []
    for item in order:
        placed = False
        for group in classes:
            if all(bool(matrix[item, other]) for other in group):
                group.append(int(item))
                placed = True
                break
        if not placed:
            classes.append([int(item)])
    return classes


def class_false_pairs(
    classes: Sequence[Sequence[int]],
    truth: np.ndarray,
) -> int:
    import itertools

    count = 0
    for group in classes:
        for left, right in itertools.combinations(group, 2):
            if not bool(truth[left, right]):
                count += 1
    return count


def doptimal_design(
    classes: Sequence[Sequence[int]],
    fishers: np.ndarray,
    labels: Sequence[str],
    depths: Sequence[int],
    steps: int = 8,
    ridge: float = 1e-9,
) -> dict[str, object]:
    matrices = np.asarray(fishers, dtype=float)
    representatives = [
        min(group, key=lambda index: (depths[index], index)) for group in classes
    ]
    current = ridge * np.eye(matrices.shape[-1])
    selected: list[int] = []

    for _ in range(steps):
        scored: list[tuple[float, int, int, int]] = []
        for index in representatives:
            score = float(np.linalg.slogdet(current + matrices[index])[1])
            scored.append((score, -int(depths[index]), -int(index), int(index)))
        chosen = max(scored)[-1]
        selected.append(chosen)
        current = current + matrices[chosen]

    return {
        "logdet": float(np.linalg.slogdet(current)[1]),
        "score_evaluations": int(len(representatives) * steps),
        "selected_total_depth_cost": int(sum(depths[index] for index in selected)),
        "selected": [labels[index] for index in selected],
        "representatives": len(representatives),
    }
