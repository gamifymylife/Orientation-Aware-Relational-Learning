from dataclasses import replace
from pathlib import Path
import json

import pandas as pd

from oarl_bench.certification import discover_exact_structure, pairwise_structure_metrics
from oarl_bench.config import BenchmarkConfig
from oarl_bench.v05 import run_v05_triplet
from oarl_bench.world import generate_world


def main():
    out = Path("evidence/v05/outputs")
    out.mkdir(parents=True, exist_ok=True)

    # Unique-orientation safety control: a conservative certifier should not
    # invent quotient structure when every orientation is genuinely distinct.
    rows = []
    base = BenchmarkConfig(
        world_regime="standard",
        n_mechanisms=10,
        n_interventions=8,
        budget=12,
    )
    for orientations in (8, 16, 24):
        cfg = replace(base, n_orientations=orientations)
        for seed in range(100):
            world = generate_world(cfg, seed)
            discovery = discover_exact_structure(world)
            metrics = pairwise_structure_metrics(world, discovery)
            rows.append({
                "seed": seed,
                "n_orientations": orientations,
                "discovered_classes": discovery.n_classes,
                **metrics,
            })
    negative = pd.DataFrame(rows)
    negative.to_csv(out / "v05a_negative_control.csv", index=False)
    negative_summary = {
        "worlds": int(len(negative)),
        "false_merge_pairs": int(negative.pair_fp.sum()),
        "all_unique_classes_retained": bool(
            (negative.discovered_classes == negative.n_orientations).all()
        ),
        "orientation_counts": sorted(map(int, negative.n_orientations.unique())),
    }
    (out / "v05a_negative_control_summary.json").write_text(
        json.dumps(negative_summary, indent=2) + "\n"
    )

    # Serial quadrature timing sanity check. Run with BLAS thread counts pinned
    # to one externally when strict timing reproducibility is desired.
    rows = []
    base_q = BenchmarkConfig(
        world_regime="equivalent_redundancy",
        n_mechanisms=10,
        n_interventions=8,
        n_equivalence_classes=4,
        budget=12,
        quadrature_points=12,
        ig_mode="quadrature",
    )
    for orientations in (8, 16, 24):
        cfg = replace(base_q, n_orientations=orientations)
        for seed in range(5):
            rows.extend(run_v05_triplet(cfg, seed))
    serial = pd.DataFrame(rows)
    serial.to_csv(out / "v05a_serial_runtime.csv", index=False)
    wide = serial.pivot_table(
        index=["seed", "n_orientations"],
        columns="v05_policy",
        values="end_to_end_runtime_s",
    )
    runtime_summary = {}
    for orientations in (8, 16, 24):
        block = wide.xs(orientations, level="n_orientations")
        reduction = 1.0 - block.discovered_quotient / block.generic_oed
        runtime_summary[str(orientations)] = {
            "paired_seeds": int(len(reduction)),
            "median_runtime_reduction": float(reduction.median()),
            "min_runtime_reduction": float(reduction.min()),
            "max_runtime_reduction": float(reduction.max()),
        }
    (out / "v05a_serial_runtime_summary.json").write_text(
        json.dumps(runtime_summary, indent=2) + "\n"
    )

    print(json.dumps({
        "negative_control": negative_summary,
        "serial_runtime": runtime_summary,
    }, indent=2))


if __name__ == "__main__":
    main()
