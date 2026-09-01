from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from oarl_bench.mutation_equivalence import evaluate_matrix, load_mutation_matrix


MIN_ELIGIBLE_TESTS = 200
MIN_ORACLE_COMPRESSION = 0.20
MIN_PASSING_MATRICES = 3
GREEDY_BUDGET = 20


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("external/mutation/v066/data"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("evidence/v066/summary_compact.json"),
    )
    args = parser.parse_args()

    started = time.perf_counter()
    results = [
        evaluate_matrix(load_mutation_matrix(path), budget=GREEDY_BUDGET)
        for path in sorted(args.data.glob("*.npz"))
    ]
    if len(results) != 4:
        raise ValueError(f"expected four frozen matrices, found {len(results)}")

    per_matrix_pass = [
        row["eligible_tests"] >= MIN_ELIGIBLE_TESTS
        and row["oracle_compression"] >= MIN_ORACLE_COMPRESSION
        and row["oracle_coverage_matches_raw"]
        and row["oracle_selected_count_matches_raw"]
        for row in results
    ]
    median_compression = statistics.median(row["oracle_compression"] for row in results)
    gates = {
        "four_external_matrices": len(results) == 4,
        "all_have_at_least_200_eligible_tests": all(
            row["eligible_tests"] >= MIN_ELIGIBLE_TESTS for row in results
        ),
        "at_least_three_have_20pct_oracle_compression": sum(per_matrix_pass)
        >= MIN_PASSING_MATRICES,
        "median_oracle_compression_ge_20pct": median_compression
        >= MIN_ORACLE_COMPRESSION,
        "all_oracle_quotients_preserve_greedy_task": all(
            row["oracle_coverage_matches_raw"]
            and row["oracle_selected_count_matches_raw"]
            for row in results
        ),
    }
    summary = {
        "version": "0.6.6",
        "benchmark": "Diversity-aware Mutation Testing / Defects4J kill matrices",
        "greedy_test_budget": GREEDY_BUDGET,
        "thresholds": {
            "minimum_eligible_tests": MIN_ELIGIBLE_TESTS,
            "minimum_oracle_compression": MIN_ORACLE_COMPRESSION,
            "minimum_passing_matrices": MIN_PASSING_MATRICES,
        },
        "matrices": results,
        "aggregate": {
            "median_oracle_compression": median_compression,
            "passing_matrices": int(sum(per_matrix_pass)),
            "matrix_count": len(results),
        },
        "gates": gates,
        "suitability_passed": all(gates.values()),
        "analysis_wall_clock_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
