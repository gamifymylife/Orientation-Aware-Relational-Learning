"""Validate v0.7 external corpus construction without executing OARL."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence" / "v07" / "external"
REGISTRY = BASE / "CANDIDATE_REGISTRY.json"
PREFLIGHT_DIR = BASE / "preflight"
LOCK = BASE / "CONFIRMATION_LOCK.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_preflight(doc: dict) -> list[str]:
    errors: list[str] = []
    cid = doc.get("case_id", "<unknown>")
    if doc.get("oarl_executed") is not False:
        errors.append(f"{cid}: OARL execution contamination")
    if not HEX40.fullmatch(str(doc.get("pre_fix_revision", ""))):
        errors.append(f"{cid}: invalid pre-fix revision")
    if not HEX40.fullmatch(str(doc.get("post_fix_revision", ""))):
        errors.append(f"{cid}: invalid post-fix revision")
    if doc.get("pre_fix_revision") == doc.get("post_fix_revision"):
        errors.append(f"{cid}: identical A/B revisions")
    replay = doc.get("historical_replay", {})
    if replay.get("stable_pre_fix_repeats", 0) < 3 or replay.get("stable_post_fix_repeats", 0) < 3:
        errors.append(f"{cid}: fewer than three stable A/B repeats")
    if replay.get("same_interface") is not True:
        errors.append(f"{cid}: common-interface requirement failed")
    if replay.get("negative_control_pass") is not True:
        errors.append(f"{cid}: negative control failed or absent")
    space = doc.get("candidate_space", {})
    if space.get("experiment_count", 0) < 1 or space.get("orientation_count", 0) < 1:
        errors.append(f"{cid}: empty experiment/orientation space")
    if not (0.8 <= float(space.get("validity_rate", 0.0)) <= 1.0):
        errors.append(f"{cid}: validity rate below 0.80")
    if not HEX64.fullmatch(str(space.get("manifest_sha256", ""))):
        errors.append(f"{cid}: candidate-space manifest not hash frozen")
    for key in ("adapter_sha256", "evaluator_sha256", "relation_generator_sha256"):
        if not HEX64.fullmatch(str(doc.get("frozen_artifacts", {}).get(key, ""))):
            errors.append(f"{cid}: {key} not frozen")
    leak = doc.get("leakage_checks", {})
    forbidden = (
        "pr_text_available_to_policy",
        "changed_files_available_to_policy",
        "known_witness_available_to_policy",
        "evaluator_labels_available_to_policy",
        "semantic_bug_labels_available_to_policy",
    )
    if any(leak.get(k) is not False for k in forbidden):
        errors.append(f"{cid}: policy leakage boundary failed")
    return errors


def main() -> int:
    data = json.loads(REGISTRY.read_text())
    errors: list[str] = []
    if data["oarl_external_outcomes_executed"] is not False:
        errors.append("registry says external OARL outcomes were executed")
    if data["confirmation_lock_created"] is not False:
        errors.append("registry claims confirmation lock during construction")
    if LOCK.exists():
        errors.append("CONFIRMATION_LOCK.json exists before construction is complete")

    sources = [c["source"] for c in data["candidates"]]
    if len(sources) != len(set(sources)):
        errors.append("duplicate source in candidate registry")
    if set(sources).intersection(data["prior_oarl_pilot_exclusions"]):
        errors.append("prior OARL pilot source present in v0.7 corpus")

    preflights = []
    if PREFLIGHT_DIR.exists():
        for path in sorted(PREFLIGHT_DIR.glob("*.json")):
            doc = json.loads(path.read_text())
            preflights.append(doc)
            errors.extend(validate_preflight(doc))

    eligible = [d for d in preflights if d.get("admission", {}).get("eligible") is True]
    report = {
        "phase": data["phase"],
        "candidate_entries": len(data["candidates"]),
        "preflight_manifests": len(preflights),
        "eligible_preflights": len(eligible),
        "minimum_cases_to_launch": data["minimum_cases_to_launch"],
        "ready_to_lock": len(eligible) >= data["minimum_cases_to_launch"] and not errors,
        "registry_sha256": sha256_file(REGISTRY),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
