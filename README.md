# Orientation-Aware Relational Learning (OARL)

> **Mechanism identifiability can depend on the boundary from which a system is interrogated.**

OARL is a falsification-oriented research programme about **boundary-aware mechanism identification**: when the same latent relation can be interrogated through multiple admissible input/output orientations, which distinctions are real, which are representational, and which experimental views are redundant?

The programme has changed materially as evidence accumulated. The original special acquisition score did **not** survive its confirmatory benchmark. The strongest surviving direction is now **certified structural compression**: discover or certify when experimental orientations are equivalent, quotient only those distinctions that are safe to remove, and otherwise abstain.

## What the evidence currently supports

| Version | Question | Result | Status |
|---|---|---|---|
| v0.1 | Does changing orientation expose hidden mechanism distinctions? | Orientation search beat a fixed boundary in controlled worlds; the proposed full scoring rule did not beat generic OED. | Support for boundary value; warning on scoring |
| v0.2 | Does the static stability/cost penalty improve generic OED? | Frozen calibration selected `lambda=0, gamma=0`; Full OARL became Generic OED. | **Falsified** |
| v0.3 | Can exact equivalence remove redundant OED computation? | 24→4 quotient preserved paired outcomes and cut score evaluations **83.3%**; scaling reached **98.4%** at 256→4. | **Supported conditionally on correct structure** |
| v0.4 | What happens when structural metadata is wrong? | False splits mostly cost efficiency; false merges and invalid-as-valid errors can damage correctness severely. | **Supported in controlled stress tests** |
| v0.5A | Can exact quotient structure be discovered rather than supplied? | Exact candidate-model geometry recovered equivalence/transport with zero false merges in the frozen synthetic gate; expensive quadrature scoring showed an end-to-end break-even regime. | **Supported in the exact synthetic construction** |
| v0.5B.1 | Can a conservative certifier recover structure from finite noisy predictive evidence? | **0 false equivalences across 72,600 held-out distinct pairs**; 1.000 pair precision, 0.2757 recall, 0 mapping errors, 17.9% mean compression. | **Passed preregistered synthetic finite-noise gate** |
| Historical | Is boundary-dependent identifiability an internally invented phenomenon? | Meselson–Stahl and Luria–Delbrück can be replayed as coarse-vs-structure-preserving boundary cases. | External historical support for the narrow boundary claim |
| DREAM4 | Does intervention identity carry directed mechanism information on a third-party executable benchmark? | Official Size100 confirmatory gate not yet run. | **Pending** |

## Strongest current claim

> A fixed observational boundary can make distinct candidate mechanisms observationally equivalent; another legitimate boundary can expose the distinction. In the current exact affine/permutation synthetic family, a precision-first certifier can recover a useful subset of orientation equivalences from finite noisy predictive evidence while abstaining on ambiguous cases, permitting partial structural compression with no observed false merges in the preregistered held-out gate.

That is deliberately narrower than claiming a general causal-discovery algorithm.

## v0.5B.1 headline

The finite-noise gate was designed around the v0.4 asymmetry: **false merges are more dangerous than missed compression**. An initial 500-sample pilot did false-merge a distinct pair and was rejected. The replacement post-pilot protocol was frozen before the full held-out run.

Confirmatory result:

- **72,600** truly distinct orientation-pair challenges;
- **0** false `EQUIVALENT` certificates;
- **400** equivalence worlds;
- pairwise precision **1.000**;
- pairwise recall **0.2757**;
- **829** accepted direct equivalence certificates;
- **0** accepted intervention-mapping errors;
- maximum accepted scale error **3.92%**;
- maximum accepted offset error **0.0212 sigma**;
- mean discovered compression **17.9%**.

See [`evidence/v05b/V05B_CONFIRMATORY_REPORT.md`](evidence/v05b/V05B_CONFIRMATORY_REPORT.md).

## What is *not* established

- OARL is not a demonstrated state-of-the-art active causal-discovery algorithm.
- The v0.2 stability/cost penalty does not improve generic OED on the tested action space.
- v0.5B.1 does **not** infer semantic/physical admissibility; admissibility remains an external constraint.
- Approximate quotienting is not yet proven safe in arbitrary real systems.
- The finite-noise thresholds are not shown to transfer beyond the current Gaussian affine/permutation family.
- Learned-representation generalization has not yet been demonstrated.
- End-to-end savings for the finite-noise certifier, including certificate acquisition cost, have not yet been demonstrated against exhaustive Generic OED.
- The official DREAM4 Size100 confirmatory gate remains pending.

## Repository map

```text
src/oarl_bench/           current implementation, including v0.5 certifiers
scripts/                  frozen benchmark and confirmatory runners
tests/                    automated safety and regression tests
archive/v01/              historical v0.1 code snapshot
archive/v02/              historical v0.2 code snapshot
evidence/v01/             v0.1 smoke evidence
evidence/v02/             v0.2 negative confirmatory evidence
evidence/v03/             exact quotient / Gate-2 evidence
evidence/v04/             structural-metadata error evidence
evidence/v05a/            exact structure-discovery evidence
evidence/v05b/            finite-noise preregistration, failed pilot note and confirmatory evidence
external/historical/      Meselson–Stahl and Luria–Delbrück replay
external/dream4/v01/      original frozen DREAM4 harness
external/dream4/v02/      preregistration-aligned corrected harness
paper/                     August 2026 working paper
docs/                      claims ledger, roadmap and provenance
```

## Reproduce the current benchmark

Python 3.10+:

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q
PYTHONPATH=src python scripts/run_v03.py
PYTHONPATH=src python scripts/run_v04.py
python scripts/run_v05b.py
```

The v0.3 quadrature scaling run is intentionally computationally expensive. Frozen outputs are included under `evidence/v03/outputs/`.

For DREAM4:

```bash
pytest -q external/dream4/v02/tests
python external/dream4/v02/run_dream4_gate.py --root /path/to/DREAM4 --size 100 --out external/dream4/v02/outputs
```

## Research integrity

Negative results are first-class evidence here. Earlier versions are not deleted when a hypothesis fails, and corrections are versioned rather than silently rewriting frozen apparatus. The failed v0.5B pilot remains documented alongside the successful post-pilot v0.5B.1 protocol. The authoritative claim-by-claim status is in [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md).

## Status

Research prototype. **v0.5B.1 has passed its synthetic finite-noise structural-certification gate.** The next scientific burden is external and representational generalization: third-party executable systems, learned representations, approximate-equivalence calibration, and end-to-end certification economics.
