"""Synthetic tests: no external scientific evidence."""
import importlib.util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v068',ROOT/'scripts/run_v068_retention_development.py')
v068=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v068)


def test_inner_split_cannot_intersect_outer_holdout():
    ids=np.asarray([f'm{i}' for i in range(1000)])
    outer=np.asarray([i%2==0 for i in range(1000)])
    design,validation=v068.split_internal(ids,'Chart',1,outer)
    assert not np.any(design & validation)
    assert not np.any((design|validation)&~outer)
    assert np.array_equal(design|validation,outer)


def test_methods_never_see_outer_eval_in_selection():
    train=np.asarray([[1,0,0,1],[0,1,0,0],[0,0,1,0],[1,1,0,0],[0,1,1,0]],dtype=np.uint8)
    types=np.asarray(['dev','randoop','dev','randoop','dev'])
    for method in v068.METHODS:
        a,cost=v068.greedy_retention(train,types,budget=3,method=method)
        assert len(a)==len(set(a))==3
        assert max(a)<len(types)
        assert cost['scored_candidates']>0
        assert isinstance(a,list)
    # Evaluation passes outer holdout only after proposals; selector has no holdout arg.
    assert v068.greedy_retention(train,types,budget=3,method='relation_aware')[0] == v068.greedy_retention(train,types,budget=3,method='relation_aware')[0]


def test_full_suite_abstention_prevents_inner_validation_loss():
    types=np.asarray(['a','b','c','d']*15)
    train=np.asarray([[i%5==j for j in range(10)] for i in range(60)],dtype=np.uint8)
    val=np.eye(60,dtype=np.uint8)
    outer=val.copy()
    res=v068.evaluate_case(types,train,val,outer)
    assert all(x['abstained_to_full_suite'] for x in res['results'])
    assert all(x['retained_tests']==60 for x in res['results'])
    assert all(x['outer_missed_detectable_mutants']==0 for x in res['results'])


def test_no_universal_certificate_claim_if_inner_validation_passes():
    types=np.asarray(['dev']*60)
    train=np.ones((60,10),dtype=np.uint8)
    val=np.ones((60,5),dtype=np.uint8)
    outer=np.eye(60,dtype=np.uint8)
    res=v068.evaluate_case(types,train,val,outer)
    assert any(x['outer_missed_detectable_mutants']>0 and not x['abstained_to_full_suite'] for x in res['results'])


def test_dominance_drops_identical_and_subset_signatures():
    dev=np.asarray([[1,1,1],[1,1,0],[1,1,1],[0,0,1]],dtype=np.uint8)
    pool,checks=v068.non_dominated_pool(dev)
    assert pool=={0}
    assert checks>0


def test_partition_gain_has_independent_pairwise_semantics():
    x=np.asarray([[1,1,0,0],[1,0,1,0],[0,0,0,1]],dtype=np.uint8)
    initial=v068.partition_split_gain(x,[],np.arange(3))
    assert initial.tolist()==[4.0,4.0,3.0]
    subsequent=v068.partition_split_gain(x,[0],np.arange(3))
    assert subsequent[0]==0.0
    assert subsequent[1]>0
