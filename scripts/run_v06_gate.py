"""Run the frozen v0.6 Complementary Orientation Gate."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from oarl_bench.complementarity import run_gate

OUT = Path("evidence/v06")
OUT.mkdir(parents=True, exist_ok=True)
rows = run_gate(range(32))

with (OUT / "v06_results.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

by = defaultdict(list)
for row in rows:
    by[(row["world"], row["policy"])].append(row)

summary = []
for (world, policy), rs in sorted(by.items()):
    summary.append({
        "world": world,
        "policy": policy,
        "accuracy": mean(r["correct"] for r in rs),
        "unknown_rate": mean(r["unknown"] for r in rs),
        "mean_probes": mean(r["probes"] for r in rs),
        "mean_cost": mean(r["cost"] for r in rs),
        "mean_planning_evals": mean(r["planning_evals"] for r in rs),
    })

with (OUT / "v06_summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

resolvable = {
    "single_view", "exact_redundancy", "pure_complementarity",
    "misleading_similarity", "higher_order_complementarity",
}
def take(policy, worlds):
    return [r for r in rows if r["policy"] == policy and r["world"] in worlds]

oarl = take("oarl", resolvable)
exhaustive = take("exhaustive", resolvable)
insuff = take("oarl", {"fundamental_insufficiency"})
xor_oarl = take("oarl", {"pure_complementarity"})
xor_active = take("active_decision", {"pure_complementarity"})
xor_two = take("two_step", {"pure_complementarity"})
red_oarl = take("oarl", {"exact_redundancy"})
red_no_transport = take("oarl_no_transport", {"exact_redundancy"})

headline = {
    "rows": len(rows),
    "oarl_resolvable_accuracy": mean(r["correct"] for r in oarl),
    "oarl_unknown_rate_insufficiency": mean(r["unknown"] for r in insuff),
    "oarl_mean_probes_resolvable": mean(r["probes"] for r in oarl),
    "exhaustive_mean_probes_resolvable": mean(r["probes"] for r in exhaustive),
    "probe_reduction_vs_exhaustive": 1 - mean(r["probes"] for r in oarl) / mean(r["probes"] for r in exhaustive),
    "xor_oarl_mean_probes": mean(r["probes"] for r in xor_oarl),
    "xor_active_decision_mean_probes": mean(r["probes"] for r in xor_active),
    "xor_two_step_mean_probes": mean(r["probes"] for r in xor_two),
    "redundancy_oarl_planning_evals": mean(r["planning_evals"] for r in red_oarl),
    "redundancy_no_transport_planning_evals": mean(r["planning_evals"] for r in red_no_transport),
}
(OUT / "v06_headline.json").write_text(json.dumps(headline, indent=2) + "\n")
print(json.dumps(headline, indent=2))
