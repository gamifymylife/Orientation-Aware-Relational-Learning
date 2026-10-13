"""v0.6.7 admission safety; all data in these tests are synthetic."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
runner_spec = importlib.util.spec_from_file_location("v067_development", ROOT / "scripts/run_v067_development.py")
runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(runner)


def fixture(tmp_path: Path, eligible: int):
    upstream_commit = "a" * 40
    assets, locked = [], []
    root = tmp_path / "data"
    root.mkdir()
    for index in range(4):
        project = f"Prospective{index}"
        fault = index + 1
        path = root / f"case{index}.npz"
        n = 230
        ids = np.asarray([f"m-{j}" for j in range(40)], dtype=str)
        split = runner.split_mask(ids, project, fault)
        kills = np.zeros((n, len(ids)), dtype=np.uint8)
        if index < eligible:
            kills[:, split] = 1
            kills[::2, ~split] = 1
        np.savez_compressed(path, project=project, fault=fault,
                            test_types=np.asarray(["dev"] * n),
                            test_names=np.asarray([f"test-{i}" for i in range(n)]),
                            mutant_ids=ids, kills=kills)
        source = f"resources/matrices/{project}/{project}.{fault}f.big.all.Matrix.csv"
        blob = f"{index + 1:040x}"
        assets.append({
            "project": project, "fault": fault, "path": path.name,
            "sha256": runner.sha256(path), "source_relative_path": source,
            "source_git_blob_sha": blob, "upstream_commit": upstream_commit,
            "upstream_url": f"https://example.org/pinned/{source}"
        })
        locked.append({"project": project, "fault": fault, "source_relative_path": source,
                       "source_git_blob_sha": blob})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema": runner.SCHEMA, "assets": assets}))
    selection = tmp_path / "SELECTION_LOCK.json"
    selection.write_text(json.dumps({"schema": "oarl-v067-source-selection-lock-1",
                                     "upstream_commit": upstream_commit,
                                     "candidates": locked}))
    return manifest, root, selection


def test_succeeds_with_three_precommitted_eligible_cases(tmp_path):
    m, root, selection = fixture(tmp_path, eligible=3)
    r = runner.run(m, root, selection)
    assert r["eligible_count"] == 3
    assert r["outcome"] == "DEVELOPMENT_ONLY_NOT_CONFIRMATORY"
    assert len(r["matrices"]) == 4
    assert "metrics" not in r["matrices"][3]
    assert r["matrices"][3]["status"] == "DEVELOPMENT_ONLY_INELIGIBLE_NOT_SCORED"
    assert all("metrics" in x for x in r["matrices"][:3])


def test_does_not_score_any_holdout_when_eligibility_gate_fails(tmp_path):
    m, root, selection = fixture(tmp_path, eligible=2)
    r = runner.run(m, root, selection)
    assert r["outcome"] == "STOP_INSUFFICIENT_ELIGIBLE_MATRICES"
    assert r["eligible_count"] == 2
    assert all("metrics" not in row for row in r["matrices"])


def test_burns_changed_selection_instead_of_swapping_failed_case(tmp_path):
    m, root, selection = fixture(tmp_path, eligible=3)
    data = json.loads(m.read_text())
    data["assets"][3]["fault"] = 999
    m.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="differs from the frozen"):
        runner.run(m, root, selection)


def test_upstream_commit_must_match_lock(tmp_path):
    m, root, selection = fixture(tmp_path, eligible=3)
    data = json.loads(m.read_text())
    data["assets"][2]["upstream_commit"] = "b" * 40
    m.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="commit differs"):
        runner.run(m, root, selection)
