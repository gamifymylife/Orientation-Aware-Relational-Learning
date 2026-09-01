#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, math, re, zipfile, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.linear_model import Ridge
from scipy.stats import spearmanr

def clean_gene(s):
    s=str(s).strip().strip('"')
    return s

def read_tsv(path):
    return pd.read_csv(path, sep="\t")

def find_files(root):
    files=list(Path(root).rglob("*"))
    out={}
    for p in files:
        if not p.is_file(): continue
        name=p.name.lower()
        # capture size 10 or 100 network id
        m=re.search(r'insilico_size(10|100)_(\d)', name)
        if not m: continue
        size=int(m.group(1)); net=int(m.group(2))
        key=(size,net)
        d=out.setdefault(key,{})
        if "wildtype" in name and name.endswith(".tsv"): d["wildtype"]=p
        elif "knockouts" in name and "dual" not in name and name.endswith(".tsv"): d["ko"]=p
        elif "knockdowns" in name and name.endswith(".tsv"): d["kd"]=p
        elif "timeseries" in name and name.endswith(".tsv"): d["ts"]=p
        elif "goldstandard" in name and name.endswith(".tsv"): d["gold"]=p
    return out

def robust_scale(X):
    med=np.nanmedian(X,axis=0)
    mad=np.nanmedian(np.abs(X-med),axis=0)*1.4826
    sd=np.nanstd(X,axis=0,ddof=1)
    scale=np.where(mad>1e-12,mad,np.where(sd>1e-12,sd,1.0))
    return scale

def perturbation_scores(X, wt, row_to_source=None):
    X=np.asarray(X,float); wt=np.asarray(wt,float)
    n=X.shape[1]
    if row_to_source is None:
        row_to_source=np.arange(min(X.shape[0],n))
    scale=robust_scale(X)
    S=np.zeros((n,n),float)
    for row,src in enumerate(row_to_source):
        if row>=X.shape[0] or src>=n: break
        S[src,:]=np.abs((X[row,:]-wt)/scale)
    np.fill_diagonal(S,0.0)
    return S

def minmax(M):
    M=np.array(M,float,copy=True)
    mask=~np.eye(M.shape[0],dtype=bool)
    vals=M[mask]
    lo,hi=np.nanmin(vals),np.nanmax(vals)
    if hi<=lo: return np.zeros_like(M)
    return (M-lo)/(hi-lo)

def parse_gold(path, genes):
    gidx={clean_gene(g):i for i,g in enumerate(genes)}
    Y=np.zeros((len(genes),len(genes)),int)
    with open(path,encoding="utf-8-sig") as f:
        for line in f:
            parts=re.split(r'[\t, ]+',line.strip())
            if len(parts)<3: continue
            a,b,val=clean_gene(parts[0]),clean_gene(parts[1]),parts[2]
            try: truth=float(val)
            except: continue
            if a in gidx and b in gidx and truth>0:
                Y[gidx[a],gidx[b]]=1
    np.fill_diagonal(Y,0)
    return Y

def metrics(S,Y):
    mask=~np.eye(Y.shape[0],dtype=bool)
    y=Y[mask].astype(int); s=S[mask].astype(float)
    prevalence=float(y.mean())
    ap=float(average_precision_score(y,s))
    auc=float(roc_auc_score(y,s)) if len(np.unique(y))>1 else float("nan")
    E=int(y.sum())
    idx=np.argsort(-s)[:E]
    top_precision=float(y[idx].mean()) if E else float("nan")
    return dict(auprc=ap, auroc=auc, prevalence=prevalence,
                auprc_over_prevalence=ap/prevalence if prevalence else float("nan"),
                topE_precision=top_precision, edges=E)

def time_series_scores(df, genes):
    # DREAM4 time-series files usually include a Time column and blank separators.
    cols=[c for c in df.columns if clean_gene(c) in set(map(clean_gene,genes))]
    if len(cols)!=len(genes):
        return None
    X=df[cols].to_numpy(float)
    # split whenever time resets if Time exists
    if "Time" in df.columns:
        t=df["Time"].to_numpy(float)
        starts=[0]+[i for i in range(1,len(t)) if t[i]<=t[i-1]]
        blocks=[]
        for k,s in enumerate(starts):
            e=starts[k+1] if k+1<len(starts) else len(t)
            if e-s>=3: blocks.append(X[s:e])
    else:
        blocks=[X]
    A=[]; B=[]
    for b in blocks:
        A.append(b[:-1]); B.append(b[1:])
    X0=np.vstack(A); X1=np.vstack(B)
    n=X0.shape[1]
    S=np.zeros((n,n))
    # target-wise ridge: coefficient source -> target
    model=Ridge(alpha=1.0)
    for j in range(n):
        model.fit(X0,X1[:,j])
        S[:,j]=np.abs(model.coef_)
    np.fill_diagonal(S,0)
    return S

