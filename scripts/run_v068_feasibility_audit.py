"""Feasibility-first correction of v068 on CONSUMED v067 public matrices.

No fixed 20/50 test budget, no whole-suite fallback. All methods satisfy
full development coverage (one witness or up to two) before scoring previously
inspected outer columns. NOT independent confirmation or OARL certification.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from time import perf_counter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "scripts/run_v067_development.py"
spec = importlib.util.spec_from_file_location("oarl_v067_feasibility", src)
if spec is None or spec.loader is None:
    raise RuntimeError("missing v067 source")
v067 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v067)
METHODS = ("greedy_cover", "rarest_first_greedy", "partition_refinement", "relation_proxy")
TARGETS = (1, 2)


def targets_for(dev: np.ndarray, redundancy: int) -> np.ndarray:
    if dev.ndim != 2 or redundancy < 1 or not np.all((dev == 0) | (dev == 1)):
        raise ValueError("binary 2D matrix and positive redundancy required")
    return np.minimum(redundancy, dev.sum(axis=0)).astype(np.int32)


def partition_gain(dev: np.ndarray, selected: list[int], remaining: np.ndarray) -> np.ndarray:
    """Classical mutant-pair split information; not a new RCC discovery."""
    scores = np.zeros(len(remaining), np.float64)
    classes: dict[bytes, list[int]] = {}
    for mutant in range(dev.shape[1]):
        key = dev[selected, mutant].tobytes() if selected else b""
        classes.setdefault(key, []).append(mutant)
    for members in classes.values():
        if len(members) < 2:
            continue
        positives = dev[np.ix_(remaining, members)].sum(axis=1).astype(float)
        scores += positives * (len(members) - positives)
    return scores


def reverse_delete(dev: np.ndarray, chosen: list[int], goal: np.ndarray) -> list[int]:
    counts = dev[chosen].sum(axis=0).astype(np.int32) if chosen else np.zeros(dev.shape[1], np.int32)
    kept = set(chosen)
    for idx in reversed(chosen):
        if np.all(counts - dev[idx] >= goal):
            kept.remove(idx)
            counts -= dev[idx]
    result = [idx for idx in chosen if idx in kept]
    if not np.all(dev[result].sum(axis=0) >= goal):
        raise AssertionError("pruning destroyed development coverage")
    return result


def pick(dev: np.ndarray, method: str, redundancy: int) -> tuple[list[int], dict]:
    if method not in METHODS:
        raise ValueError("unknown method")
    x = np.asarray(dev, dtype=np.uint8)
    goal = targets_for(x, redundancy)
    available = np.ones(len(x), dtype=bool)
    counts = np.zeros(x.shape[1], np.int32)
    selected: list[int] = []
    score_evals = pair_evals = 0
    frequency = x.sum(axis=0).astype(float)
    rarity = np.divide(1.0, np.sqrt(frequency), out=np.zeros_like(frequency), where=frequency > 0)
    while np.any(counts < goal):
        remaining = np.flatnonzero(available)
        deficient = counts < goal
        gains_all = x[remaining][:, deficient].sum(axis=1).astype(float)
        eligible = gains_all > 0
        candidates = remaining[eligible]
        if not len(candidates):
            raise AssertionError("no progress possible on feasible development target")
        gains = gains_all[eligible]
        score_evals += len(candidates)
        if method == "greedy_cover":
            scores = gains
        elif method == "rarest_first_greedy":
            scores = x[candidates][:, deficient].astype(float) @ rarity[deficient]
        else:
            splits = partition_gain(x, selected, candidates)
            pair_evals += len(candidates)
            if method == "partition_refinement":
                scores = splits
            else:
                scores = (0.6 * gains / max(float(np.max(gains)), 1.0)
                          + 0.4 * splits / max(float(np.max(splits)), 1.0))
        tied = np.flatnonzero(np.isclose(scores, np.max(scores), rtol=0., atol=1e-12))
        best_pos = min(tied, key=lambda j: (-float(gains[j]), int(candidates[j])))
        best = int(candidates[best_pos])
        selected.append(best)
        available[best] = False
        counts += x[best]
    pre_delete = len(selected)
    selected = reverse_delete(x, selected, goal)
    return selected, {
        "scored_candidates": score_evals,
        "pair_gain_candidates": pair_evals,
        "reverse_delete_checks": pre_delete,
        "development_goal_satisfied": bool(np.all(x[selected].sum(axis=0) >= goal)),
    }


def optimal_set_cover(dev: np.ndarray, redundancy: int, seconds: float) -> dict:
    """MILP lower bound/candidate, using greedy incumbent if HiGHS times out."""
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import csc_matrix
    x = np.asarray(dev, dtype=np.uint8)
    goal = targets_for(x, redundancy)
    initial, _ = pick(x, "greedy_cover", redundancy)
    active = goal > 0
    if not np.any(active):
        return {"status": "OPTIMAL_EMPTY", "solver_seconds": 0.,
                "lower_bound": 0., "mip_gap": 0., "selected": [],
                "n_selected": 0, "optimality_proven": True}
    start = perf_counter()
    result = milp(
        c=np.ones(len(x)),
        integrality=np.ones(len(x)),
        bounds=Bounds(np.zeros(len(x)), np.ones(len(x))),
        constraints=LinearConstraint(csc_matrix(x[:, active].T.astype(float)),
                                     lb=goal[active].astype(float),
                                     ub=np.full(int(active.sum()), np.inf)),
        options={"time_limit": float(seconds), "mip_rel_gap": 0.},
    )
    lower = getattr(result, "mip_dual_bound", None)
    gap = getattr(result, "mip_gap", None)
    record = {
        "status": str(result.message), "solver_seconds": perf_counter() - start,
        "lower_bound": float(lower) if lower is not None else None,
        "mip_gap": float(gap) if gap is not None else None,
        "greedy_upper_bound": len(initial),
        "selected": initial, "reference_source": "greedy_fallback",
    }
    if result.x is not None:
        solver_pick = np.flatnonzero(np.asarray(result.x) > .5).tolist()
        if not np.all(x[solver_pick].sum(axis=0) >= goal):
            raise AssertionError("invalid MILP result")
        record["solver_raw_incumbent_count"] = len(solver_pick)
        if len(solver_pick) < len(initial):
            record["selected"] = solver_pick
            record["reference_source"] = "milp_incumbent"
    record["n_selected"] = len(record["selected"])
    record["optimality_proven"] = bool(
        result.x is not None and result.status == 0
        and record["mip_gap"] is not None and record["mip_gap"] <= 1e-9
        and record["solver_raw_incumbent_count"] == record["n_selected"])
    return record


def evaluate(dev: np.ndarray, outer: np.ndarray, methods=METHODS,
             redundancies=TARGETS, *, mip_seconds: float = 4.) -> dict:
    if dev.ndim != 2 or outer.ndim != 2 or dev.shape[0] != outer.shape[0]:
        raise ValueError("misaligned matrices")
    complete_outer = np.any(outer, axis=0)
    arms = []
    for redundancy in redundancies:
        for method in methods:
            start = perf_counter()
            chosen, cost = pick(dev, method, redundancy)
            elapsed = perf_counter() - start
            detected = np.any(outer[chosen], axis=0) if chosen else np.zeros(outer.shape[1], bool)
            arms.append({
                "method": method, "redundancy_target": redundancy,
                "retained_count": len(chosen), "retained_fraction": len(chosen)/len(dev),
                "selected_indices": chosen, "development_coverage_verified": cost["development_goal_satisfied"],
                "outer_detectable_mutants": int(complete_outer.sum()),
                "outer_detected_mutants": int(detected.sum()),
                "outer_missed_mutants": int(np.sum(complete_outer & ~detected)),
                "algorithm_seconds": elapsed, **cost,
            })
        if mip_seconds > 0:
            optimal = optimal_set_cover(dev, redundancy, mip_seconds)
            chosen = optimal.pop("selected")
            detected = np.any(outer[chosen], axis=0) if chosen else np.zeros(outer.shape[1], bool)
            arms.append({
                "method": "set_cover_milp", "redundancy_target": redundancy,
                "retained_count": len(chosen), "retained_fraction": len(chosen)/len(dev),
                "selected_indices": chosen,
                "development_coverage_verified": True,
                "outer_detectable_mutants": int(complete_outer.sum()),
                "outer_detected_mutants": int(detected.sum()),
                "outer_missed_mutants": int(np.sum(complete_outer & ~detected)),
                **{("solver_"+k if k != "solver_seconds" else k): v for k, v in optimal.items()},
            })
    return {
        "eligible_tests": len(dev), "dev_mutants": dev.shape[1],
        "outer_mutants": outer.shape[1],
        "development_evidence_cells_shared": int(dev.size),
        "outer_is_already_consumed_v067": True,
        "real_test_execution_savings_measured": False,
        "arms": arms,
    }


def run(manifest_path: Path, data_root: Path, selection_lock_path: Path,
        *, mip_seconds: float = 4.) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lock = v067.require_frozen_selection(manifest, selection_lock_path)
    assets = v067.check_manifest(manifest, data_root, minimum=4)
    cases = []
    for asset, path in assets:
        types, names, ids, kills = v067.load_asset(path, asset)
        dev_mask = v067.split_mask(ids, str(asset["project"]), int(asset["fault"]))
        eligible = v067.canonical_active_rows(types, names, kills[:, dev_mask])
        if len(eligible) < 200:
            raise ValueError("frozen v067 admission inconsistency")
        analysis = evaluate(kills[eligible][:, dev_mask],
                            kills[eligible][:, ~dev_mask], mip_seconds=mip_seconds)
        cases.append({
            "project": asset["project"], "fault": asset["fault"],
            "asset_sha256": asset["sha256"], "analysis": analysis,
        })
    return {
        "protocol": "v068-feasibility-correction-development-v1",
        "status": "POST_HOC_CONSUMED_DATA_NOT_INDEPENDENT_CONFIRMATION",
        "source_commit": lock["upstream_commit"],
        "methods": list(METHODS) + ["set_cover_milp"],
        "redundancy_targets": list(TARGETS),
        "mip_time_limit_per_target_seconds": mip_seconds,
        "cost_note": "all arms use same supplied development evidence; real test-execution savings not measured",
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--selection-lock", type=Path,
                        default=Path("evidence/v067/SELECTION_LOCK.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mip-seconds", type=float, default=4.)
    args = parser.parse_args()
    if not (0 <= args.mip_seconds <= 60):
        parser.error("--mip-seconds must lie in [0,60]")
    if args.out.exists():
        parser.error("refusing to overwrite any prior result")
    result = run(args.manifest, args.data_root, args.selection_lock,
                 mip_seconds=args.mip_seconds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("CORRECTED DEVELOPMENT RUN (not independent confirmation):", args.out)


if __name__ == "__main__":
    main()
