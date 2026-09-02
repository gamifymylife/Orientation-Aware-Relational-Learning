"""Frozen acquisition policies for OARL v0.7 external Track R.

All selectors consume only policy-visible candidate metadata, declared cost, the frozen
relation graph, and observations produced by prior executed probes.  They never consume
repository names, PR metadata, changed files, post-fix regression tests, evaluator labels,
or known witness locations.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .external_track_r import DEFAULT_STUDY_SEED, RelationGraph

POLICY_NAMES = (
    "random",
    "fixed",
    "greedy_information",
    "greedy_decision",
    "cost_aware_greedy",
    "generic_two_step",
    "generic_set_cover",
    "oarl_equivalence_only",
    "oarl_complementarity_only",
    "oarl_full",
    "oarl_scrambled_relations",
)

_FEATURE_FIELDS = (
    "operator_family",
    "value_category",
    "call_shape",
    "fixture_shape",
    "test_structure",
)
_RELATION_TYPES = (
    "same_operator_family",
    "same_value_category",
    "same_call_shape",
    "same_fixture_shape",
    "same_test_structure",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class ProbeCandidate:
    candidate_id: str
    features: Mapping[str, str]
    cost: float = 1.0

    @classmethod
    def from_policy_view(cls, view: Mapping[str, Any], *, cost: float = 1.0) -> "ProbeCandidate":
        missing = [name for name in ("candidate_id", *_FEATURE_FIELDS) if name not in view]
        if missing:
            raise ValueError(f"candidate missing policy-visible fields: {missing}")
        return cls(
            candidate_id=str(view["candidate_id"]),
            features={name: str(view[name]) for name in _FEATURE_FIELDS},
            cost=max(0.000001, float(cost)),
        )


@dataclass(frozen=True)
class ProbeOutcome:
    candidate_id: str
    distance: float
    valid: bool = True

    @property
    def witness_signal(self) -> float:
        return _clamp(float(self.distance)) if self.valid else 0.0

    @property
    def positive(self) -> bool:
        return self.valid and self.witness_signal > 0.0


class TrackRPolicy:
    """Case-independent policy with frozen empirical feature models and instrumentation."""

    def __init__(
        self,
        name: str,
        candidates: Sequence[ProbeCandidate],
        *,
        relation_graph: RelationGraph | None = None,
        seed: int = DEFAULT_STUDY_SEED,
    ) -> None:
        if name not in POLICY_NAMES:
            raise ValueError(f"unknown policy {name!r}")
        ids = [candidate.candidate_id for candidate in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")
        self.name = name
        self.seed = int(seed)
        self.candidates = tuple(candidates)
        self.by_id = {candidate.candidate_id: candidate for candidate in candidates}
        self.fixed_rank = {candidate.candidate_id: i for i, candidate in enumerate(candidates)}
        self.relation_graph = relation_graph
        self.history: list[ProbeOutcome] = []
        self.tried: set[str] = set()
        self.planning_steps = 0
        self.raw_candidate_considerations = 0
        self.utility_evaluations = 0
        self.orbit_evaluations = 0
        self._rng = random.Random(self.seed)
        self._random_priority = {candidate.candidate_id: self._rng.random() for candidate in candidates}

    def identity(self) -> dict[str, Any]:
        return {
            "type": "oarl-v07-external-track-r-policy",
            "name": self.name,
            "seed": self.seed,
            "feature_fields": list(_FEATURE_FIELDS),
            "relation_types": list(_RELATION_TYPES),
            "source_sha256": _hash({"policy_names": POLICY_NAMES, "features": _FEATURE_FIELDS, "relations": _RELATION_TYPES}),
            "quotient_semantics": "share utility evaluation only for exact score-equivalent planner state; never delete concrete probes",
        }

    def observe(self, outcome: ProbeOutcome) -> None:
        if outcome.candidate_id not in self.by_id:
            raise ValueError(f"unknown candidate {outcome.candidate_id!r}")
        if outcome.candidate_id in self.tried:
            raise ValueError(f"duplicate observation for {outcome.candidate_id!r}")
        self.tried.add(outcome.candidate_id)
        self.history.append(outcome)

    def _remaining(self) -> list[ProbeCandidate]:
        return [candidate for candidate in self.candidates if candidate.candidate_id not in self.tried]

    def _feature_evidence(self) -> dict[tuple[str, str], tuple[float, float, float]]:
        """Beta-Bernoulli counts plus mean distance for every visible feature value."""
        positives: Counter[tuple[str, str]] = Counter()
        negatives: Counter[tuple[str, str]] = Counter()
        distance_sum: Counter[tuple[str, str]] = Counter()
        for row in self.history:
            candidate = self.by_id[row.candidate_id]
            for field, value in candidate.features.items():
                key = (field, value)
                if row.positive:
                    positives[key] += 1
                else:
                    negatives[key] += 1
                distance_sum[key] += row.witness_signal
        out: dict[tuple[str, str], tuple[float, float, float]] = {}
        keys = set(positives) | set(negatives)
        for key in keys:
            p = positives[key]
            n = negatives[key]
            posterior = (1.0 + p) / (2.0 + p + n)
            mean_distance = distance_sum[key] / max(1, p + n)
            out[key] = (posterior, float(p + n), mean_distance)
        return out

    def _candidate_prediction(self, candidate: ProbeCandidate) -> tuple[float, float, float]:
        evidence = self._feature_evidence()
        posteriors: list[float] = []
        counts: list[float] = []
        distances: list[float] = []
        for field, value in candidate.features.items():
            posterior, count, mean_distance = evidence.get((field, value), (0.5, 0.0, 0.0))
            posteriors.append(posterior)
            counts.append(count)
            distances.append(mean_distance)
        # Geometric aggregation avoids one high feature dominating completely.
        log_mean = sum(math.log(max(1e-9, p)) for p in posteriors) / len(posteriors)
        probability = math.exp(log_mean)
        support = sum(counts) / len(counts)
        distance = sum(distances) / len(distances)
        return _clamp(probability), support, _clamp(distance)

    def _information_score(self, candidate: ProbeCandidate) -> float:
        probability, support, _ = self._candidate_prediction(candidate)
        entropy = 0.0
        if 0.0 < probability < 1.0:
            entropy = -(probability * math.log2(probability) + (1 - probability) * math.log2(1 - probability))
        novelty = 1.0 / math.sqrt(1.0 + support)
        return entropy + 0.20 * novelty

    def _decision_score(self, candidate: ProbeCandidate) -> float:
        probability, support, distance = self._candidate_prediction(candidate)
        return probability + 0.20 * distance + 0.05 / math.sqrt(1.0 + support)

    def _relation_state(self, candidate: ProbeCandidate) -> tuple[tuple[str, int, int, int], ...]:
        if self.relation_graph is None:
            return tuple()
        by_relation: dict[str, list[str]] = defaultdict(list)
        for neighbour, relation in self.relation_graph.neighbours(candidate.candidate_id):
            by_relation[relation].append(neighbour)
        state: list[tuple[str, int, int, int]] = []
        outcome_by_id = {row.candidate_id: row for row in self.history}
        for relation in sorted(by_relation):
            observed = [outcome_by_id[n] for n in by_relation[relation] if n in outcome_by_id]
            positive = sum(row.positive for row in observed)
            negative = len(observed) - positive
            unseen = len(by_relation[relation]) - len(observed)
            state.append((relation, positive, negative, unseen))
        return tuple(state)

    def _complementarity_score(self, candidate: ProbeCandidate) -> float:
        """Interaction-aware acquisition value from relation-conditioned evidence.

        The term is positive when evidence on one structural perspective raises the value
        of a candidate that composes additional perspectives.  It does not treat two
        non-witness probes as a witness and never changes the final confirmation rule.
        """
        if self.relation_graph is None or not self.history:
            return 0.0
        outcome_by_id = {row.candidate_id: row for row in self.history}
        grouped: dict[str, list[ProbeOutcome]] = defaultdict(list)
        for neighbour, relation in self.relation_graph.neighbours(candidate.candidate_id):
            row = outcome_by_id.get(neighbour)
            if row is not None and row.valid:
                grouped[relation].append(row)
        active_relations = 0
        weighted = 0.0
        for rows in grouped.values():
            if not rows:
                continue
            active_relations += 1
            weighted += max(row.witness_signal for row in rows)
        if active_relations < 2:
            return 0.0
        # Synergy grows only when multiple relation projections carry evidence.
        return _clamp((weighted / active_relations) * (1.0 - 1.0 / active_relations))

    def _set_cover_score(self, candidate: ProbeCandidate) -> float:
        covered: set[tuple[str, str]] = set()
        for row in self.history:
            old = self.by_id[row.candidate_id]
            covered.update(old.features.items())
        return float(sum((field, value) not in covered for field, value in candidate.features.items()))

    def _generic_two_step_score(self, candidate: ProbeCandidate, remaining: Sequence[ProbeCandidate]) -> float:
        first = self._decision_score(candidate)
        alternatives = [other for other in remaining if other.candidate_id != candidate.candidate_id]
        if not alternatives:
            return first
        # Generic lookahead deliberately ignores relation edges.  It estimates the best
        # second action from the same marginal empirical feature model.
        second = max(self._decision_score(other) for other in alternatives)
        return first + (1.0 - first) * 0.5 * second

    def _base_score(self, candidate: ProbeCandidate, remaining: Sequence[ProbeCandidate]) -> float:
        if self.name == "greedy_information":
            return self._information_score(candidate)
        if self.name == "greedy_decision":
            return self._decision_score(candidate)
        if self.name == "cost_aware_greedy":
            return self._decision_score(candidate) / candidate.cost
        if self.name == "generic_two_step":
            return self._generic_two_step_score(candidate, remaining)
        if self.name == "generic_set_cover":
            return self._set_cover_score(candidate) / candidate.cost
        if self.name in {"oarl_equivalence_only", "oarl_full", "oarl_scrambled_relations"}:
            score = self._decision_score(candidate) / candidate.cost
            if self.name in {"oarl_full", "oarl_scrambled_relations"}:
                score += 0.35 * self._complementarity_score(candidate) / candidate.cost
            return score
        if self.name == "oarl_complementarity_only":
            return self._decision_score(candidate) / candidate.cost + 0.35 * self._complementarity_score(candidate) / candidate.cost
        raise RuntimeError(f"no score for policy {self.name}")

    def _orbit_key(self, candidate: ProbeCandidate) -> tuple[Any, ...]:
        # Every item below is an input to the frozen OARL score.  Therefore equal keys
        # imply equal utility under current policy-visible state.
        probability, support, distance = self._candidate_prediction(candidate)
        key: list[Any] = [
            tuple(sorted(candidate.features.items())),
            round(candidate.cost, 12),
            round(probability, 12),
            round(support, 12),
            round(distance, 12),
        ]
        if self.name in {"oarl_full", "oarl_scrambled_relations"}:
            key.append(self._relation_state(candidate))
            key.append(round(self._complementarity_score(candidate), 12))
        return tuple(key)

    def choose(self) -> str:
        remaining = self._remaining()
        if not remaining:
            raise StopIteration
        self.planning_steps += 1
        self.raw_candidate_considerations += len(remaining)

        if self.name == "fixed":
            return min(remaining, key=lambda c: self.fixed_rank[c.candidate_id]).candidate_id
        if self.name == "random":
            return min(
                remaining,
                key=lambda c: (self._random_priority[c.candidate_id], self.fixed_rank[c.candidate_id]),
            ).candidate_id

        quotient = self.name in {"oarl_equivalence_only", "oarl_full", "oarl_scrambled_relations"}
        scored: list[tuple[float, int, str]] = []
        if quotient:
            groups: dict[tuple[Any, ...], list[ProbeCandidate]] = defaultdict(list)
            for candidate in remaining:
                groups[self._orbit_key(candidate)].append(candidate)
            self.orbit_evaluations += len(groups)
            for members in groups.values():
                representative = min(members, key=lambda c: self.fixed_rank[c.candidate_id])
                score = self._base_score(representative, remaining)
                self.utility_evaluations += 1
                for candidate in members:
                    scored.append((score, self.fixed_rank[candidate.candidate_id], candidate.candidate_id))
        else:
            self.orbit_evaluations += len(remaining)
            for candidate in remaining:
                score = self._base_score(candidate, remaining)
                self.utility_evaluations += 1
                scored.append((score, self.fixed_rank[candidate.candidate_id], candidate.candidate_id))

        scored.sort(key=lambda row: (-row[0], row[1], row[2]))
        return scored[0][2]

    def counters(self) -> dict[str, int]:
        return {
            "planning_steps": self.planning_steps,
            "raw_candidate_considerations": self.raw_candidate_considerations,
            "utility_evaluations": self.utility_evaluations,
            "orbit_evaluations": self.orbit_evaluations,
        }


def make_policy(
    name: str,
    candidate_views: Sequence[Mapping[str, Any]],
    *,
    costs: Mapping[str, float] | None = None,
    relation_graph: RelationGraph | None = None,
    seed: int = DEFAULT_STUDY_SEED,
) -> TrackRPolicy:
    costs = costs or {}
    candidates = [
        ProbeCandidate.from_policy_view(view, cost=float(costs.get(str(view["candidate_id"]), 1.0)))
        for view in candidate_views
    ]
    return TrackRPolicy(name, candidates, relation_graph=relation_graph, seed=seed)
