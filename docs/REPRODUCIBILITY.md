# Reproducibility

## Test suites verified during consolidation

- v0.1 archive: **7 passed**
- v0.2 archive: **12 passed**
- current live suite through v0.6.5: **43 passed**
- DREAM4 v0.1 harness: **3 passed**

The current CI runs the live test suite and the corrected DREAM4 v0.2 tests. Historical source snapshots are retained so their original suites can also be rerun independently.

## Current package

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q
pytest -q external/dream4/v02/tests
```

## External pyGSTi structural audit

```bash
python -m pip install 'pygsti==0.10.2'
python scripts/run_v065_structural_baseline_audit.py --out evidence/v065/outputs
```

The v0.6.5 runner regenerates:

- `summary.json` and `summary_compact.json`;
- the exact structural and operational class memberships;
- the three-step finite-difference numerical audit;
- the retrospective v0.6.4 evaluator/accounting correction.

The committed concise outputs are `evidence/v065/summary_compact.json` and `evidence/v065/numerical_audit.csv`. CI reruns the complete gate and checks the frozen structural and suitability outcomes.

## Frozen evidence

Reports and result tables under `evidence/` should be treated as immutable evidence snapshots. New experimental revisions should create a new version directory rather than modify old evidence in place.
