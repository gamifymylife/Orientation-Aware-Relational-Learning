from __future__ import annotations

import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

from oarl_bench.certification import CertificateStatus
from oarl_bench.config import BenchmarkConfig
from oarl_bench.noisy_certification import (
    apply_noisy_discovered_structure,
    certify_pair_noisy,
    discover_noisy_structure,
    draw_predictive_summary,
    noisy_structure_metrics,
)
from oarl_bench.runner import run_episode_on_world
from oarl_bench.world import generate_world


N_SAMPLES = 2000
DISTINCT_SEEDS = range(1000, 1300)
EQUIVALENT_SEEDS = range(2000, 2100)
DISTINCT_CONFIGS = [
    (8, 8, 6),
    (12, 8, 7),
    (16, 12, 8),
    (12, 16, 8),
]
EQUIVALENT_CONFIGS = [
    (8, 8, 6, 4),
    (12, 8, 7, 4),
    (16, 12, 8, 4),
    (12, 16, 8, 4),
]


def _certificate_seed(seed: int, h: int, o: int, a: int) -> int:
    return int(seed * 1000003 + h * 100 + o * 10 + a + 505021)


def _true_direct_transport(world, target: int, reference: int):
    A = world.n_interventions
    target_to_canonical = world.true_to_canonical_intervention[target]
    reference_to_canonical = world.true_to_canonical_intervention[reference]
    canonical_to_reference = np.empty(A, dtype=int)
    canonical_to_reference[reference_to_canonical] = np.arange(A, dtype=int)
    mapping = canonical_to_reference[target_to_canonical]
    scale = float(
        world.true_transform_scale[target]
        / world.true_transform_scale[reference]
    )
    offset = float(
        world.true_transform_offset[target]
        - scale * world.true_transform_offset[reference]
    )
    return mapping, scale, offset


def run_distinct_gate():
    config_rows = []
    false_rows = []
    total_pairs = 0

    for h, orientations, interventions in DISTINCT_CONFIGS:
        config_pairs = 0
        config_equivalent = 0
        config_unknown = 0
        config_distinct = 0
        for seed in DISTINCT_SEEDS:
            cfg = BenchmarkConfig(
                world_regime="standard",
                n_mechanisms=h,
                n_orientations=orientations,
                n_interventions=interventions,
            )
            world = generate_world(cfg, seed)
            rng = np.random.default_rng(_certificate_seed(seed, h, orientations, interventions))
            fit = draw_predictive_summary(world, N_SAMPLES, rng)
            validation = draw_predictive_summary(world, N_SAMPLES, rng)

            for target in range(orientations):
                for reference in range(target):
                    cert = certify_pair_noisy(fit, validation, target, reference)
                    config_pairs += 1
                    if cert.status is CertificateStatus.EQUIVALENT:
                        config_equivalent += 1
                        false_rows.append({
                            "H": h,
                            "O": orientations,
                            "A": interventions,
                            "seed": seed,
                            "target": target,
                            "reference": reference,
                            "assignment_min_gap": cert.assignment_min_gap,
                            "assignment_max_distance": cert.assignment_max_distance,
                            "validation_upper_z": cert.validation_upper_z,
                            "scale": cert.scale,
                            "offset": cert.offset,
                        })
                    elif cert.status is CertificateStatus.DISTINCT:
                        config_distinct += 1
                    else:
                        config_unknown += 1

        total_pairs += config_pairs
        config_rows.append({
            "H": h,
            "O": orientations,
            "A": interventions,
            "seeds": len(DISTINCT_SEEDS),
            "pair_challenges": config_pairs,
            "equivalent_certificates": config_equivalent,
            "distinct_certificates": config_distinct,
            "unknown_certificates": config_unknown,
        })

    return pd.DataFrame(config_rows), pd.DataFrame(false_rows), total_pairs


def run_equivalence_gate():
    rows = []
    downstream_rows = []

    for h, orientations, interventions, classes in EQUIVALENT_CONFIGS:
        for seed in EQUIVALENT_SEEDS:
            cfg = BenchmarkConfig(
                world_regime="equivalent_redundancy",
                n_mechanisms=h,
                n_orientations=orientations,
                n_equivalence_classes=classes,
                n_interventions=interventions,
                budget=20,
            )
            world = generate_world(cfg, seed)
            discovery = discover_noisy_structure(
                world,
                n_samples=N_SAMPLES,
                certificate_seed=_certificate_seed(seed, h, orientations, interventions),
            )
            metrics = noisy_structure_metrics(world, discovery)

            accepted = 0
            mapping_errors = 0
            scale_errors = []
            offset_errors_z = []
            for cert in discovery.certificates:
                if cert.status is not CertificateStatus.EQUIVALENT:
                    continue
                accepted += 1
                true_map, true_scale, true_offset = _true_direct_transport(
                    world, cert.target, cert.reference
                )
                mapping_errors += int(not np.array_equal(cert.intervention_map, true_map))
                scale_errors.append(abs(cert.scale / true_scale - 1.0))
                noise = float(np.median(world.nominal_sigma[cert.target]))
                offset_errors_z.append(
                    abs(cert.offset - true_offset) / max(noise, 1e-12)
                )

            rows.append({
                "H": h,
                "O": orientations,
                "A": interventions,
                "C": classes,
                "seed": seed,
                "discovered_classes": discovery.n_classes,
                "compression_fraction": metrics["compression_fraction"],
                "pair_tp": metrics["pair_tp"],
                "pair_fp": metrics["pair_fp"],
                "pair_fn": metrics["pair_fn"],
                "pair_tn": metrics["pair_tn"],
                "pair_precision": metrics["pair_precision"],
                "pair_recall": metrics["pair_recall"],
                "accepted_certificates": accepted,
                "mapping_errors": mapping_errors,
                "max_scale_relative_error": max(scale_errors) if scale_errors else 0.0,
                "max_offset_error_z": max(offset_errors_z) if offset_errors_z else 0.0,
                "certificate_comparisons": discovery.comparisons,
                "certificate_runtime_s": discovery.runtime_s,
            })

            if seed < 2025:
                oracle = run_episode_on_world(cfg, seed, "structured_oarl", world)
                discovered_world = apply_noisy_discovered_structure(world, discovery)
                discovered = run_episode_on_world(
                    cfg, seed, "structured_oarl", discovered_world
                )
                downstream_rows.append({
                    "H": h,
                    "O": orientations,
                    "A": interventions,
                    "C": classes,
                    "seed": seed,
                    "oracle_correct": oracle["correct_argmax"],
                    "discovered_correct": discovered["correct_argmax"],
                    "oracle_success_95": oracle["success_95"],
                    "discovered_success_95": discovered["success_95"],
                    "oracle_false_high_confidence": oracle["false_high_confidence"],
                    "discovered_false_high_confidence": discovered["false_high_confidence"],
                    "oracle_score_evals": oracle["score_evals"],
                    "discovered_score_evals": discovered["score_evals"],
                    "oracle_transported_updates": oracle["transported_updates"],
                    "discovered_transported_updates": discovered["transported_updates"],
                })

    return pd.DataFrame(rows), pd.DataFrame(downstream_rows)


