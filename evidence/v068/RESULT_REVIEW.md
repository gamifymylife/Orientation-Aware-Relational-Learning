# OARL v0.6.8 — Frozen development outcome review

**Disposition: STOP — NO COMPARATIVE RETENTION ADVANTAGE; ALL 48 PROPOSALS ABSTAINED.**

Received from project owner: `RETENTION_RESULT.json`, SHA-256
`de82e24d1d546eaada469849e190befca5b07a1187bee59d1826e0aedc61a595`, 38,057 bytes.
Analysis checked the uploaded JSON's counts and aggregates; this is **not independent reproduction** of the owner's source checkout or runner. The four public faults have already been inspected in v0.6.7 and are development-only, not independent holdouts.

## Summary

- Protocol: `v068-development-comparison-v01`; source revision `f8d8376e0efe345161f26ff6483a404c8548fe1c`.
- Four previously consumed public cases: Chart-1 (395 tests), Lang-9 (1,449), Math-1 (768), Time-4 (290).
- Six arms: greedy coverage, dominance + greedy coverage, two-witness greedy multicoverage, greedy partition refinement, metadata-diversified greedy, and a fixed-weight relation-aware proxy.
- Each arm proposed 20 or 50 tests in each fault: **4 faults × 2 budgets × 6 arms = 48 proposals**.
- **Every proposal failed inner-validation preservation**, hence all 48 abstained and kept the full suite. All 48 final outputs therefore have zero outer missed detectable mutants **by construction**, not successful selective retention.
- Realized retained-test reduction: **0% for every arm**. Real execution-time savings: **not measured**. The proxy demonstrates **no additional utility**.

## Method-by-method diagnostics

| Arm | Cases abstained (of 8) | Sum of validation mutants missed by proposed (not retained) subsets | Planning-scored candidates | Expensive pair-gain candidates | Dominance comparisons |
|---|---:|---:|---:|---:|---:|
| Greedy cover | 8 | 43 | 197,480 | 0 | 0 |
| Dominance + greedy | 8 | 39 | 43,766 | 0 | 79,046 |
| Greedy multicover 2 | 8 | 42 | 197,480 | 0 | 0 |
| Greedy partition refinement | 8 | 43 | 197,480 | 197,480 | 0 |
| Metadata-diversified | 8 | 44 | 197,480 | 0 | 0 |
| **Relation-aware** | **8** | **40** | **197,480** | **197,480** | **0** |

The missed-mutant sums are *diagnostic counts over distinct scenarios*, not unique defects, and do not establish a per-proposal ranking where all scenarios abstained. Computation counters are different operations and **not calibrated elapsed CPU time**.

## Important experimental-design limitation

The strict gate required zero lost mutants relative to the **entire eligible suite** in a separate development validation slice, despite asking each selector to retain only 20 or 50 tests. The setup did not first establish that complete validation coverage was achievable within either budget. Accordingly, 48/48 fallback shows the proposed **budget-and-gate combination was nonproductive**, not that no smaller safe subset exists. A trivial fallback guarantees zero realized missing mutants at the cost of all savings.

The complete inner evidence matrix, reported as 956,843 test × mutant cells in aggregate across the four cases, was available to each selector/guard. No physical test execution savings or acquisition-cost advantage follows from these results. The validation guard is not a prospective certificate for unseen faults.

## Gate judgment and next action

The preregistered `v068/PROTOCOL.md` says stop if the relation-aware method fails to find a strictly better retained-test/miss tradeoff than conventional methods. **It did fail**: every arm retained 100% and missed 0 after fallback.

**Close this experimental line at v0.6.8 and do not tune the score or budgets on exposed cases and call the revision prospective.** Retain the broader decision-preserving reduction question as unproven and available for a *separately justified* future experiment, but no immediate escalation to neural RSI, additional RCC framework, or a supposedly confirmatory report is supported.

The frozen protocol, prior negative v0.6.7 result, and repository `main` remain unchanged.
