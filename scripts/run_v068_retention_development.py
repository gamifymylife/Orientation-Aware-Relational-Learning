"""Development-only decision-preserving test retention feasibility study.

Reuses *consumed* v0.6.7 mutation matrices. NOT confirmatory science.
No source downloads, execution of tests, or new external data acquisition.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
V067 = BASE / 'scripts/run_v067_development.py'
spec = importlib.util.spec_from_file_location('oarl_v067_frozen', V067)
if spec is None or spec.loader is None:
    raise RuntimeError('v0.6.7 source unavailable')
v067 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v067)

METHODS = ('greedy_cover', 'dominance_cover', 'greedy_multicover2', 'partition_greedy', 'metadata_diversified', 'relation_aware')
BUDGETS = (20, 50)


def split_internal(mutant_ids: np.ndarray, project: str, fault: int, outer_mask: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    # Split *only v067 development columns* into design and developmental validation.
    # Uses precommitted fixed hash. The previous v067 outer evaluator is consumed.
    hashes = np.asarray([
        hashlib.sha256(f'v068-validation:{project.casefold()}:{fault}:{mid}'.encode()).digest()[0]
        for mid in mutant_ids], dtype=np.int16)
    train = outer_mask & (hashes >= 64)
    validate = outer_mask & (hashes < 64)
    if not train.any() or not validate.any():
        raise ValueError('empty inner partition')
    return train, validate


def partition_split_gain(train: np.ndarray, selected: list[int], remaining: np.ndarray) -> np.ndarray:
    """For each test, count novel *pairs of mutants* separated under observation history.

    This is established partition refinement / information gain, NOT a new RCC theorem.
    """
    m = train.shape[1]
    keys: dict[bytes,list[int]] = {}
    for mutant in range(m):
        key = train[selected, mutant].tobytes() if selected else b''
        keys.setdefault(key, []).append(mutant)
    score = np.zeros(len(remaining), dtype=np.float64)
    for group in keys.values():
        if len(group) < 2:
            continue
        counts = np.asarray(train[remaining][:, group].sum(axis=1), dtype=np.float64)
        score += counts * (len(group) - counts)
    return score


def non_dominated_pool(train: np.ndarray) -> tuple[set[int], int]:
    """Classical exact development-signature subset pruning; equality ties favor low IDs."""
    vectors = [int.from_bytes(np.packbits(row, bitorder='little').tobytes(), 'little') for row in train]
    ordered = sorted(range(len(vectors)), key=lambda i: (-vectors[i].bit_count(),i))
    retained: list[int] = []
    comparisons = 0
    for i in ordered:
        dominated = False
        for j in retained:
            comparisons += 1
            if vectors[i] & vectors[j] == vectors[i]:
                dominated = True
                break
        if not dominated:
            retained.append(i)
    return set(retained), comparisons


def greedy_retention(train: np.ndarray, test_types: np.ndarray, *, budget: int, method: str) -> tuple[list[int],dict]:
    if method not in METHODS or train.ndim != 2 or train.shape[0] != len(test_types) or budget < 1:
        raise ValueError('invalid selection input')
    x = np.asarray(train, dtype=np.uint8)
    n, m = x.shape
    chosen: list[int] = []
    available = np.ones(n, dtype=bool)
    witness_counts = np.zeros(m, dtype=np.int32)
    type_counts: dict[str,int] = {}
    score_evaluations, pair_gain_evaluations = 0, 0
    allowed, dominance_checks = non_dominated_pool(x) if method == 'dominance_cover' else (None,0)
    for _ in range(min(budget, n)):
        remaining = np.flatnonzero(available)
        if allowed is not None and any(int(i) in allowed for i in remaining):
            remaining = np.asarray([i for i in remaining if int(i) in allowed],dtype=int)
        sub = x[remaining]
        unseen_gain = sub[:, witness_counts == 0].sum(axis=1).astype(float)
        # Additional witness coverage for a known mutant, bounded to two.
        two_gain = sub[:, witness_counts < 2].sum(axis=1).astype(float)
        rarity = sub.sum(axis=1).astype(float)
        score_evaluations += len(remaining)
        if method in ('greedy_cover', 'dominance_cover'):
            score = unseen_gain
        elif method == 'greedy_multicover2':
            score = two_gain
        elif method == 'metadata_diversified':
            score = unseen_gain + 0.01 * np.asarray(
                [1.0/(1 + type_counts.get(str(test_types[i]),0)) for i in remaining]
            )
        elif method in ('partition_greedy', 'relation_aware'):
            split = partition_split_gain(x, chosen, remaining)
            pair_gain_evaluations += len(remaining)
            if method == 'partition_greedy':
                score = split
            else:
                # Fixed weights; do NOT tune on consumed outer evaluation.
                max_cover = max(float(np.max(unseen_gain)), 1.0)
                max_split = max(float(np.max(split)), 1.0)
                novel_type = np.asarray([1.0 if str(test_types[i]) not in type_counts else 0.0 for i in remaining])
                score = 0.6*unseen_gain/max_cover + 0.4*split/max_split + 0.01*novel_type
        if np.max(score) <= 0:
            # Matched deterministic fill after target saturates; no convenient
            # early stopping that gives a comparator fewer retained tests.
            score = rarity
        best = int(remaining[int(np.argmax(score))])
        chosen.append(best)
        available[best] = False
        witness_counts += x[best]
        t = str(test_types[best]); type_counts[t] = type_counts.get(t,0)+1
    return chosen, {'scored_candidates': int(score_evaluations),
                    'dominance_comparisons': dominance_checks,
                    'pair_gain_candidate_evaluations': int(pair_gain_evaluations)}


def observed_kills(x: np.ndarray, selected: list[int]) -> np.ndarray:
    if not selected:
        return np.zeros(x.shape[1], dtype=bool)
    return np.any(x[selected], axis=0)


def evaluate_case(test_types: np.ndarray, train: np.ndarray, val: np.ndarray,
                  outer_holdout: np.ndarray) -> dict:
    if not (train.ndim == val.ndim == outer_holdout.ndim == 2) or not (
        train.shape[0] == val.shape[0] == outer_holdout.shape[0] == len(test_types)):
        raise ValueError('misaligned inputs')
    full_val = np.any(val, axis=0)
    full_outer = np.any(outer_holdout, axis=0)
    n = train.shape[0]
    rows = []
    for budget in BUDGETS:
        if budget >= n:
            raise ValueError('benchmark retention budget exceeds candidate tests')
        for method in METHODS:
            selected, costs = greedy_retention(train, test_types, budget=budget, method=method)
            validation_misses = int(np.count_nonzero(full_val & ~observed_kills(val, selected)))
            abstain = validation_misses > 0
            retained = list(range(n)) if abstain else selected
            resulting = observed_kills(outer_holdout, retained)
            missed = int(np.count_nonzero(full_outer & ~resulting))
            rows.append({
                'method': method, 'budget': budget, 'proposed_tests': len(selected),
                'retained_tests': len(retained), 'retained_fraction': len(retained)/n,
                'abstained_to_full_suite': abstain,
                'inner_validation_missed_detectable_mutants_before_abstention': validation_misses,
                'outer_missed_detectable_mutants': missed,
                'outer_detectable_mutants': int(full_outer.sum()),
                'outer_coverage_fraction': (int(resulting.sum())/int(full_outer.sum())) if full_outer.any() else 1.0,
                'distinct_types_retained': len(set(map(str, test_types[retained]))),
                'planning_scored_candidates': costs['scored_candidates'],
                'pair_gain_candidate_evaluations': costs['pair_gain_candidate_evaluations'],
                'dominance_comparisons': costs['dominance_comparisons'],
                'full_inner_data_evidence_cells': int(n*(train.shape[1]+val.shape[1])),
                'real_execution_savings_measured': False,
            })
    return {'n_tests':n,'train_mutants':train.shape[1], 'internal_validation_mutants':val.shape[1],
            'consumed_outer_mutants':outer_holdout.shape[1], 'results':rows}


def run(manifest_path: Path, data_root: Path, selection_lock_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    lock = v067.require_frozen_selection(manifest, selection_lock_path)
    assets = v067.check_manifest(manifest, data_root, minimum=4)
    rows = []
    for asset,path in assets:
        test_types,names,ids,kills = v067.load_asset(path,asset)
        mask = v067.split_mask(ids,str(asset['project']),int(asset['fault']))
        eligible = v067.canonical_active_rows(test_types,names,kills[:,mask])
        if len(eligible) < 200:
            raise ValueError('v0.6.7 admission inconsistency; no selective evaluation')
        train_mask,val_mask = split_internal(ids,str(asset['project']),int(asset['fault']),mask)
        result = evaluate_case(test_types[eligible],kills[eligible][:,train_mask],
                               kills[eligible][:,val_mask],kills[eligible][:,~mask])
        rows.append({'project':asset['project'],'fault':asset['fault'],
                     'asset_sha256':asset['sha256'], 'analysis':result})
    return {'protocol':'v068-development-comparison-v01',
            'status':'CONSUMED_V067_DATA_DEVELOPMENT_ONLY_NO_INDEPENDENT_CONFIRMATION',
            'source_commit':lock['upstream_commit'],'methods':list(METHODS),
            'budgets':list(BUDGETS), 'cost_note':'full inner evidence accessed by all; no real test executions measured',
            'safety_note':'inner validation abstention is not a certificate on unseen faults',
            'cases':rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,required=True)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--selection-lock',type=Path,default=Path('evidence/v067/SELECTION_LOCK.json'))
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('do not overwrite consumed results')
    result=run(args.manifest,args.data_root,args.selection_lock)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(f'DEVELOPMENT_ONLY: {len(result["cases"])} public, previously exposed cases; result {args.out}')


if __name__=='__main__':
    main()