def run_one(paths, size, net, repeats=100):
    req=["wildtype","ko","kd","gold"]
    missing=[k for k in req if k not in paths]
    if missing: return None, f"missing {missing}"
    wt_df=read_tsv(paths["wildtype"])
    ko_df=read_tsv(paths["ko"]); kd_df=read_tsv(paths["kd"])
    genes=list(ko_df.columns)
    # wildtype row; discard non-gene column if any
    genes=[g for g in genes if clean_gene(g).lower()!="time"]
    ko=ko_df[genes].to_numpy(float); kd=kd_df[genes].to_numpy(float)
    wt=wt_df[genes].iloc[0].to_numpy(float)
    Y=parse_gold(paths["gold"],genes)
    rows=[]
    Sko=perturbation_scores(ko,wt)
    Skd=perturbation_scores(kd,wt)
    for label,S in [("KO_ID",Sko),("KD_ID",Skd),
                    ("KO_KD_CONSENSUS",(minmax(Sko)+minmax(Skd))/2)]:
        r={"size":size,"network":net,"condition":label,"repeat":-1}
        r.update(metrics(S,Y)); rows.append(r)
    if "ts" in paths:
        try:
            Sts=time_series_scores(read_tsv(paths["ts"]),genes)
            if Sts is not None:
                r={"size":size,"network":net,"condition":"TIME_SERIES","repeat":-1}
                r.update(metrics(Sts,Y)); rows.append(r)
        except Exception:
            pass
    n=len(genes)
    for rep in range(repeats):
        rng=np.random.default_rng(20260831+1000*net+rep)
        perm=rng.permutation(n)
        for label,X in [("KO_ERASED",ko),("KD_ERASED",kd)]:
            S=perturbation_scores(X,wt,row_to_source=perm)
            r={"size":size,"network":net,"condition":label,"repeat":rep}
            r.update(metrics(S,Y)); rows.append(r)
    # cross-boundary consistency
    mask=~np.eye(n,dtype=bool)
    rho=float(spearmanr(Sko[mask],Skd[mask]).statistic)
    return rows, rho

def bootstrap_effects(pairdf, B=10000, seed=20260831):
    """Hierarchical paired bootstrap: resample networks, then modalities within network."""
    rng=np.random.default_rng(seed)
    networks=np.array(sorted(pairdf.network.unique()), dtype=int)
    observed=float(np.median(pairdf.delta_auprc.to_numpy(float)))
    boots=[]
    for _ in range(B):
        sampled_networks=rng.choice(networks, len(networks), replace=True)
        vals=[]
        for net in sampled_networks:
            local=pairdf.loc[pairdf.network==net, "delta_auprc"].to_numpy(float)
            vals.extend(rng.choice(local, len(local), replace=True).tolist())
        boots.append(float(np.median(vals)))
    return observed, float(np.quantile(boots,.025)), float(np.quantile(boots,.975))

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--archive")
    g.add_argument("--root")
    ap.add_argument("--out",default="outputs")
    ap.add_argument("--size",type=int,choices=[10,100],default=100)
    ap.add_argument("--erasure-repeats",type=int,default=100)
    args=ap.parse_args()
    tmp=None
    if args.archive:
        tmp=tempfile.TemporaryDirectory()
        with zipfile.ZipFile(args.archive) as z: z.extractall(tmp.name)
        data_root=Path(tmp.name)
    else: data_root=Path(args.root)
    files=find_files(data_root)
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    allrows=[]; rhos=[]; missing={}
    for net in range(1,6):
        paths=files.get((args.size,net),{})
        rows,rho=run_one(paths,args.size,net,args.erasure_repeats)
        if rows is None:
            missing[net]=rho; continue
        allrows.extend(rows); rhos.append({"network":net,"ko_kd_spearman":rho})
    if not allrows:
        raise SystemExit(f"No complete DREAM4 networks found. Missing: {missing}")
    df=pd.DataFrame(allrows)
    df.to_csv(out/"dream4_gate_raw.csv",index=False)
    pd.DataFrame(rhos).to_csv(out/"dream4_cross_boundary_consistency.csv",index=False)

    preserved=df[df["condition"].isin(["KO_ID","KD_ID"])]
    erased=df[df["condition"].isin(["KO_ERASED","KD_ERASED"])]
    effects=[]
    paired=[]
    for net in sorted(preserved.network.unique()):
        for mod in ["KO","KD"]:
            p=preserved[(preserved.network==net)&(preserved.condition==mod+"_ID")].iloc[0]
            e=erased[(erased.network==net)&(erased.condition==mod+"_ERASED")]["auprc"].mean()
            effects.append(float(p.auprc-e))
            paired.append({"network":net,"modality":mod,"preserved_auprc":p.auprc,
                           "erased_mean_auprc":e,"delta_auprc":p.auprc-e,
                           "preserved_ratio":p.auprc_over_prevalence})
    pairdf=pd.DataFrame(paired); pairdf.to_csv(out/"dream4_gate_paired.csv",index=False)
    med,lo,hi=bootstrap_effects(pairdf)
    ko_wins=sum(pairdf.query("modality=='KO'").delta_auprc>0)
    kd_wins=sum(pairdf.query("modality=='KD'").delta_auprc>0)
    ko_ratio_networks=int((pairdf.query("modality=='KO'").preserved_ratio>1).sum())
    kd_ratio_networks=int((pairdf.query("modality=='KD'").preserved_ratio>1).sum())
    ratio_gate=(ko_ratio_networks>=3 or kd_ratio_networks>=3)
    verdict=(ko_wins>=4 and kd_wins>=4 and med>0 and lo>0 and ratio_gate)
    summary={
        "networks_completed":int(pairdf.network.nunique()),
        "ko_identity_wins":int(ko_wins),
        "kd_identity_wins":int(kd_wins),
        "median_paired_auprc_delta":med,
        "bootstrap95":[lo,hi],
        "ko_networks_above_random_ratio":ko_ratio_networks,
        "kd_networks_above_random_ratio":kd_ratio_networks,
        "normalized_auprc_gate_pass":bool(ratio_gate),
        "cross_boundary_spearman_median":float(pd.DataFrame(rhos).ko_kd_spearman.median()),
        "gate_pass":bool(verdict),
        "missing":missing,
    }
    (out/"dream4_gate_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
