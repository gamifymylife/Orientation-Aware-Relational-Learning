from __future__ import annotations

import numpy as np
import pytest

from oarl_bench.structural_transport import (
    GATE_X,
    GATE_Y,
    analytic_orientation_transport,
    doptimal_design,
    exact_fisher_signature,
    exact_relation,
    relation_axioms,
    relation_components,
)


def test_analytic_transport_matches_known_short_word_gradients() -> None:
    probability_x, gradient_x, fisher_x = analytic_orientation_transport((GATE_X,))
    probability_xx, gradient_xx, fisher_xx = analytic_orientation_transport(
        (GATE_X, GATE_X)
    )
    probability_xy, gradient_xy, fisher_xy = analytic_orientation_transport(
        (GATE_X, GATE_Y)
    )

    assert probability_x == pytest.approx(0.5)
    assert gradient_x == pytest.approx(np.asarray([-0.5, 0.0, 0.0]))
    assert fisher_x == pytest.approx(np.diag([1.0, 0.0, 0.0]))

    assert probability_xx == pytest.approx(0.0)
    assert gradient_xx == pytest.approx(np.zeros(3))
    assert fisher_xx == pytest.approx(np.zeros((3, 3)))

    assert probability_xy == pytest.approx(0.5)
    assert gradient_xy == pytest.approx(np.asarray([-0.5, 0.0, -0.5]))
    assert fisher_xy == pytest.approx(
        np.asarray(
            [
                [1.0, 0.0, 1.0],
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 1.0],
            ]
        )
    )


def test_exact_signatures_form_true_equivalence_classes() -> None:
    words = [
        (GATE_X,),
        (GATE_X,),
        (GATE_Y,),
        (GATE_X, GATE_X),
    ]
    fishers = [analytic_orientation_transport(word)[2] for word in words]
    signatures = [exact_fisher_signature(fisher) for fisher in fishers]
    relation = exact_relation(signatures)

    assert relation_axioms(relation) == {
        "reflexive": True,
        "symmetric": True,
        "transitive": True,
        "nontransitive_endpoint_pairs": 0,
        "nontransitive_witness_paths": 0,
    }
    assert relation_components(relation) == [[0, 1], [2], [3]]


def test_threshold_compatibility_is_not_assumed_transitive() -> None:
    relation = np.asarray(
        [
            [True, True, False],
            [True, True, True],
            [False, True, True],
        ],
        dtype=bool,
    )

    audit = relation_axioms(relation)
    assert audit["reflexive"] is True
    assert audit["symmetric"] is True
    assert audit["transitive"] is False
    assert audit["nontransitive_endpoint_pairs"] == 2
    with pytest.raises(ValueError, match="equivalence relation"):
        relation_components(relation)


def test_exact_partition_preserves_doptimal_selection_value() -> None:
    words = [
        (GATE_X,),
        (GATE_X,),
        (GATE_Y,),
        (GATE_X, GATE_Y),
    ]
    fishers = np.asarray(
        [analytic_orientation_transport(word)[2] for word in words]
    )
    signatures = [exact_fisher_signature(fisher) for fisher in fishers]
    quotient = relation_components(exact_relation(signatures))
    raw = [[index] for index in range(len(words))]
    labels = [".".join(word) for word in words]
    depths = [len(word) for word in words]

    raw_design = doptimal_design(raw, fishers, labels, depths, steps=4)
    quotient_design = doptimal_design(quotient, fishers, labels, depths, steps=4)

    assert quotient_design["logdet"] == pytest.approx(raw_design["logdet"])
    assert quotient_design["score_evaluations"] < raw_design["score_evaluations"]
