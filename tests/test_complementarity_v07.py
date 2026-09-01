from oarl_bench.complementarity import (
    benchmark_worlds,
    decision_complete,
    discover_equivalence_classes,
    pair_synergy,
    run_policy,
)


def by_name(name, true_h=0):
    return next(w for w in benchmark_worlds(true_h=true_h) if w.name == name)


def test_pure_synergy_is_invisible_one_step_but_positive_jointly():
    w = by_name("pure_complementarity")
    assert pair_synergy(w, {}, 1, 2) > 0.99


def test_pure_complementarity_requires_both_views():
    w = by_name("pure_complementarity")
    assert not decision_complete(w, {1: w.observe(1)})
    assert not decision_complete(w, {2: w.observe(2)})
    assert decision_complete(w, {1: w.observe(1), 2: w.observe(2)})


def test_oarl_finds_pure_complementarity_in_two_probes():
    for h in range(4):
        w = by_name("pure_complementarity", h)
        r = run_policy(w, "oarl")
        assert r["correct"]
        assert r["probes"] == 2
        assert set(r["orientations_used"]) == {1, 2}


def test_unknown_when_no_available_orientation_is_decision_complete():
    for h in range(4):
        w = by_name("fundamental_insufficiency", h)
        r = run_policy(w, "oarl")
        assert r["unknown"]
        assert not r["decision_complete"]


def test_exact_redundancy_quotient_reduces_oarl_pair_planning():
    w = by_name("exact_redundancy")
    oarl = run_policy(w, "oarl")
    two = run_policy(w, "two_step")
    assert oarl["correct"] and two["correct"]
    assert oarl["planning_evals"] < two["planning_evals"]


def test_higher_order_case_is_not_falsely_declared_sufficient_after_two():
    w = by_name("higher_order_complementarity", 0)
    assert not decision_complete(w, {0: w.observe(0), 1: w.observe(1)})
    r = run_policy(w, "oarl")
    assert r["correct"]
    assert r["probes"] == 3


def test_equivalence_is_discovered_from_response_geometry():
    w = by_name("exact_redundancy")
    c = discover_equivalence_classes(w)
    assert c[0] == c[1]
    assert c[2] != c[0]
    assert c[3] != c[0]


def test_synergy_ablation_loses_one_probe_on_xor():
    for h in range(4):
        w = by_name("pure_complementarity", h)
        full = run_policy(w, "oarl")
        ablated = run_policy(w, "oarl_no_synergy")
        assert full["probes"] == 2
        assert ablated["probes"] >= 3


def test_transport_ablation_removes_redundancy_planning_gain():
    w = by_name("exact_redundancy")
    full = run_policy(w, "oarl")
    ablated = run_policy(w, "oarl_no_transport")
    assert full["planning_evals"] < ablated["planning_evals"]
