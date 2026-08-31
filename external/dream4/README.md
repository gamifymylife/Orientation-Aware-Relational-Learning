# DREAM4 External Gate

This folder contains the frozen external falsification gate for the official 2009 **DREAM4 In Silico Network Challenge**.

The test compares the same perturbation-response matrices under two representations:

- `KO_ID` / `KD_ID`: intervention identity is preserved;
- `KO_ERASED` / `KD_ERASED`: the response values are unchanged, but the mapping from response row to intervened gene is deterministically permuted.

The primary question is whether preserving the relation

```text
which intervention -> which response
```

improves recovery of the official directed gold-standard network.

## Run

```bash
python external/dream4/run_dream4_gate.py \
  --archive "/path/to/DREAM4 in silico challenge.zip" \
  --out outputs/dream4
```

or point `--root` at an extracted archive.

The confirmatory estimator and pass/fail criteria are frozen in [`PREREGISTRATION.md`](PREREGISTRATION.md). Do not tune the estimator against the five gold-standard networks and then report the same networks as confirmatory evidence.

## Data policy

The official DREAM4 archive is **not vendored into this repository**. Keep third-party data outside Git and pass its local path to the runner.

## Current status

**Preregistered, not yet executed in this repository.** No DREAM4 pass/fail result is claimed until the official data have been run through the frozen script.
