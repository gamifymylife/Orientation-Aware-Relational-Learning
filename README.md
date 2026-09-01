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
| v0.6 CSuite | Is CSuite suitable as an external equivalence-discovery benchmark? | The tested published systems expose too few candidate intervention views for a serious pairwise equivalence gate. | **Suitability failure preserved** |
| v0.6.1 pyGSTi smoke | Does an independent domain contain the target phenomenon? | Gauge transformations materially change internal representation while preserving all tested circuit probabilities; physical perturbations change them. | **External phenomenon confirmed; not OARL-specific utility** |
| v0.6.1 finite-shot | Can shallow finite-shot OARL certification safely generalize equivalence to unseen deeper circuits? | OARL improved precision vs direct probability equivalence but still made **522 sealed operational false merges**. More shots increased the boundary failure. | **Primary safety gate failed** |
| DREAM4 | Does intervention identity carry directed mechanism information on a third-party executable benchmark? | Official Size100 confirmatory gate not yet run. | **Pending** |

## Strongest current claim

> A fixed observational boundary can hide mechanism distinctions that become visible under another legitimate boundary. In an independently authored gate-set tomography domain, internally different gauge representations can be observationally equivalent, while a physically distinct model can look epsilon-equivalent on shallow circuits yet violate the same epsilon criterion on deeper circuits. The current OARL finite-shot certificate reduces false merges relative to direct shallow probability comparison, but it does **not** yet safely extrapolate equivalence beyond the boundary on which it was certified.

That is deliberately narrower than claiming a general causal-discovery or equivalence-discovery algorithm.

## v0.6.1 external finite-shot result

The external gate uses `pygsti==0.10.2`, 15 discovery circuits at depths 0–3 and 112 sealed evaluator circuits at depths 4–6. The confirmatory grid contains 300 held-out seeds, eight pair types and four shot budgets: **9,600 classifications per method**.

Aggregate result:

| method | operational precision | operational recall | operational false merges | abstention |
|---|---:|---:|---:|---:|
| raw parameter distance | n/a | 0.0000 | 0 | 0.0000 |
| generic probability equivalence | 0.7497 | 0.9908 | 1,191 | 0.0044 |
| OARL cross-fit + depth stability | **0.8355** | 0.7364 | **522** | 0.1695 |

The decisive failure is the `op_noise=0.010` control. Its shallow discovery behavior can remain inside `epsilon=0.020`, while the sealed deeper circuits reach a maximum difference of **0.02926**. At 50k shots OARL abstained on all of these boundary cases; at 500k shots it falsely merged 282/300. More data inside the insufficient boundary made the wrong shallow conclusion more certain.

See [`evidence/v061/FINITE_SHOT_REPORT.md`](evidence/v061/FINITE_SHOT_REPORT.md).

## v0.5B.1 synthetic finite-noise headline

The earlier synthetic gate remains important because it established that precision-first finite-noise certification can work when the discovery evidence family itself contains the relevant structural distinction.

- **72,600** truly distinct orientation-pair challenges;
- **0** false `EQUIVALENT` certificates;
- pairwise precision **1.000**;
- pairwise recall **0.2757**;
- **829** accepted direct equivalence certificates;
- **0** accepted intervention-mapping errors;
- mean discovered compression **17.9%**.

See [`evidence/v05b/V05B_CONFIRMATORY_REPORT.md`](evidence/v05b/V05B_CONFIRMATORY_REPORT.md).

## What is *not* established

- OARL is not a demonstrated state-of-the-art active causal-discovery algorithm.
- The v0.2 stability/cost penalty does not improve generic OED on the tested action space.
- v0.5B.1 does **not** infer semantic/physical admissibility; admissibility remains an external constraint.
- Approximate quotienting is not proven safe in arbitrary real systems.
- The current external finite-shot certificate does **not** safely extrapolate equivalence beyond its discovery boundary.
- The v0.6.1 depth-stability heuristic does **not** satisfy the preregistered zero-false-merge requirement.
- Physical identity cannot be inferred from finite operational equivalence with a nonzero epsilon.
- Learned-representation generalization has not yet been demonstrated.
- End-to-end savings for finite-noise certification, including certificate acquisition cost, have not yet been demonstrated against exhaustive Generic OED.
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
evidence/v05/             exact structure-discovery evidence
evidence/v05b/            finite-noise preregistration, failed pilot note and confirmatory evidence
evidence/v06/             CSuite external adapter/suitability evidence
evidence/v061/            pyGSTi smoke + finite-shot external boundary evidence
external/historical/      Meselson–Stahl and Luria–Delbrück replay
external/dream4/v01/      original frozen DREAM4 harness
external/dream4/v02/      preregistration-aligned corrected harness
paper/                     August 2026 working paper
docs/                      claims ledger, roadmap and provenance
```

## Reproduce

Python 3.10+:

```bash
python -m pip install -e '.[dev,dream4]'
pytest -q
PYTHONPATH=src python scripts/run_v03.py
PYTHONPATH=src python scripts/run_v04.py
python scripts/run_v05b.py
```

For the external pyGSTi gate:

```bash
python -m pip install 'pygsti==0.10.2'
python scripts/run_v061_pygsti_smoke.py
python scripts/run_v061_finite_shot_gate.py
```

For DREAM4:

```bash
pytest -q external/dream4/v02/tests
python external/dream4/v02/run_dream4_gate.py --root /path/to/DREAM4 --size 100 --out external/dream4/v02/outputs
```

## Research integrity

Negative results are first-class evidence here. Earlier versions are not deleted when a hypothesis fails, and corrections are versioned rather than silently rewriting frozen apparatus. The failed v0.5B pilot, the CSuite benchmark-suitability failure and the failed v0.6.1 external finite-shot safety gate remain documented.

The authoritative claim-by-claim status is in [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md).

## Status

Research prototype. **v0.6.1 has exposed boundary extrapolation as the immediate technical bottleneck.** The next high-priority gate is **v0.6.2 boundary extrapolation** on fresh held-out seeds: estimate how divergence changes as the observational boundary changes, propagate that uncertainty to unseen orientations/depths, and compare OARL against equally strong generic trend/extrapolation baselines. v0.5C admissibility and end-to-end economics remain necessary, but external generalization currently has priority.
