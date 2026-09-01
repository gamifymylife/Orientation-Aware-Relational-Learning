import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence" / "v07" / "external" / "CANDIDATE_REGISTRY.json"
LOCK = ROOT / "evidence" / "v07" / "external" / "CONFIRMATION_LOCK.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load_registry():
    return json.loads(REGISTRY.read_text())


def test_v07_corpus_remains_pre_oarl():
    data = load_registry()
    assert data["phase"] == "CORPUS_CONSTRUCTION_PRE_OARL"
    assert data["oarl_external_outcomes_executed"] is False
    assert data["confirmation_lock_created"] is False
    assert data["counts"]["v07_external_oarl_runs"] == 0
    assert all(c["oarl_executed"] is False for c in data["candidates"])


def test_confirmation_lock_does_not_exist_during_construction():
    assert not LOCK.exists()


def test_prior_oarl_pilot_cases_are_excluded():
    data = load_registry()
    sources = {c["source"] for c in data["candidates"]}
    assert not sources.intersection(data["prior_oarl_pilot_exclusions"])


def test_candidate_sources_are_unique():
    data = load_registry()
    sources = [c["source"] for c in data["candidates"]]
    assert len(sources) == len(set(sources))


def test_registry_counts_are_self_consistent():
    data = load_registry()
    rows = data["candidates"]
    counts = data["counts"]
    assert counts["candidate_entries"] == len(rows)
    assert counts["actual_revision_replay_verified"] == sum(
        c["v07_status"] == "REPLAY_VERIFIED_NEEDS_V07_PREFLIGHT" for c in rows
    )
    assert counts["unreviewed"] == sum(
        c["v07_status"] == "NEEDS_ACTUAL_REVISION_REPLAY" for c in rows
    )
    assert counts["rejected"] == sum(c["v07_status"].startswith("REJECTED_") for c in rows)


def test_replay_verified_cases_have_frozen_exact_provenance():
    data = load_registry()
    verified = [c for c in data["candidates"] if c["v07_status"] == "REPLAY_VERIFIED_NEEDS_V07_PREFLIGHT"]
    assert len(verified) == data["counts"]["actual_revision_replay_verified"]
    for case in verified:
        assert case["repository"]
        assert HEX40.fullmatch(case["pre_fix_revision"])
        assert HEX40.fullmatch(case["post_fix_revision"])
        assert case["pre_fix_revision"] != case["post_fix_revision"]
        assert case["stable_repeats"] >= 3
        assert HEX64.fullmatch(case["replay_evidence_sha256"])
        assert HEX40.fullmatch(case["source_eligibility_blob_sha"])


def test_source_candidate_pool_is_blob_pinned():
    data = load_registry()
    assert HEX40.fullmatch(data["source_program"]["artifact_blob_sha"])


def test_launch_threshold_is_not_claimed_from_candidates_alone():
    data = load_registry()
    admitted = [c for c in data["candidates"] if c["v07_status"] == "ADMITTED_LOCK_READY"]
    assert len(admitted) < data["minimum_cases_to_launch"]
    assert data["confirmation_lock_created"] is False
