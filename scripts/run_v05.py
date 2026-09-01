from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
import json

import pandas as pd

from oarl_bench.config import BenchmarkConfig
from oarl_bench.v05 import run_v05_triplet


def _task(args):
    base_cfg, seed, orientations, classes, ig_mode = args
    cfg = replace(
        base_cfg,
        world_regime="equivalent_redundancy",
        n_orientations=int(orientations),
        n_equivalence_classes=int(classes),
        ig_mode=str(ig_mode),
    )
    return run_v05_triplet(cfg, int(seed))


def main():
    out = Path("evidence/v05/outputs")
    out.mkdir(parents=True, exist_ok=True)

    cfg = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=10,
        n_interventions=8,
        n_equivalence_classes=4,
        budget=12,
        quadrature_points=12,
    )
    tasks = [
        (cfg, seed, orientations, 4, ig_mode)
        for ig_mode in ("proxy", "quadrature")
        for orientations in (8, 16, 24)
        for seed in range(20)
    ]
    rows = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for triplet in ex.map(_task, tasks):
            rows.extend(triplet)
    df = pd.DataFrame(rows)
    df.to_csv(out / "v05a_results.csv", index=False)

    summary = (
        df.groupby(["ig_mode", "n_orientations", "v05_policy"], dropna=False)
        .agg(
            runs=("seed", "count"),
            correct_rate=("correct_argmax", "mean"),
            success_rate=("success_95", "mean"),
            median_score_evals=("score_evals", "median"),
            median_runtime_s=("runtime_s", "median"),
            median_certificate_runtime_s=("certificate_runtime_s", "median"),
            median_end_to_end_runtime_s=("end_to_end_runtime_s", "median"),
            pair_precision=("pair_precision", "min"),
            pair_recall=("pair_recall", "min"),
        )
        .reset_index()
    )
    summary.to_csv(out / "v05a_summary.csv", index=False)

    discovered = df[df.v05_policy == "discovered_quotient"]
    oracle = df[df.v05_policy == "oracle_quotient"]
    generic = df[df.v05_policy == "generic_oed"]

    key = ["seed", "ig_mode", "n_orientations"]
    paired = discovered.merge(
        oracle[key + ["correct_argmax", "success_95", "score_evals"]],
        on=key, suffixes=("_discovered", "_oracle")
    ).merge(
        generic[key + ["score_evals", "end_to_end_runtime_s"]],
        on=key, suffixes=("", "_generic")
    )
    paired["outcome_match"] = (
        (paired.correct_argmax_discovered == paired.correct_argmax_oracle)
        & (paired.success_95_discovered == paired.success_95_oracle)
    )
    paired["score_eval_reduction"] = 1.0 - paired.score_evals_discovered / paired.score_evals
    paired["runtime_reduction_vs_generic"] = (
        1.0 - paired.end_to_end_runtime_s / paired.end_to_end_runtime_s_generic
    )
    paired.to_csv(out / "v05a_paired.csv", index=False)

    headline = {
        "runs_discovered": int(len(discovered)),
        "false_merge_pairs": int(discovered["pair_fp"].fillna(0).sum()),
        "min_pair_precision": float(discovered["pair_precision"].min()),
        "min_pair_recall": float(discovered["pair_recall"].min()),
        "paired_outcome_match_rate": float(paired["outcome_match"].mean()),
        "median_score_eval_reduction": float(paired["score_eval_reduction"].median()),
        "median_runtime_reduction_vs_generic": float(paired["runtime_reduction_vs_generic"].median()),
    }
    (out / "v05a_headline.json").write_text(json.dumps(headline, indent=2) + "\n")
    print(json.dumps(headline, indent=2))


if __name__ == "__main__":
    main()
