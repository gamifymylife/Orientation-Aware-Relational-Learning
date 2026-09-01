import numpy as np
import pandas as pd

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["policy", "regime", "n_mechanisms", "base_noise", "perturbation_scale"]
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            runs=("seed", "count"),
            success_rate=("success_95", "mean"),
            correct_rate=("correct_argmax", "mean"),
            median_n95=("n95", "median"),
            mean_n95=("n95", "mean"),
            median_c95=("c95", "median"),
            median_penalized_c95=("penalized_c95", "median"),
            mean_penalized_c95=("penalized_c95", "mean"),
            median_posterior_true=("posterior_true", "median"),
            mean_score_evals=("score_evals", "mean"),
            mean_runtime_s=("runtime_s", "mean"),
            mean_orientation_switches=("orientation_switches", "mean"),
        )
        .reset_index()
    )

def paired_cost_advantage(
    df: pd.DataFrame,
    candidate: str = "full_oarl",
    baseline: str = "generic_oed",
    metric: str = "penalized_c95",
) -> pd.DataFrame:
    keys = ["seed", "regime", "n_mechanisms", "base_noise", "perturbation_scale"]
    p = df.pivot_table(index=keys, columns="policy", values=metric)
    p = p.dropna(subset=[candidate, baseline]).copy()
    p["relative_cost_reduction"] = (p[baseline] - p[candidate]) / p[baseline]
    return p.reset_index()

def bootstrap_median_ci(values, seed: int = 0, draws: int = 5000, alpha: float = 0.05):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    medians = np.empty(draws, dtype=float)
    for i in range(draws):
        sample = rng.choice(values, size=len(values), replace=True)
        medians[i] = np.median(sample)
    lo = np.quantile(medians, alpha / 2)
    hi = np.quantile(medians, 1 - alpha / 2)
    return float(np.median(values)), float(lo), float(hi)
