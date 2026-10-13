"""Synthetic apparatus checks. These examples are NOT research results."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_v067_development.py"
spec = importlib.util.spec_from_file_location("v067_dev", MODULE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def write_matrix(root: Path, project="Chart", fault=2):
    root.mkdir(parents=True, exist_ok=True)
    p = root / f"{project}-{fault}.npz"
    np.savez_compressed(p, project=project, fault=fault,
                        test_types=np.asarray(["dev"] * 3),
                        test_names=np.asarray(["a", "b", "c"]),
                        mutant_ids=np.asarray(["m1", "m2", "m3", "m4"]),
                        kills=np.asarray([[1,0,1,0],[1,0,0,1],[0,1,0,1]], dtype=np.uint8))
    asset = {"path": p.name, "project": project, "fault": fault,
             "sha256": engine.sha256(p), "upstream_url": "https://example.org/pinned", "upstream_commit": "commit123"}
    return p, asset


def test_rejects_burned_faults_and_duplicate_assets(tmp_path):
    _, asset = write_matrix(tmp_path, "Lang", 33)
    with pytest.raises(ValueError, match="burned"):
        engine.check_manifest({"schema": engine.SCHEMA, "assets": [asset]}, tmp_path, minimum=1)
    _, other = write_matrix(tmp_path, "Chart", 2)
    with pytest.raises(ValueError, match="duplicate"):
        engine.check_manifest({"schema": engine.SCHEMA, "assets": [other, other]}, tmp_path, minimum=1)


def test_digest_and_path_guard(tmp_path):
    p, a = write_matrix(tmp_path)
    a["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        engine.check_manifest({"schema": engine.SCHEMA, "assets": [a]}, tmp_path, minimum=1)
    a["sha256"] = engine.sha256(p)
    a["path"] = "../outside.npz"
    with pytest.raises(ValueError, match="unsafe"):
        engine.check_manifest({"schema": engine.SCHEMA, "assets": [a]}, tmp_path, minimum=1)


def test_minimum_new_fault_gate(tmp_path):
    _, a = write_matrix(tmp_path)
    with pytest.raises(ValueError, match="at least 3"):
        engine.check_manifest({"schema": engine.SCHEMA, "assets": [a]}, tmp_path)


def test_load_and_bit_validation(tmp_path):
    p, a = write_matrix(tmp_path)
    assert engine.load_asset(p,a)[3].shape == (3,4)
    np.savez_compressed(p, project="Chart", fault=2,
                        test_types=["dev"], test_names=["a"], mutant_ids=["1","2","3","4"],
                        kills=np.asarray([[2,0,0,0]]))
    with pytest.raises(ValueError, match="binary"):
        engine.load_asset(p,a)


def test_heldout_never_controls_proposals_or_selection():
    dev = np.asarray([[1,0,0],[1,0,0],[0,1,1]], dtype=np.uint8)
    h1 = np.asarray([[1,0],[0,1],[1,1]], dtype=np.uint8)
    h2 = np.asarray([[1,0],[1,0],[1,1]], dtype=np.uint8)
    a, b = engine.analyze_split(dev,h1), engine.analyze_split(dev,h2)
    for method in engine.METHODS:
        x, y = a["arms"][method], b["arms"][method]
        assert x["selected_local_rows"] == y["selected_local_rows"]
        assert x["classes"] == y["classes"]
        assert x["development_planning_score_evaluations"] == y["development_planning_score_evaluations"]
    assert a["arms"]["exact_development"]["heldout_false_merge_pairs"] == 1
    assert b["arms"]["exact_development"]["heldout_false_merge_pairs"] == 0


def test_detects_downstream_missed_mutant_not_only_total_coverage():
    dev = np.asarray([[1,0],[1,0],[0,1]], dtype=np.uint8)
    held = np.asarray([[0,0,1],[1,0,0],[0,1,0]], dtype=np.uint8)
    result = engine.analyze_split(dev,held,budget=2)
    # Raw and quotient happen to choose the same earliest canonical representative here.
    assert result["arms"]["exact_development"]["heldout_false_merge_pairs"] == 1
    assert result["real_execution_savings_measured"] is False
    assert result["oarl_specific_method_evaluated"] is False