def summarize(negative, false_equivalences, negative_total_pairs, positive, downstream):
    tp = float(positive["pair_tp"].sum())
    fp = float(positive["pair_fp"].sum())
    fn = float(positive["pair_fn"].sum())
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0

    accepted = int(positive["accepted_certificates"].sum())
    mapping_errors = int(positive["mapping_errors"].sum())
    max_scale_error = float(positive["max_scale_relative_error"].max())
    max_offset_error_z = float(positive["max_offset_error_z"].max())
    mean_compression = float(positive["compression_fraction"].mean())

    checks = {
        "zero_false_equivalence_certificates_on_unique_pairs": int(len(false_equivalences)) == 0,
        "zero_pairwise_false_merges_in_equivalence_worlds": fp == 0.0,
        "pairwise_precision_is_one": precision == 1.0,
        "zero_accepted_mapping_errors": mapping_errors == 0,
        "max_scale_relative_error_le_0_06": max_scale_error <= 0.06,
        "max_offset_error_z_le_0_05": max_offset_error_z <= 0.05,
        "aggregate_pair_recall_ge_0_20": recall >= 0.20,
        "mean_compression_ge_0_10": mean_compression >= 0.10,
    }

    score_reduction = 1.0 - (
        downstream["discovered_score_evals"].sum()
        / downstream["oracle_score_evals"].sum()
    ) if len(downstream) and downstream["oracle_score_evals"].sum() else 0.0

    return {
        "version": "v0.5B.1",
        "n_samples_per_split": N_SAMPLES,
        "distinct_seed_range": [1000, 1299],
        "equivalent_seed_range": [2000, 2099],
        "unique_pair_challenges": int(negative_total_pairs),
        "false_equivalence_certificates": int(len(false_equivalences)),
        "equivalence_worlds": int(len(positive)),
        "accepted_equivalence_certificates": accepted,
        "pair_tp": tp,
        "pair_fp": fp,
        "pair_fn": fn,
        "pair_precision": float(precision),
        "pair_recall": float(recall),
        "mean_compression_fraction": mean_compression,
        "accepted_mapping_errors": mapping_errors,
        "max_scale_relative_error": max_scale_error,
        "max_offset_error_z": max_offset_error_z,
        "downstream_worlds": int(len(downstream)),
        "oracle_correct_rate": float(downstream["oracle_correct"].mean()) if len(downstream) else None,
        "discovered_correct_rate": float(downstream["discovered_correct"].mean()) if len(downstream) else None,
        "oracle_false_high_confidence_rate": float(downstream["oracle_false_high_confidence"].mean()) if len(downstream) else None,
        "discovered_false_high_confidence_rate": float(downstream["discovered_false_high_confidence"].mean()) if len(downstream) else None,
        "discovered_vs_oracle_score_eval_reduction": float(score_reduction),
        "checks": checks,
        "gate_pass": bool(all(checks.values())),
    }


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / "evidence" / "v05b" / "outputs"
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    negative, false_equivalences, negative_total_pairs = run_distinct_gate()
    positive, downstream = run_equivalence_gate()
    summary = summarize(
        negative, false_equivalences, negative_total_pairs, positive, downstream
    )
    summary["wall_runtime_s"] = float(time.perf_counter() - t0)

    negative.to_csv(out / "v05b_unique_controls.csv", index=False)
    positive.to_csv(out / "v05b_equivalence_controls.csv", index=False)
    downstream.to_csv(out / "v05b_downstream_controls.csv", index=False)
    if len(false_equivalences):
        false_equivalences.to_csv(out / "v05b_false_equivalences.csv", index=False)
    else:
        pd.DataFrame(columns=[
            "H", "O", "A", "seed", "target", "reference",
            "assignment_min_gap", "assignment_max_distance",
            "validation_upper_z", "scale", "offset",
        ]).to_csv(out / "v05b_false_equivalences.csv", index=False)

    (out / "v05b_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
