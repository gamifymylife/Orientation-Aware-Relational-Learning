"""Exact test-equivalence utilities for the v0.6.6 mutation gate.

The external matrix contains one row per test and one column per mutant.  Two
tests are task-equivalent on a mutant family exactly when their binary kill
vectors are identical.  This is a dataset-relative equivalence relation, not a
claim that the tests are semantically identical programs.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class MutationMatrix:
    project: str
    fault: int
    test_types: np.ndarray
    test_names: np.ndarray
    mutant_ids: np.ndarray
    kills: np.ndarray

    def __post_init__(self) -> None:
        if self.kills.ndim != 2:
            raise ValueError("kills must be a two-dimensional test x mutant matrix")
        if self.kills.shape != (len(self.test_names), len(self.mutant_ids)):
            raise ValueError("matrix dimensions do not match test and mutant labels")
        if len(self.test_types) != len(self.test_names):
            raise ValueError("test type and name arrays must have equal length")
        if not np.all((self.kills == 0) | (self.kills == 1)):
            raise ValueError("kill matrix must be binary")


def load_mutation_matrix(path: Path) -> MutationMatrix:
    """Load a compact, non-pickle NPZ mutation matrix."""

    with np.load(path, allow_pickle=False) as data:
        return MutationMatrix(
            project=str(data["project"].item()),
            fault=int(data["fault"].item()),
            test_types=np.asarray(data["test_types"], dtype=str),
            test_names=np.asarray(data["test_names"], dtype=str),
            mutant_ids=np.asarray(data["mutant_ids"], dtype=str),
            kills=np.asarray(data["kills"], dtype=np.uint8),
        )


def mutant_split_mask(
    mutant_ids: np.ndarray,
    project: str,
    fault: int,
    *,
    seed_label: str = "v066-mutant-split",
) -> np.ndarray:
    """Return the preregistered deterministic development-mutant mask."""

    mask = np.asarray(
        [
            hashlib.sha256(
                f"{seed_label}:{project}:{int(fault)}:{mutant_id}".encode("utf-8")
            ).digest()[0]
            < 128
            for mutant_id in np.asarray(mutant_ids, dtype=str)
        ],
        dtype=bool,
    )
    if not np.any(mask) or np.all(mask):
        raise ValueError("deterministic split produced an empty partition")
    return mask


def metadata_representatives(
    test_types: np.ndarray,
    test_names: np.ndarray,
) -> np.ndarray:
    """Keep the first row for each exact externally supplied test identifier."""

    seen: set[tuple[str, str]] = set()
    representatives: list[int] = []
    for index, (test_type, test_name) in enumerate(zip(test_types, test_names)):
        key = (str(test_type), str(test_name))
        if key not in seen:
            seen.add(key)
            representatives.append(index)
    return np.asarray(representatives, dtype=int)


def exact_signature_classes(matrix: np.ndarray) -> list[list[int]]:
    """Partition rows by exact binary response signature."""

    values = np.asarray(matrix, dtype=np.uint8)
    if values.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    classes: dict[bytes, list[int]] = {}
    for index, row in enumerate(values):
        key = np.packbits(row, bitorder="little").tobytes()
        classes.setdefault(key, []).append(index)
    return list(classes.values())


def false_merge_pairs(
    proposed_classes: list[list[int]],
    heldout_matrix: np.ndarray,
) -> int:
    """Count unordered proposed pairs whose held-out signatures differ."""

    heldout = np.asarray(heldout_matrix, dtype=np.uint8)
    keys = [np.packbits(row, bitorder="little").tobytes() for row in heldout]
    false_pairs = 0
    for members in proposed_classes:
        for offset, left in enumerate(members):
            for right in members[:offset]:
                false_pairs += keys[left] != keys[right]
    return int(false_pairs)


def proposed_pair_count(classes: list[list[int]]) -> int:
    return int(sum(len(members) * (len(members) - 1) // 2 for members in classes))


def greedy_maximum_coverage(
    classes: list[list[int]],
    heldout_matrix: np.ndarray,
    *,
    budget: int,
) -> dict[str, object]:
    """Run the same deterministic greedy coverage policy over any partition."""

    if budget < 1:
        raise ValueError("budget must be positive")
    heldout = np.asarray(heldout_matrix, dtype=np.uint8).astype(bool)
    representatives = np.asarray([min(members) for members in classes], dtype=int)
    available = np.ones(len(classes), dtype=bool)
    covered = np.zeros(heldout.shape[1], dtype=bool)
    selected: list[int] = []
    score_evaluations = 0

    for _ in range(min(budget, len(classes))):
        candidate_indices = np.flatnonzero(available)
        gains = np.asarray(
            [np.sum(heldout[representatives[index]] & ~covered) for index in candidate_indices],
            dtype=int,
        )
        score_evaluations += len(candidate_indices)
        max_gain = int(np.max(gains))
        if max_gain <= 0:
            break
        tied = candidate_indices[gains == max_gain]
        chosen = int(min(tied, key=lambda index: int(representatives[index])))
        representative = int(representatives[chosen])
        selected.append(representative)
        covered |= heldout[representative]
        available[chosen] = False

    coverable = np.any(heldout, axis=0)
    return {
        "selected_representatives": selected,
        "selected_count": len(selected),
        "covered_mutants": int(np.sum(covered)),
        "coverable_mutants": int(np.sum(coverable)),
        "coverage_fraction": float(np.sum(covered) / max(np.sum(coverable), 1)),
        "score_evaluations": int(score_evaluations),
    }


def evaluate_matrix(matrix: MutationMatrix, *, budget: int = 20) -> dict[str, object]:
    """Evaluate suitability without fitting an OARL-specific learner."""

    development_mask = mutant_split_mask(
        matrix.mutant_ids,
        matrix.project,
        matrix.fault,
    )
    metadata_rows = metadata_representatives(matrix.test_types, matrix.test_names)
    development_all = matrix.kills[:, development_mask]
    heldout_all = matrix.kills[:, ~development_mask]

    eligible_global = metadata_rows[np.any(development_all[metadata_rows], axis=1)]
    development = development_all[eligible_global]
    heldout = heldout_all[eligible_global]

    raw_classes = [[index] for index in range(len(eligible_global))]
    development_classes = exact_signature_classes(development)
    oracle_classes = exact_signature_classes(heldout)

    proposed_pairs = proposed_pair_count(development_classes)
    false_pairs = false_merge_pairs(development_classes, heldout)
    true_pairs = proposed_pairs - false_pairs
    raw_design = greedy_maximum_coverage(raw_classes, heldout, budget=budget)
    development_design = greedy_maximum_coverage(
        development_classes,
        heldout,
        budget=budget,
    )
    oracle_design = greedy_maximum_coverage(oracle_classes, heldout, budget=budget)

    return {
        "project": matrix.project,
        "fault": matrix.fault,
        "raw_tests": int(len(matrix.test_names)),
        "metadata_canonical_tests": int(len(metadata_rows)),
        "eligible_tests": int(len(eligible_global)),
        "development_mutants": int(np.sum(development_mask)),
        "heldout_mutants": int(np.sum(~development_mask)),
        "development_evidence_cells": int(development.size),
        "heldout_evaluator_cells": int(heldout.size),
        "development_signature_classes": int(len(development_classes)),
        "development_signature_compression": float(
            1.0 - len(development_classes) / max(len(eligible_global), 1)
        ),
        "development_proposed_pairs": int(proposed_pairs),
        "development_true_pairs": int(true_pairs),
        "development_false_merge_pairs": int(false_pairs),
        "development_pair_precision": float(true_pairs / max(proposed_pairs, 1)),
        "oracle_classes": int(len(oracle_classes)),
        "oracle_compression": float(
            1.0 - len(oracle_classes) / max(len(eligible_global), 1)
        ),
        "raw_design": raw_design,
        "development_signature_design": development_design,
        "oracle_design": oracle_design,
        "oracle_false_merge_pairs": 0,
        "oracle_score_evaluations_saved": int(
            raw_design["score_evaluations"] - oracle_design["score_evaluations"]
        ),
        "oracle_coverage_matches_raw": bool(
            oracle_design["covered_mutants"] == raw_design["covered_mutants"]
        ),
        "oracle_selected_count_matches_raw": bool(
            oracle_design["selected_count"] == raw_design["selected_count"]
        ),
    }
