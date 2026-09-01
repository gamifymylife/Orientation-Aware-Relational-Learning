# Reproducibility

## Test suites verified during consolidation

- v0.1 archive: **7 passed**
- v0.2 archive: **12 passed**
- v0.4/current: **22 passed**
- DREAM4 v0.1 harness: **3 passed**

The current CI runs the live v0.4 test suite and the corrected DREAM4 v0.2 tests. Historical source snapshots are retained so their original suites can also be rerun independently.

## Current package

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q
pytest -q external/dream4/v02/tests
```

## Frozen evidence

Reports and result tables under `evidence/` should be treated as immutable evidence snapshots. New experimental revisions should create a new version directory rather than modify old evidence in place.
