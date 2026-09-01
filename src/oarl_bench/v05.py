"""v0.5A end-to-end benchmark helpers."""

from __future__ import annotations

import time
from dataclasses import replace

import pandas as pd

from .certification import (
    apply_discovered_structure,
    discover_exact_structure,
    pairwise_structure_metrics,
)
from .config import BenchmarkConfig
from .runner import run_episode_on_world
from .world import generate_world


def run_v05_triplet(
    cfg: BenchmarkConfig,
    seed: int,
    *,
    equivalence_tol: float = 1e-8,
    distinct_tol: float = 5e-3,
) -> list[dict]:
    """Compare Generic OED, oracle quotient, and discovered quotient on one world."""
    world = generate_world(cfg, seed)

    generic = run_episode_on_world(cfg, seed, "generic_cost_tiebreak", world)
    generic["v05_policy"] = "generic_oed"
    generic["certificate_runtime_s"] = 0.0
    generic["certificate_comparisons"] = 0
    generic["end_to_end_runtime_s"] = generic["runtime_s"]

    oracle = run_episode_on_world(cfg, seed, "structured_oarl", world)
    oracle["v05_policy"] = "oracle_quotient"
    oracle["certificate_runtime_s"] = 0.0
    oracle["certificate_comparisons"] = 0
    oracle["end_to_end_runtime_s"] = oracle["runtime_s"]

    t0 = time.perf_counter()
    discovery = discover_exact_structure(
        world,
        equivalence_tol=equivalence_tol,
        distinct_tol=distinct_tol,
        admissible=world.admissible,
    )
    certificate_wall = time.perf_counter() - t0
    discovered_world = apply_discovered_structure(world, discovery)
    discovered = run_episode_on_world(cfg, seed, "structured_oarl", discovered_world)
    discovered["v05_policy"] = "discovered_quotient"
    discovered["certificate_runtime_s"] = float(certificate_wall)
    discovered["certificate_comparisons"] = int(discovery.comparisons)
    discovered["end_to_end_runtime_s"] = float(certificate_wall + discovered["runtime_s"])
    discovered["discovered_classes"] = int(discovery.n_classes)
    discovered.update(pairwise_structure_metrics(world, discovery))

    oracle["discovered_classes"] = int(world.n_true_equivalence_classes)
    oracle.update({
        "pair_precision": 1.0,
        "pair_recall": 1.0,
        "pair_fp": 0.0,
        "pair_fn": 0.0,
    })
    generic["discovered_classes"] = int(world.n_orientations)
    generic.update({
        "pair_precision": 1.0,
        "pair_recall": 0.0 if world.n_true_equivalence_classes < world.n_orientations else 1.0,
        "pair_fp": 0.0,
        "pair_fn": float("nan"),
    })

    return [generic, oracle, discovered]


def run_v05_grid(
    base_cfg: BenchmarkConfig,
    seeds,
    orientation_counts=(8, 16, 24),
    class_counts=(4,),
    ig_modes=("proxy", "quadrature"),
) -> pd.DataFrame:
    rows = []
    for ig_mode in ig_modes:
        for classes in class_counts:
            for orientations in orientation_counts:
                if classes > orientations:
                    continue
                cfg = replace(
                    base_cfg,
                    world_regime="equivalent_redundancy",
                    n_orientations=int(orientations),
                    n_equivalence_classes=int(classes),
                    ig_mode=str(ig_mode),
                )
                for seed in seeds:
                    rows.extend(run_v05_triplet(cfg, int(seed)))
    return pd.DataFrame(rows)
