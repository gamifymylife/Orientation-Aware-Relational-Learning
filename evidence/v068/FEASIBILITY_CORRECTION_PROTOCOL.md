# OARL v0.6.8 — Feasibility-first corrective experiment

**Status: FIXED DESIGN; NO REAL-DATA CORRECTED RESULT YET.**

## Why the original comparison was uninformative

The original v0.6.8 imposed **20/50-test budgets without first demonstrating that those budgets could detect every mutant detectable by the full development suite**. Every strategy then triggered the all-tests fallback (48/48). That showed the budget-and-fallback design was unsuitable for measuring retention utility, not that no smaller safe subset exists. Keep the original protocol and negative result immutable.

## Fixed inputs and information boundary

Exactly the same four already-consumed public v0.6.7 mutation matrices (Chart-1, Lang-9, Math-1, Time-4) and their frozen manifest/digest/selection lock. No replacements. All methods see exactly the entire v0.6.7 **development** mutant matrix, and must satisfy the same coverage target. Previously exposed outer columns are scored only after subset selection. They are **not independently sealed data**; this is a post-hoc development correction, *never* a confirmatory result.

No arbitrary test-count limit and **no automatically reverting to the full suite**. Algorithms stop after meeting the known feasible coverage constraint, then run the same reverse-delete pruning.

## Feasible targets

- **C1**: at least one detecting test for every development mutant detectable by the full eligible suite.
- **C2**: min(2, total available detecting tests) retained witnesses for each development mutant. This is redundancy protection, not a universal future-defect guarantee.

Both goals are known feasible for the full development data by construction. Achieved suite size is a measured *outcome*, not a fixed input.

## Same-information baselines

- Standard greedy set cover: maximum marginal uncovered/witness shortfall.
- Rare-mutant-weighted greedy: inverse square root of mutant detection frequency.
- Standard observational partition-refinement greedy: count newly separated mutant pairs among coverage-progressing candidates.
- Relation proxy: frozen combination of normalized coverage progress (0.6) and partition discrimination (0.4), requiring positive coverage progress. It is a *classical-combination proxy*, **not a novel OARL or RCC coherence certifier**.
- SciPy/HiGHS mixed-integer set-cover/multicover solver with **4 s** cap per case and goal: logs incumbent, dual bound and gap. Never label its result globally optimal unless solver certifies; compare the better of solver's candidate and greedy's feasible candidate when time limited.

These baselines address the main error: no arbitrary safety gate makes all methods vacuously retain the complete original suite. They do **not** imply guaranteed generalization to unseen mutants.

## Evaluation ledger

For each case, method and target report: development feasibility, retained test count/fraction, previously exposed outer detectable mutants missed relative to the full suite, mutant detection vector counts, evaluated candidates, partition operations, elapsed algorithm time, source manifest hash and complete selected row IDs. Full pre-provided development matrix evidence cells are charged identically to all methods. No measured test-execution time savings. Solver overhead and design computation are different kinds of costs.

**Interpretation/stop rule:** Evaluate retained-count vs outer detection-loss tradeoffs, not just total coverage on development data. No RCC-specific comparative utility is established unless the relation proxy offers a superior safety–retention–cost tradeoff relative to the strongest ordinary baseline on multiple datasets. A conventional tie/loss or merely lower selected-test count with lost outer mutants is a negative comparative result. Do not retune on these already-burned outer cases and relabel the outcome confirmatory.

## Execution

```bash
cd "$HOME/oarl-v067-validation/OARL"
git pull --ff-only origin research/v067-safe-quotient-development-v01
source .venv/bin/activate
python -m pip install "scipy>=1.15"
python -m pytest -q tests/test_v068_feasibility_audit.py
python scripts/run_v068_feasibility_audit.py \
  --manifest "$HOME/oarl-v067-validation/prepared/manifest.json" \
  --data-root "$HOME/oarl-v067-validation/prepared/data" \
  --out "$HOME/oarl-v067-validation/FEASIBILITY_RESULT.json"
```
