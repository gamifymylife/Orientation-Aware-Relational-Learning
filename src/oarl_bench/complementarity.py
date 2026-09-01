"""v0.6 Complementary Orientation Gate.

A small exact benchmark for decision-complete perspective selection. The module
uses only candidate-mechanism predictions; the hidden true mechanism is used
only to generate observations and score outcomes.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import log2
from typing import Iterable

import numpy as np

UNKNOWN = -1


@dataclass(frozen=True)
class ComplementarityWorld:
    name: str
    responses: np.ndarray
    decisions: np.ndarray
    costs: np.ndarray
    equivalence_class: np.ndarray
    true_h: int

    def __post_init__(self):
        h, o = self.responses.shape
        if self.decisions.shape != (h,):
            raise ValueError("decisions must have one value per mechanism")
        if self.costs.shape != (o,):
            raise ValueError("costs must have one value per orientation")
        if self.equivalence_class.shape != (o,):
            raise ValueError("equivalence_class must have one value per orientation")
        if not (0 <= self.true_h < h):
            raise ValueError("true_h out of range")

    @property
    def n_mechanisms(self) -> int:
        return self.responses.shape[0]

    @property
    def n_orientations(self) -> int:
        return self.responses.shape[1]

    def observe(self, orientation: int) -> int:
        return int(self.responses[self.true_h, orientation])


def compatible(world: ComplementarityWorld, evidence: dict[int, int]) -> np.ndarray:
    mask = np.ones(world.n_mechanisms, dtype=bool)
    for o, y in evidence.items():
        mask &= world.responses[:, o] == y
    return np.flatnonzero(mask)


def decision_set(world: ComplementarityWorld, evidence: dict[int, int]) -> set[int]:
    idx = compatible(world, evidence)
    return set(map(int, world.decisions[idx]))


def decision_complete(world: ComplementarityWorld, evidence: dict[int, int]) -> bool:
    return len(decision_set(world, evidence)) == 1


def current_decision(world: ComplementarityWorld, evidence: dict[int, int]) -> int:
    ds = decision_set(world, evidence)
    return next(iter(ds)) if len(ds) == 1 else UNKNOWN


def _entropy(counts: Iterable[int]) -> float:
    counts = np.asarray(list(counts), dtype=float)
    total = counts.sum()
    if total <= 0:
        return 0.0
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum())


def mechanism_entropy(world: ComplementarityWorld, evidence: dict[int, int]) -> float:
    n = len(compatible(world, evidence))
    return log2(n) if n > 0 else 0.0


def decision_entropy(world: ComplementarityWorld, evidence: dict[int, int]) -> float:
    idx = compatible(world, evidence)
    _, counts = np.unique(world.decisions[idx], return_counts=True)
    return _entropy(counts)


def expected_utility(
    world: ComplementarityWorld,
    evidence: dict[int, int],
    orientation: int,
    *,
    target: str = "decision",
) -> float:
    idx = compatible(world, evidence)
    if len(idx) == 0:
        return 0.0
    entropy_fn = decision_entropy if target == "decision" else mechanism_entropy
    before = entropy_fn(world, evidence)
    values, counts = np.unique(world.responses[idx, orientation], return_counts=True)
    after = 0.0
    for y, count in zip(values, counts):
        e2 = dict(evidence)
        e2[orientation] = int(y)
        after += (count / len(idx)) * entropy_fn(world, e2)
    return float(before - after)


def pair_synergy(
    world: ComplementarityWorld,
    evidence: dict[int, int],
    a: int,
    b: int,
) -> float:
    idx = compatible(world, evidence)
    if len(idx) == 0:
        return 0.0
    before = decision_entropy(world, evidence)
    pairs = world.responses[idx][:, [a, b]]
    _, inverse, counts = np.unique(pairs, axis=0, return_inverse=True, return_counts=True)
    after = 0.0
    for group, count in enumerate(counts):
        members = idx[inverse == group]
        _, dc = np.unique(world.decisions[members], return_counts=True)
        after += (count / len(idx)) * _entropy(dc)
    joint = before - after
    return float(joint - expected_utility(world, evidence, a) - expected_utility(world, evidence, b))


def discover_equivalence_classes(world: ComplementarityWorld) -> np.ndarray:
    """Discover exact orientation equivalence from candidate response partitions."""
    O = world.n_orientations
    cls = np.full(O, -1, dtype=int)
    next_c = 0
    for o in range(O):
        if cls[o] >= 0:
            continue
        cls[o] = next_c
        a = world.responses[:, o]
        for q in range(o + 1, O):
            if cls[q] >= 0:
                continue
            b = world.responses[:, q]
            mapping = {}
            reverse = {}
            ok = True
            for av, bv in zip(a, b):
                av, bv = int(av), int(bv)
                if av in mapping and mapping[av] != bv:
                    ok = False
                    break
                if bv in reverse and reverse[bv] != av:
                    ok = False
                    break
                mapping[av] = bv
                reverse[bv] = av
            if ok:
                cls[q] = next_c
        next_c += 1
    return cls


def canonical_orientations(world: ComplementarityWorld) -> list[int]:
    classes = discover_equivalence_classes(world)
    out = []
    for c in np.unique(classes):
        members = np.flatnonzero(classes == c)
        out.append(int(members[np.argmin(world.costs[members])]))
    return sorted(out)


def _argmax_score(scores: list[tuple[float, float, int]]) -> int | None:
    if not scores:
        return None
    scores.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return int(scores[0][2])


def select_greedy(world, evidence, remaining, *, target="decision") -> int | None:
    scores = []
    for o in remaining:
        u = expected_utility(world, evidence, o, target=target)
        scores.append((u / world.costs[o], u, o))
    return _argmax_score(scores)


def select_two_step(world, evidence, remaining) -> tuple[int | None, int]:
    """Fair generic two-step decision lookahead over unordered pairs."""
    remaining = list(remaining)
    if not remaining:
        return None, 0
    best = None
    for o in remaining:
        u = expected_utility(world, evidence, o)
        cand = (u / world.costs[o], u, -o)
        if best is None or cand > best[0]:
            best = (cand, o)
    evals = 0
    for a, b in combinations(remaining, 2):
        evals += 1
        ua = expected_utility(world, evidence, a)
        ub = expected_utility(world, evidence, b)
        syn = pair_synergy(world, evidence, a, b)
        joint = ua + ub + syn
        first = a if world.costs[a] <= world.costs[b] else b
        cand = (joint / (world.costs[a] + world.costs[b]), joint, -first)
        if cand > best[0]:
            best = (cand, first)
    return int(best[1]), evals


def select_oarl(world, evidence, remaining) -> tuple[int | None, int]:
    canonical = [o for o in canonical_orientations(world) if o in remaining]
    if not canonical:
        return None, 0
    best = None
    evals = 0
    for o in canonical:
        u = expected_utility(world, evidence, o)
        cand = (u / world.costs[o], u, -o)
        if best is None or cand > best[0]:
            best = (cand, o)
    for a, b in combinations(canonical, 2):
        evals += 1
        syn = pair_synergy(world, evidence, a, b)
        if syn <= 1e-12:
            continue
        joint = expected_utility(world, evidence, a) + expected_utility(world, evidence, b) + syn
        first = a if world.costs[a] <= world.costs[b] else b
        cand = (joint / (world.costs[a] + world.costs[b]), joint, -first)
        if cand > best[0]:
            best = (cand, first)
    return int(best[1]), evals


def select_oarl_no_synergy(world, evidence, remaining) -> tuple[int | None, int]:
    canonical = [o for o in canonical_orientations(world) if o in remaining]
    return select_greedy(world, evidence, canonical, target="decision"), 0


def select_oarl_no_transport(world, evidence, remaining) -> tuple[int | None, int]:
    remaining = list(remaining)
    if not remaining:
        return None, 0
    best = None
    for o in remaining:
        u = expected_utility(world, evidence, o)
        cand = (u / world.costs[o], u, -o)
        if best is None or cand > best[0]:
            best = (cand, o)
    evals = 0
    for a, b in combinations(remaining, 2):
        evals += 1
        syn = pair_synergy(world, evidence, a, b)
        if syn <= 1e-12:
            continue
        joint = expected_utility(world, evidence, a) + expected_utility(world, evidence, b) + syn
        first = a if world.costs[a] <= world.costs[b] else b
        cand = (joint / (world.costs[a] + world.costs[b]), joint, -first)
        if cand > best[0]:
            best = (cand, first)
    return int(best[1]), evals


def run_policy(world: ComplementarityWorld, policy: str, *, seed: int = 0) -> dict:
    evidence: dict[int, int] = {}
    remaining = list(range(world.n_orientations))
    probes = 0
    cost = 0.0
    planning_evals = 0
    rng = np.random.default_rng(seed)
    while remaining and not decision_complete(world, evidence):
        if policy == "fixed":
            o = remaining[0]
        elif policy == "random":
            o = int(rng.choice(remaining))
        elif policy == "greedy_feature":
            o = select_greedy(world, evidence, remaining, target="mechanism")
        elif policy == "active_decision":
            o = select_greedy(world, evidence, remaining, target="decision")
        elif policy == "two_step":
            o, n = select_two_step(world, evidence, remaining)
            planning_evals += n
        elif policy == "oarl":
            o, n = select_oarl(world, evidence, remaining)
            planning_evals += n
        elif policy == "oarl_no_synergy":
            o, n = select_oarl_no_synergy(world, evidence, remaining)
            planning_evals += n
        elif policy == "oarl_no_transport":
            o, n = select_oarl_no_transport(world, evidence, remaining)
            planning_evals += n
        elif policy == "exhaustive":
            o = remaining[0]
        else:
            raise ValueError(f"unknown policy {policy}")
        if o is None:
            break
        evidence[o] = world.observe(o)
        remaining.remove(o)
        probes += 1
        cost += float(world.costs[o])
        if policy == "exhaustive" and remaining:
            continue
    if policy == "exhaustive":
        for o in list(remaining):
            evidence[o] = world.observe(o)
            probes += 1
            cost += float(world.costs[o])
        remaining = []
    d = current_decision(world, evidence)
    true_d = int(world.decisions[world.true_h])
    return {
        "world": world.name,
        "policy": policy,
        "probes": probes,
        "cost": cost,
        "planning_evals": planning_evals,
        "decision": d,
        "true_decision": true_d,
        "correct": d == true_d,
        "unknown": d == UNKNOWN,
        "decision_complete": d != UNKNOWN,
        "orientations_used": tuple(sorted(evidence)),
    }


def _world(name, cols, decisions, *, true_h=0, costs=None, classes=None):
    r = np.asarray(cols, dtype=int).T
    o = r.shape[1]
    if costs is None:
        costs = np.ones(o, dtype=float)
    if classes is None:
        classes = np.arange(o, dtype=int)
    return ComplementarityWorld(
        name=name,
        responses=r,
        decisions=np.asarray(decisions, dtype=int),
        costs=np.asarray(costs, dtype=float),
        equivalence_class=np.asarray(classes, dtype=int),
        true_h=int(true_h),
    )


def benchmark_worlds(true_h: int = 0) -> list[ComplementarityWorld]:
    xor_decision = [0, 1, 1, 0]
    x = [0, 0, 1, 1]
    y = [0, 1, 0, 1]
    noise1 = [0, 1, 2, 3]
    constant = [0, 0, 0, 0]
    worlds = [
        _world("single_view", [xor_decision, constant, noise1], xor_decision, true_h=true_h),
        _world("exact_redundancy", [xor_decision, [7, 8, 8, 7], x, y], xor_decision,
               true_h=true_h, classes=[0, 0, 1, 2]),
        _world("pure_complementarity", [constant, x, y, x], xor_decision, true_h=true_h),
        _world("misleading_similarity", [x, y, xor_decision, constant], xor_decision, true_h=true_h),
        _world("fundamental_insufficiency", [constant, [0, 0, 1, 1], [2, 2, 3, 3]],
               [0, 1, 0, 1], true_h=true_h),
    ]
    bits = np.array([[i >> 2 & 1, i >> 1 & 1, i & 1] for i in range(8)], dtype=int)
    parity = np.bitwise_xor.reduce(bits, axis=1)
    worlds.append(ComplementarityWorld(
        name="higher_order_complementarity",
        responses=bits,
        decisions=parity,
        costs=np.ones(3),
        equivalence_class=np.arange(3),
        true_h=min(true_h, 7),
    ))
    return worlds


def run_gate(seeds: Iterable[int] = range(16)) -> list[dict]:
    policies = [
        "fixed", "random", "exhaustive", "greedy_feature", "active_decision",
        "two_step", "oarl_no_synergy", "oarl_no_transport", "oarl",
    ]
    rows = []
    for seed in seeds:
        for h in range(4):
            for world in benchmark_worlds(true_h=h):
                for policy in policies:
                    rows.append(run_policy(world, policy, seed=int(seed)))
    return rows
