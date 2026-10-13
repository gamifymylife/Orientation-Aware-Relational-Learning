"""OARL v0.6.7: development-only, leak-aware mutation-equivalence screen.

No networking, subprocess execution, automatic dataset acquisition, or heldout tuning.
Uninspected *new* mutation matrices are required. Not an independent evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = "oarl-v067-development-manifest-1"
BURNED = {("closure", 118), ("lang", 33), ("math", 22), ("time", 6)}
METHODS = ("raw", "exact_development", "near_hamming_1")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_manifest(manifest: dict[str, Any], data_root: Path, *, minimum: int = 3) -> list[tuple[dict[str, Any], Path]]:
    if manifest.get("schema") != SCHEMA or not isinstance(manifest.get("assets"), list):
        raise ValueError("unexpected schema or missing assets")
    if len(manifest["assets"]) < minimum:
        raise ValueError(f"at least {minimum} *new* assets required; no science run")
    seen: set[tuple[str, int]] = set()
    root = data_root.resolve(strict=True)
    resolved = []
    for asset in manifest["assets"]:
        if not isinstance(asset, dict):
            raise ValueError("asset must be an object")
        project = str(asset["project"])
        fault = int(asset["fault"])
        identity = (project.casefold(), fault)
        if identity in BURNED or identity in seen:
            raise ValueError(f"burned or duplicate project-fault: {project}-{fault}")
        seen.add(identity)
        relative = Path(str(asset["path"]))
        if relative.is_absolute() or not relative.parts or any(p in ("..", ".") for p in relative.parts):
            raise ValueError("unsafe asset path")
        candidate = (root / relative).resolve(strict=True)
        if not candidate.is_relative_to(root) or candidate.suffix != ".npz":
            raise ValueError("invalid asset location / extension")
        recorded_sha = str(asset.get("sha256", "")).lower()
        if len(recorded_sha) != 64 or any(c not in "0123456789abcdef" for c in recorded_sha):
            raise ValueError("a 64-digit sha256 is mandatory")
        if sha256(candidate) != recorded_sha:
            raise ValueError(f"SHA-256 mismatch: {relative}")
        if not str(asset.get("upstream_url", "")).startswith("https://") or not str(asset.get("upstream_commit", "")):
            raise ValueError("upstream URL and immutable source revision required")
        resolved.append((asset, candidate))
    return resolved


def load_asset(path: Path, asset: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as src:
        required = {"project", "fault", "test_types", "test_names", "mutant_ids", "kills"}
        if not required.issubset(src.files):
            raise ValueError("missing mutation matrix fields")
        project, fault = str(src["project"].item()), int(src["fault"].item())
        if project.casefold() != str(asset["project"]).casefold() or fault != int(asset["fault"]):
            raise ValueError("asset identity disagrees with manifest")
        types = np.asarray(src["test_types"], dtype=str)
        names = np.asarray(src["test_names"], dtype=str)
        ids = np.asarray(src["mutant_ids"], dtype=str)
        kills = np.asarray(src["kills"])
        if kills.ndim != 2 or kills.shape != (len(names), len(ids)) or len(types) != len(names):
            raise ValueError("invalid kill-matrix dimensions")
        if len(ids) < 4 or len(names) < 1 or len(set(ids.tolist())) != len(ids):
            raise ValueError("too few or duplicate identifiers")
        if not np.all((kills == 0) | (kills == 1)):
            raise ValueError("kill matrix must be binary")
        return types, names, ids, kills.astype(np.uint8)


def split_mask(ids: np.ndarray, project: str, fault: int) -> np.ndarray:
    mask = np.array([hashlib.sha256(f"v067-develop:{project.casefold()}:{fault}:{mid}".encode()).digest()[0] < 128 for mid in ids], dtype=bool)
    if not np.any(mask) or np.all(mask):
        raise ValueError("empty split; reject asset")
    return mask


def canonical_active_rows(types: np.ndarray, names: np.ndarray, development: np.ndarray) -> np.ndarray:
    seen: set[tuple[str, str]] = set()
    chosen = []
    for i, key in enumerate(zip(types.tolist(), names.tolist())):
        if key not in seen:
            seen.add(key)
            if np.any(development[i]):
                chosen.append(i)
    return np.asarray(chosen, dtype=int)


def groups_for(development: np.ndarray, method: str) -> list[list[int]]:
    if method == "raw":
        return [[i] for i in range(development.shape[0])]
    if method == "exact_development":
        groups: dict[bytes, list[int]] = {}
        for i, row in enumerate(development):
            groups.setdefault(row.tobytes(), []).append(i)
        return list(groups.values())
    if method == "near_hamming_1":
        # Greedy complete-link partition: every new member must be <=1 bit away
        # from every existing member. Deliberately unsafe negative control.
        result: list[list[int]] = []
        for i, row in enumerate(development):
            for group in result:
                if all(np.count_nonzero(row != development[j]) <= 1 for j in group):
                    group.append(i)
                    break
            else:
                result.append([i])
        return result
    raise ValueError(f"unknown baseline: {method}")


def greedy_on_development(groups: list[list[int]], development: np.ndarray, budget: int = 20) -> tuple[list[int], int]:
    if budget < 1:
        raise ValueError("budget must be positive")
    candidates = sorted(min(group) for group in groups)
    covered = np.zeros(development.shape[1], dtype=bool)
    selected, calls = [], 0
    while len(selected) < budget and candidates:
        scored = [(int(np.count_nonzero((development[i] != 0) & ~covered)), i) for i in candidates]
        calls += len(scored)
        gain, index = min(scored, key=lambda pair: (-pair[0], pair[1]))
        if gain == 0:
            break
        selected.append(index)
        covered |= development[index].astype(bool)
        candidates.remove(index)
    return selected, calls


def false_merge_pairs(groups: list[list[int]], heldout: np.ndarray) -> int:
    return sum(int(np.any(heldout[left] != heldout[right]))
               for group in groups for p, left in enumerate(group) for right in group[p + 1:])


def analyze_split(development: np.ndarray, heldout: np.ndarray, *, budget: int = 20) -> dict[str, Any]:
    """Proposal uses development ONLY; holdout used strictly after all proposals."""
    if development.ndim != 2 or heldout.ndim != 2 or development.shape[0] != heldout.shape[0]:
        raise ValueError("invalid split")
    plans = {method: (groups_for(development, method)) for method in METHODS}
    selections = {method: greedy_on_development(plans[method], development, budget) for method in METHODS}
    raw_selected = selections["raw"][0]
    raw_hits = np.any(heldout[raw_selected], axis=0) if raw_selected else np.zeros(heldout.shape[1], dtype=bool)
    arms = {}
    for method in METHODS:
        groups = plans[method]
        selected, score_calls = selections[method]
        hits = np.any(heldout[selected], axis=0) if selected else np.zeros(heldout.shape[1], dtype=bool)
        pairs = sum(len(g) * (len(g) - 1) // 2 for g in groups)
        false = false_merge_pairs(groups, heldout)
        arms[method] = {
            "classes": len(groups), "compression": 1 - len(groups) / max(development.shape[0], 1),
            "proposed_pairs": pairs, "heldout_false_merge_pairs": false,
            "heldout_pair_precision": (pairs - false) / pairs if pairs else None,
            "selected_local_rows": selected, "selected_count": len(selected),
            "development_planning_score_evaluations": score_calls,
            "heldout_covered_mutants": int(np.sum(hits)),
            "heldout_missed_vs_raw": int(np.sum(raw_hits & ~hits)),
            "heldout_new_vs_raw": int(np.sum(~raw_hits & hits)),
            "preserved_raw_holdout_detection_vector": bool(np.array_equal(hits, raw_hits)),
        }
    return {"eligible_tests": development.shape[0],
            "development_mutants": development.shape[1],
            "heldout_mutants": heldout.shape[1],
            "development_evidence_cells_shared_by_all_arms": int(development.size),
            "real_execution_savings_measured": False,
            "oarl_specific_method_evaluated": False,
            "arms": arms}


def run(manifest_path: Path, data_root: Path, *, budget: int = 20) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = check_manifest(manifest, data_root)
    rows = []
    for asset, path in assets:
        types, names, ids, kills = load_asset(path, asset)
        mask = split_mask(ids, str(asset["project"]), int(asset["fault"]))
        canonical = canonical_active_rows(types, names, kills[:, mask])
        if len(canonical) < 200:
            raise ValueError(f"{asset['project']}-{asset['fault']} has only {len(canonical)} eligible tests (min 200)")
        result = analyze_split(kills[canonical][:, mask], kills[canonical][:, ~mask], budget=budget)
        rows.append({"project": asset["project"], "fault": asset["fault"],
                     "asset_sha256": asset["sha256"], "upstream_commit": asset["upstream_commit"],
                     "source_claim": asset["upstream_url"], "metrics": result})
    return {"protocol": "v067-development-1", "outcome": "DEVELOPMENT_ONLY_NOT_CONFIRMATORY",
            "evaluation_secret": "NONE: public fault data; split only protects procedural leakage",
            "frozen_methods": list(METHODS), "mutant_split": "sha256 v067-develop 1-byte threshold 128",
            "greedy_test_budget": budget, "matrices": rows,
            "claim": "No OARL-specific safe discovery or real execution-cost advantage tested."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    # Do not overwrite earlier runs; their evidence and consumed holdouts stay immutable.
    if args.out.exists():
        parser.error(f"output already exists: {args.out}")
    report = run(args.manifest, args.data_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"DEVELOPMENT_ONLY; recorded {len(report['matrices'])} matrices in {args.out}")


if __name__ == "__main__":
    main()
