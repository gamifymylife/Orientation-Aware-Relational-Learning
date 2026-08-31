#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score


def clean_gene(value):
    return str(value).strip().strip('"')


def read_tsv(path):
    return pd.read_csv(path, sep="\t")


def find_files(root):
    out = {}
    for p in Path(root).rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        m = re.search(r"insilico_size(10|100)_(\d)", name)
        if not m:
            continue
        size, net = int(m.group(1)), int(m.group(2))
        d = out.setdefault((size, net), {})
        if "wildtype" in name and name.endswith(".tsv"):
            d["wildtype"] = p
        elif "knockouts" in name and "dual" not in name and name.endswith(".tsv"):
            d["ko"] = p
        elif "knockdowns" in name and name.endswith(".tsv"):
            d["kd"] = p
        elif "goldstandard" in name and name.endswith(".tsv"):
            d["gold"] = p
    return out


def robust_scale(X):
    med = np.nanmedian(X, axis=0)
    mad = np.nanmedian(np.abs(X - med), axis=0) * 1.4826
    sd = np.nanstd(X, axis=0, ddof=1)
    return np.where(mad > 1e-12, mad, np.where(sd > 1e-12, sd, 1.0))


def perturbation_scores(X, wt, row_to_source=None):
    X = np.asarray(X, float)
    wt = np.asarray(wt, float)
    n = X.shape[1]
    if row_to_source is None:
        row_to_source = np.arange(min(X.shape[0], n))
    scale = robust_scale(X)
    scores = np.zeros((n, n), float)
    for row, src in enumerate(row_to_source):
        if row >= X.shape[0] or src >= n:
            break
        scores[src, :] = np.abs((X[row, :] - wt) / scale)
    np.fill_diagonal(scores, 0.0)
    return scores


def parse_gold(path, genes):
    gidx = {clean_gene(g): i for i, g in enumerate(genes)}
    truth = np.zeros((len(genes), len(genes)), int)
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            parts = re.split(r"[\t, ]+", line.strip())
            if len(parts) < 3:
                continue
            a, b = clean_gene(parts[0]), clean_gene(parts[1])
            try:
                value = float(parts[2])
            except ValueError:
                continue
            if a in gidx and b in gidx and value > 0:
                truth[gidx[a], gidx[b]] = 1
    np.fill_diagonal(truth, 0)
    return truth


def metrics(scores, truth):
    mask = ~np.eye(truth.shape[0], dtype=bool)
    y = truth[mask].astype(int)
    s = scores[mask].astype(float)
    prevalence = float(y.mean())
    auprc = float(average_precision_score(y, s))
    auroc = float(roc_auc_score(y, s)) if len(np.unique(y)) > 1 else float("nan")
    edges = int(y.sum())
    order = np.argsort(-s)[:edges]
    top_precision = float(y[order].mean()) if edges else float("nan")
    return {
        "auprc": auprc,
        "auroc": auroc,
        "prevalence": prevalence,
        "auprc_over_prevalence": auprc / prevalence if prevalence else float("nan"),
        "topE_precision": top_precision,
        "edges": edges,
    }


def run_network(paths, size, network, repeats):
    required = ["wildtype", "ko", "kd", "gold"]
    missing = [k for k in required if k not in paths]
    if missing:
        return None, f"missing {missing}"

    wt_df = read_tsv(paths["wildtype"])
    ko_df = read_tsv(paths["ko"])
    kd_df = read_tsv(paths["kd"])
    genes = [g for g in ko_df.columns if clean_gene(g).lower() != "time"]

    ko = ko_df[genes].to_numpy(float)
    kd = kd_df[genes].to_numpy(float)
    wt = wt_df[genes].iloc[0].to_numpy(float)
    truth = parse_gold(paths["gold"], genes)

    ko_id = perturbation_scores(ko, wt)
    kd_id = perturbation_scores(kd, wt)
    rows = []
    for label, score in [("KO_ID", ko_id), ("KD_ID", kd_id)]:
        row = {"size": size, "network": network, "condition": label, "repeat": -1}
        row.update(metrics(score, truth))
        rows.append(row)

    n = len(genes)
    for rep in range(repeats):
        rng = np.random.default_rng(20260831 + 1000 * network + rep + 100000 * size)
        perm = rng.permutation(n)
        for label, matrix in [("KO_ERASED", ko), ("KD_ERASED", kd)]:
            score = perturbation_scores(matrix, wt, row_to_source=perm)
            row = {"size": size, "network": network, "condition": label, "repeat": rep}
            row.update(metrics(score, truth))
            rows.append(row)

    mask = ~np.eye(n, dtype=bool)
    rho = float(spearmanr(ko_id[mask], kd_id[mask]).statistic)
    return rows, rho


