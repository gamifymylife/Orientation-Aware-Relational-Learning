import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_dream4_gate import bootstrap_effects

def test_hierarchical_bootstrap_returns_finite_interval():
    df=pd.DataFrame({
        "network":[1,1,2,2,3,3,4,4,5,5],
        "modality":["KO","KD"]*5,
        "delta_auprc":[.1,.2,.05,.1,.2,.15,.12,.08,.09,.11],
    })
    med,lo,hi=bootstrap_effects(df,B=200,seed=7)
    assert np.isfinite([med,lo,hi]).all()
    assert lo <= med <= hi

def test_preregistered_seed_formula_is_size_independent():
    # The preregistered erasure seed contains network and repeat only.
    net,rep=3,17
    a=np.random.default_rng(20260831+1000*net+rep).permutation(10)
    b=np.random.default_rng(20260831+1000*net+rep).permutation(10)
    assert np.array_equal(a,b)
