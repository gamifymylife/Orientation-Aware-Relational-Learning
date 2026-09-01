# External mutation benchmark v0.6.6

This adapter uses independently authored Defects4J mutant-test kill matrices from the Diversity-aware Mutation Testing artifact.

Source: <https://github.com/donghwan-shin/Diversity-aware-Mutation-Testing>

Pinned source commit: `f8d8376e0efe345161f26ff6483a404c8548fe1c`

The checked-in `.npz` files are lossless compact projections of the four preregistered CSV matrices. They retain test type, test identifier, mutant identifier and every binary kill outcome. `manifest.json` records both upstream and compact SHA-256 checksums.

Rebuild from an upstream checkout:

```bash
python scripts/prepare_v066_mutation_data.py \
  --source-root /path/to/Diversity-aware-Mutation-Testing \
  --out external/mutation/v066/data
```

Run the suitability gate:

```bash
python scripts/run_v066_mutation_suitability.py
```

This gate tests benchmark suitability only. It does not fit or evaluate an OARL-specific learner.
