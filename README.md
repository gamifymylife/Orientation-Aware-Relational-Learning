# Orientation-Aware Relational Learning (OARL)

> **Mechanism identifiability can depend on the boundary from which a system is interrogated.**

OARL is a falsification-oriented research programme about **boundary-aware mechanism identification**: when the same latent relation can be interrogated through multiple admissible input/output orientations, which distinctions are real, which are representational, and which experimental views are redundant?

The programme has changed materially as evidence accumulated. The original special acquisition score did **not** survive its confirmatory benchmark. The strongest surviving direction is now **certified structural compression**: discover or certify when experimental orientations are equivalent/admissible, quotient only those distinctions that are safe to remove, and otherwise abstain.

## What the evidence currently supports

| Version | Question | Result | Status |
|---|---|---|---|
| v0.1 | Does changing orientation expose hidden mechanism distinctions? | Orientation search beat a fixed boundary in controlled worlds; the proposed full scoring rule did not beat generic OED. | Support for boundary value; warning on scoring |
| v0.2 | Does the static stability/cost penalty improve generic OED? | Frozen calibration selected `lambda=0, gamma=0`; Full OARL became Generic OED. | **Falsified** |
| v0.3 | Can exact equivalence remove redundant OED computation? | 24→4 quotient preserved paired outcomes and cut score evaluations **83.3%**; scaling reached **98.4%** at 256→4. | **Supported conditionally on correct structure** |
| v0.4 | What happens when structural metadata is wrong? | False splits mostly cost efficiency; false merges and invalid-as-valid errors can damage correctness severely. | **Supported in controlled stress tests** |
| Historical | Is boundary-dependent identifiability an internally invented phenomenon? | Meselson–Stahl and Luria–Delbrück can be replayed as coarse-vs-structure-preserving boundary cases. | External historical support for the narrow boundary claim |
| DREAM4 | Does intervention identity carry directed mechanism information on a third-party executable benchmark? | Official Size100 confirmatory gate not yet run. | **Pending** |

## Strongest current claim

> A fixed observational boundary can make distinct candidate mechanisms observationally equivalent; another legitimate boundary can expose the distinction. When multiple orientations are **certifiably equivalent**, exact quotienting can remove redundant acquisition computation without changing Bayesian mechanism-identification outcomes.

## What is *not* established

- OARL is not a demonstrated state-of-the-art active causal-discovery algorithm.
- The v0.2 stability/cost penalty does not improve generic OED on the tested action space.
- No learned structural classifier currently produces trustworthy equivalence/admissibility certificates from raw evidence.
- Approximate quotienting is not yet proven safe in arbitrary real systems.
- End-to-end savings including the cost of discovering/certifying the quotient have not yet been demonstrated.
- The official DREAM4 Size100 confirmatory gate remains pending.

That missing classifier/certifier is now the central research problem. See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Repository map

```text
src/oarl_bench/           current v0.4 implementation
scripts/                  current frozen v0.3/v0.4 runners
tests/                    current automated tests
archive/v01/              historical v0.1 code snapshot
archive/v02/              historical v0.2 code snapshot
evidence/v01/             v0.1 smoke evidence
evidence/v02/             v0.2 negative confirmatory evidence
evidence/v03/             exact quotient / Gate-2 evidence
evidence/v04/             structural-metadata error evidence
external/historical/      Meselson–Stahl and Luria–Delbrück replay
external/dream4/v01/      original frozen DREAM4 harness
external/dream4/v02/      preregistration-aligned corrected harness
paper/                     August 2026 working paper
docs/                      claims ledger, roadmap and provenance
```

## Reproduce the current benchmark

Python 3.10+:

```bash
python -m pip install -e '.[dev]'
pytest -q
PYTHONPATH=src python scripts/run_v03.py
PYTHONPATH=src python scripts/run_v04.py
```

The v0.3 quadrature scaling run is intentionally computationally expensive. Frozen outputs are included under `evidence/v03/outputs/`.

For DREAM4:

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q external/dream4/v02/tests
python external/dream4/v02/run_dream4_gate.py --root /path/to/DREAM4 --size 100 --out external/dream4/v02/outputs
```

## Research integrity

Negative results are first-class evidence here. Earlier versions are not deleted when a hypothesis fails, and corrections are versioned rather than silently rewriting frozen apparatus. The authoritative claim-by-claim status is in [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md).

## Status

Research prototype. The next gate is **v0.5 — Certified Orientation Structure Discovery**.
