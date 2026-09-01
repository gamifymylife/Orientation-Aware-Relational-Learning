from pathlib import Path

import numpy as np

from oarl_bench.mutation_equivalence import (
    MutationMatrix,
    exact_signature_classes,
    false_merge_pairs,
    greedy_maximum_coverage,
    load_mutation_matrix,
    metadata_representatives,
    mutant_split_mask,
)


def test_exact_signature_classes_are_transitive_partition():
    matrix = np.asarray(
        [
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
        ],
        dtype=np.uint8,
    )
    assert exact_signature_classes(matrix) == [[0, 1, 3], [2]]


def test_false_merge_pairs_use_heldout_truth():
    heldout = np.asarray([[1, 0], [1, 0], [0, 1]], dtype=np.uint8)
    assert false_merge_pairs([[0, 1, 2]], heldout) == 2
    assert false_merge_pairs([[0, 1], [2]], heldout) == 0


def test_metadata_canonicalization_is_identifier_only():
    test_types = np.asarray(["dev", "dev", "randoop", "dev"])
    test_names = np.asarray(["a", "a", "a", "b"])
    assert metadata_representatives(test_types, test_names).tolist() == [0, 2, 3]


def test_mutant_split_is_stable_and_nonempty():
    ids = np.asarray([str(index) for index in range(100)])
    first = mutant_split_mask(ids, "Chart", 1)
    second = mutant_split_mask(ids, "Chart", 1)
    assert np.array_equal(first, second)
    assert 25 < int(np.sum(first)) < 75


def test_oracle_quotient_preserves_greedy_coverage_and_saves_scores():
    heldout = np.asarray(
        [
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
        ],
        dtype=np.uint8,
    )
    raw = greedy_maximum_coverage([[0], [1], [2], [3]], heldout, budget=2)
    oracle = greedy_maximum_coverage([[0, 1], [2, 3]], heldout, budget=2)
    assert oracle["covered_mutants"] == raw["covered_mutants"] == 4
    assert oracle["selected_representatives"] == raw["selected_representatives"] == [0, 2]
    assert oracle["score_evaluations"] < raw["score_evaluations"]


def test_compact_loader_rejects_no_expected_fields(tmp_path: Path):
    path = tmp_path / "matrix.npz"
    np.savez_compressed(
        path,
        project=np.asarray("Tiny"),
        fault=np.asarray(1),
        test_types=np.asarray(["dev", "dev"]),
        test_names=np.asarray(["a", "b"]),
        mutant_ids=np.asarray(["1", "2"]),
        kills=np.asarray([[1, 0], [0, 1]], dtype=np.uint8),
    )
    loaded = load_mutation_matrix(path)
    assert isinstance(loaded, MutationMatrix)
    assert loaded.project == "Tiny"
    assert loaded.kills.shape == (2, 2)
