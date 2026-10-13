# OARL v0.6.8 — Decision-preserving test retention (development only)

**Status:** FROZEN DESIGN, NOT YET EXECUTED ON EXTERNAL MATRICES.

### Question

Can a relation-aware test-retention policy protect mutant-detection decisions with fewer retained tests than conventional methods, after charging for evidence and applying the **same abstention rule** to every arm?

We are not trying to certify pairwise test equivalence. The distinction matters: on Lang-9 in v0.6.7, many pairs had different heldout signatures but retaining a representative per class did not reduce the full suite's detectable-mutant set.

### Data

Reuse the **four fully consumed** public v0.6.7 matrices Chart-1, Lang-9, Math-1, Time-4. Their heldout outcomes have already been examined; v0.6.8 is **post hoc development feasibility, not new confirmation**. Verify source identity through v0.6.7 pinned manifest and frozen cohort. No replacements.

Within the old development columns only, deterministic SHA-256 split (`v068-validation:{project.casefold()}:{fault}:{mutant_id}`): first byte <64 = internal validation; remainder = candidate design. The original outer v0.6.7 evaluator is read **only after** proposing/validating test subsets, and it is already consumed evidence.

Every method has the same canonical test universe, design/validation observations, and budgets **20 and 50**. No model calls, learned weights, or tuning on outer evaluator.

### Arms

| Arm | Definition |
|---|---|
| `greedy_cover` | Standard greedy marginal new-mutant coverage |
| `dominance_cover` | Eliminate exact development-subsets, then greedy cover, with fallback filling |
| `greedy_multicover2` | Greedy redundancy, aiming to retain 2 witnesses per mutant |
| `partition_greedy` | Classical mutant-pair observational partition refinement |
| `metadata_diversified` | Greedy coverage with source-type diversity tie preference |
| **`relation_aware`** | Fixed score: 0.6 × normalized uncovered mutant coverage + 0.4 × normalized newly distinguished mutant pairs + 0.01 × novel source type |

All methods fill exactly their budget. If the objective saturates they fill by overall design kill count (deterministic tie breaking). **The candidate is a simple RCC-inspired proxy, not an OARL-specific novel algorithm or certifier**. Prior work includes Rothermel et al. (2002), Jeffrey & Gupta (2007, DOI 10.1109/TSE.2007.18), and Jehan & Wotawa (2023). Selectively retaining redundant tests is established prior art.

### Shared safeguard, costs, and scoring

Test selected subsets against the **full suite's detectable mutant set** in the internal-validation slice. If any detectable mutant is missed, that arm **abstains to the complete test suite**. This is a heuristic guard, not a bound or certificate of future safety.

Primary outcome: number of detectable outer mutants omitted relative to the full suite (not a matched equivalence-pair count). Report retained tests, abstention, evidence cells (all arms access full inner development evidence), candidate-score calculations, expensive pair-gain calculations, dominance comparisons, source types retained. **No actual test-execution time is measured.**

### Predeclared decision

**STOP** if any conventional arm weakly dominates relation-aware on both missed outer mutants and retained tests for all 8 fault × budget settings with a strict improvement in at least one; or if relation-aware fails to obtain any strictly better retained-test/miss tradeoff than controls. Otherwise, at most pursue one independent evaluator trial after including stronger conventional cost-aware and submodular comparators.

No novelty/RSI promotion from a development-only result. The old result and main branch stay unchanged.

### Execution

```bash
python -m pytest -q tests/test_v068_retention_development.py
python scripts/run_v068_retention_development.py \
  --manifest "$HOME/oarl-v067-validation/prepared/manifest.json" \
  --data-root "$HOME/oarl-v067-validation/prepared/data" \
  --out "$HOME/oarl-v067-validation/RETENTION_RESULT.json"
```
