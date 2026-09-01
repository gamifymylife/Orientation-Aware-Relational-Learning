import sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from run_dream4_gate import perturbation_scores, metrics

def test_identity_mapping():
    wt=np.array([1.,1.,1.])
    X=np.array([[0.,.2,1.],[1.,0.,.4],[.3,1.,0.]])
    S=perturbation_scores(X,wt)
    assert S.shape==(3,3)
    assert np.allclose(np.diag(S),0)

def test_permutation_changes_sources():
    wt=np.ones(3)
    X=np.array([[0.,.2,1.],[1.,0.,.4],[.3,1.,0.]])
    A=perturbation_scores(X,wt)
    B=perturbation_scores(X,wt,row_to_source=np.array([1,2,0]))
    assert not np.allclose(A,B)

def test_metrics_perfect():
    Y=np.array([[0,1,0],[0,0,1],[0,0,0]])
    S=Y.astype(float)
    m=metrics(S,Y)
    assert abs(m["auprc"]-1)<1e-9
    assert abs(m["auroc"]-1)<1e-9
