"""Corrected feasibility-first apparatus checks; synthetic, not external evidence."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v068_feasibility', ROOT/'scripts/run_v068_feasibility_audit.py')
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def test_arbitrary_20_and_50_limits_are_absent():
    # Every row uniquely detects a different mutant: must retain all 80.
    dev=np.eye(80,dtype=np.uint8)
    for method in engine.METHODS:
        chosen,ledger=engine.pick(dev,method,1)
        assert len(chosen)==80
        assert ledger['development_goal_satisfied']


def test_reduces_when_small_full_cover_is_feasible():
    dev=np.asarray([[1,1,0,0],[0,0,1,1],[1,0,0,0],[0,0,1,0],[1,1,1,1]],dtype=np.uint8)
    for method in engine.METHODS:
        chosen,_=engine.pick(dev,method,1)
        assert len(chosen)<len(dev)
        assert np.all(np.any(dev[chosen],axis=0))
    ref=engine.optimal_set_cover(dev,1,1.0)
    assert ref['optimality_proven']
    assert ref['n_selected']==1


def test_two_witness_target_is_feasible_even_when_only_one_exists():
    dev=np.asarray([[1,0,0],[1,1,0],[0,1,0],[0,0,1]],dtype=np.uint8)
    goal=engine.targets_for(dev,2)
    assert goal.tolist()==[2,2,1]
    for method in engine.METHODS:
        chosen,_=engine.pick(dev,method,2)
        assert np.all(dev[chosen].sum(axis=0)>=goal)
    assert engine.optimal_set_cover(dev,2,1.0)['n_selected']==4


def test_holdout_cannot_change_selection():
    dev=np.asarray([[1,0,1,0],[0,1,0,1],[1,1,0,0],[0,0,1,1]],dtype=np.uint8)
    different_outer=[np.eye(4,dtype=np.uint8),np.ones((4,4),dtype=np.uint8)]
    outputs=[engine.evaluate(dev,x,mip_seconds=0) for x in different_outer]
    for a,b in zip(outputs[0]['arms'], outputs[1]['arms']):
        assert a['selected_indices']==b['selected_indices']
        assert a['retained_count']==b['retained_count']


def test_dev_coverage_does_not_guarantee_heldout_coverage():
    dev=np.asarray([[1,1,1],[1,0,0],[0,1,0]],dtype=np.uint8)
    outer=np.asarray([[0,0],[1,0],[0,1]],dtype=np.uint8)
    rows=engine.evaluate(dev,outer,mip_seconds=0)['arms']
    greedy=next(r for r in rows if r['method']=='greedy_cover' and r['redundancy_target']==1)
    assert greedy['development_coverage_verified']
    assert greedy['retained_count']==1
    assert greedy['outer_missed_mutants']==2


def test_reverse_delete_never_breaks_coverage():
    dev=np.asarray([[1,1],[1,0],[0,1]],dtype=np.uint8)
    assert engine.reverse_delete(dev,[0,1,2],engine.targets_for(dev,1))==[0]


def test_nonbinary_values_and_bad_targets_are_rejected():
    with pytest.raises(ValueError):
        engine.targets_for(np.asarray([[2,0]]),1)
    with pytest.raises(ValueError):
        engine.targets_for(np.ones((2,2)),0)
