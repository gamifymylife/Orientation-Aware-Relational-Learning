from dataclasses import replace
from pathlib import Path
import json, sys
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from oarl_bench.config import BenchmarkConfig
from oarl_bench.runner import run_grid
from oarl_bench.analysis import paired_cost_advantage, bootstrap_median_ci


def main():
    frozen = json.loads((ROOT/'outputs'/'frozen_parameters.json').read_text())
    base = BenchmarkConfig(
        n_mechanisms=12, n_orientations=8, n_interventions=10,
        budget=35, base_noise=1.0, ig_mode='quadrature', quadrature_points=16,
        lambda_stability=frozen['lambda_stability'], gamma_cost=frozen['gamma_cost']
    )
    frames=[]
    blocks=[
        ('standard_clean','standard',0.0,range(6000,6020)),
        ('informative_unstable','informative_unstable',0.35,range(7000,7020)),
    ]
    for label, regime, perturb, seeds in blocks:
        cfg=replace(base, world_regime=regime, perturbation_scale=perturb)
        df=run_grid(cfg,seeds,[12],[1.0],[perturb],[regime],policies=['generic_oed','full_oarl'])
        df['condition']=label
        frames.append(df)
    out=pd.concat(frames,ignore_index=True)
    out.to_csv(ROOT/'outputs'/'quadrature_confirmatory_results.csv',index=False)
    rows=[]
    for c, sub in out.groupby('condition'):
        adv=paired_cost_advantage(sub,metric='penalized_c95')
        med,lo,hi=bootstrap_median_ci(adv.relative_cost_reduction,draws=3000,seed=31)
        rows.append({'condition':c,'pairs':len(adv),'median_reduction':med,'lo':lo,'hi':hi,
                     'max_abs_reduction':float(adv.relative_cost_reduction.abs().max())})
    summary=pd.DataFrame(rows)
    summary.to_csv(ROOT/'outputs'/'quadrature_confirmatory_summary.csv',index=False)
    print(summary.to_string(index=False))

if __name__=='__main__': main()
