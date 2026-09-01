import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence" / "v07" / "external"
EXPANSION = BASE / "METADATA_EXPANSION_001.json"
REGISTRY = BASE / "CANDIDATE_REGISTRY.json"


def load(path: Path):
    return json.loads(path.read_text())


def test_metadata_expansion_is_pre_oarl_only():
    data = load(EXPANSION)
    assert data["phase"] == "METADATA_ONLY_CANDIDATE_EXPANSION"
    assert data["oarl_executed"] is False
    assert all(c["oarl_executed"] is False for c in data["candidates"])
    assert all(c["status"] == "METADATA_ONLY_NEEDS_ACTUAL_REVISION_REPLAY" for c in data["candidates"])


def test_metadata_expansion_count_and_scores():
    data = load(EXPANSION)
    rows = data["candidates"]
    assert data["selected_count"] == len(rows)
    assert len(rows) >= 20
    assert all(c["score"] >= 6 for c in rows)
    assert all(c["score_components"] for c in rows)


def test_metadata_expansion_sources_are_unique_and_were_fresh_at_selection():
    data = load(EXPANSION)
    registry = load(REGISTRY)
    sources = [c["source"] for c in data["candidates"]]
    assert len(sources) == len(set(sources))
    # Promoted expansion cases may now appear in the live registry. Freshness is
    # therefore checked against the pre-expansion/core lineage only.
    core_sources = {
        c["source"]
        for c in registry["candidates"]
        if c.get("source_status") != "v07_metadata_expansion"
    }
    assert not set(sources).intersection(core_sources)
    assert not set(sources).intersection(registry["prior_oarl_pilot_exclusions"])


def test_promoted_expansion_cases_remain_traceable_to_frozen_queue():
    data = load(EXPANSION)
    registry = load(REGISTRY)
    expansion_sources = {c["source"] for c in data["candidates"]}
    promoted = [c for c in registry["candidates"] if c.get("source_status") == "v07_metadata_expansion"]
    assert promoted
    assert all(c["source"] in expansion_sources for c in promoted)
    assert all(c["oarl_executed"] is False for c in promoted)


def test_metadata_expansion_repository_caps_and_breadth():
    data = load(EXPANSION)
    counts = Counter(c["repository"] for c in data["candidates"])
    assert counts == data["selected_by_repository"]
    assert all(n <= 12 for n in counts.values())
    assert len(counts) >= 6


def test_metadata_expansion_does_not_count_as_admission():
    registry = load(REGISTRY)
    assert registry["confirmation_lock_created"] is False
    assert registry["oarl_external_outcomes_executed"] is False
    admitted = [c for c in registry["candidates"] if c["v07_status"] == "ADMITTED_LOCK_READY"]
    assert len(admitted) < registry["minimum_cases_to_launch"]