def bootstrap_median(values, draws=10000, seed=20260831):
    rng = np.random.default_rng(seed)
    values = np.asarray(values, float)
    boot = np.empty(draws)
    for i in range(draws):
        boot[i] = np.median(rng.choice(values, len(values), replace=True))
    return float(np.median(values)), float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archive")
    group.add_argument("--root")
    parser.add_argument("--out", default="outputs/dream4")
    parser.add_argument("--size", type=int, choices=[10, 100], default=100)
    parser.add_argument("--erasure-repeats", type=int, default=100)
    args = parser.parse_args()

    tmp = None
    if args.archive:
        tmp = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(args.archive) as archive:
            archive.extractall(tmp.name)
        data_root = Path(tmp.name)
    else:
        data_root = Path(args.root)

    files = find_files(data_root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    all_rows = []
    correlations = []
    missing = {}
    for network in range(1, 6):
        rows, rho = run_network(files.get((args.size, network), {}), args.size, network, args.erasure_repeats)
        if rows is None:
            missing[network] = rho
            continue
        all_rows.extend(rows)
        correlations.append({"network": network, "ko_kd_spearman": rho})

    if not all_rows:
        raise SystemExit(f"No complete DREAM4 networks found. Missing: {missing}")

    df = pd.DataFrame(all_rows)
    df.to_csv(out / "dream4_gate_raw.csv", index=False)
    corr_df = pd.DataFrame(correlations)
    corr_df.to_csv(out / "dream4_cross_boundary_consistency.csv", index=False)

    preserved = df[df["condition"].isin(["KO_ID", "KD_ID"])]
    erased = df[df["condition"].isin(["KO_ERASED", "KD_ERASED"])]
    paired = []
    effects = []
    for network in sorted(preserved.network.unique()):
        for modality in ["KO", "KD"]:
            p = preserved[(preserved.network == network) & (preserved.condition == modality + "_ID")].iloc[0]
            e = erased[(erased.network == network) & (erased.condition == modality + "_ERASED")]["auprc"].mean()
            delta = float(p.auprc - e)
            effects.append(delta)
            paired.append({
                "network": network,
                "modality": modality,
                "preserved_auprc": p.auprc,
                "erased_mean_auprc": e,
                "delta_auprc": delta,
                "preserved_ratio": p.auprc_over_prevalence,
            })

    paired_df = pd.DataFrame(paired)
    paired_df.to_csv(out / "dream4_gate_paired.csv", index=False)
    median, lo, hi = bootstrap_median(effects)
    ko_wins = int((paired_df.query("modality == 'KO'").delta_auprc > 0).sum())
    kd_wins = int((paired_df.query("modality == 'KD'").delta_auprc > 0).sum())
    ratios = int((paired_df.preserved_ratio > 1).sum())
    verdict = ko_wins >= 4 and kd_wins >= 4 and median > 0 and lo > 0 and ratios >= 3

    summary = {
        "networks_completed": int(paired_df.network.nunique()),
        "ko_identity_wins": ko_wins,
        "kd_identity_wins": kd_wins,
        "median_paired_auprc_delta": median,
        "bootstrap95": [lo, hi],
        "preserved_comparisons_above_random_ratio": ratios,
        "cross_boundary_spearman_median": float(corr_df.ko_kd_spearman.median()),
        "gate_pass": bool(verdict),
        "missing": missing,
    }
    (out / "dream4_gate_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
