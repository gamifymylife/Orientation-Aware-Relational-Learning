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
| v0.6.2 | Does repeating a fixed boundary add missing information directions? | Fisher magnitude grew under repetition but rank stayed 2/3; one new depth-2 circuit completed rank. Generic D-optimality tied the OARL selector. | **Boundary result supported; no OARL advantage** |
| v0.6.3 | Can response-level quotienting safely reduce a fixed downstream D-optimal search? | OARL compressed 42.5% but accepted 555 task-false merges. | **Safety gate failed** |
| v0.6.4 | Can direct finite-Fisher certification repair safety? | Zero evaluator-defined false merges but zero compression at a nominal 1.9304B view-shot cost. Its finite-difference oracle was later shown to fragment exact zero-Fisher classes. | **Utility gate failed; evaluator interpretation corrected** |
| v0.6.5 | Does learned opportunity remain after known canonicalization and analytic structural transport? | Held-out depth 8: `512 views -> 256 physical circuits -> 50 exact classes`, identical D-optimality, zero Bernoulli shots. The operational oracle was also 50 classes. | **Generic structural baseline passed; learned-discovery suitability failed** |
| v0.6.6 | Do external mutation-test matrices contain a hidden exact quotient suitable for prospective certification? | Lang, Math and Time had 43–87% exact held-out compression with preserved mutation coverage, but Closure retained only 67 eligible tests. Generic development signatures made 51,316 held-out false merges. | **Full suitability gate failed; three matrices expose a real target** |
| DREAM4 | Does intervention identity carry directed mechanism information on a third-party executable benchmark? | Official Size100 confirmatory gate not yet run. | **Pending** |

## Strongest current claim

> A fixed observational boundary can hide mechanism distinctions that become visible under another legitimate boundary. Exact, task-preserving orientation structure can also remove substantial redundant experimental computation. External mutation matrices now expose a substantial hidden quotient, but no external benchmark yet demonstrates that an OARL-specific learner can discover it safely and more efficiently than generic baselines.

That is deliberately narrower than claiming a general causal-discovery or equivalence-discovery algorithm.

## v0.6.6 external mutation suitability result

The preregistered gate used independently authored Defects4J mutant-test kill matrices. Tests are candidate experiments; exact equality of held-out mutant kill vectors defines the evaluator relation.

| Matrix | Eligible tests | Oracle classes | Compression | Development-signature false merges | RAW → oracle score evaluations |
|---|---:|---:|---:|---:|---:|
| Closure-118 | 67 | 56 | 16.42% | 1 | 1,102 → 893 |
| Lang-33 | 258 | 147 | **43.02%** | 51 | 4,970 → 2,750 |
| Math-22 | 225 | 114 | **49.33%** | 182 | 2,847 → 1,404 |
| Time-6 | 1,225 | 165 | **86.53%** | 51,082 | 24,310 → 3,110 |

The full gate failed because every matrix was required to retain at least 200 eligible tests and Closure-118 retained 67. The other three matrices show the first strong external residual target that is neither a metadata duplicate nor exactly calculable from a public model. This is benchmark evidence, not an OARL algorithm win.

See [`evidence/v066/V066_RESULT.md`](evidence/v066/V066_RESULT.md).

## v0.6.5 decisive structural audit

The preregistered held-out depth-8 gate separated known outcome relabelling from physical-circuit compression and replaced the numerically unstable finite-difference oracle with exact analytic `SO(3)` transport.

| Method | Classes | Compression beyond physical baseline | D-opt logdet | Score evaluations | Bernoulli shots |
|---|---:|---:|---:|---:|---:|
| RAW-VIEWS | 512 | — | 12.3273695 | 4,096 | 0 |
| VIEW-CANONICAL | 256 | 0.00% | 12.3273695 | 2,048 | 0 |
| STRUCTURAL-TRANSPORT | **50** | **80.47%** | **12.3273695** | **400** | **0** |
| OPERATIONAL-ORACLE | **50** | **80.47%** | **12.3273695** | **400** | 0 |

Generic model-based structural transport exactly exhausted the oracle opportunity. The planned adaptive learned stage was therefore not run: there was no nontrivial residual target on which OARL could establish incremental utility.

The same audit corrected two v0.6.4 interpretations. Its “exact” oracle was a central finite-difference evaluator that split exact zero-Fisher classes, and its 1.9304B shot count treated deterministic ordinary/complement relabellings as independent physical experiments. The frozen v0.6.4 result remains preserved, with the correction documented separately.

See [`evidence/v065/V065_RESULT.md`](evidence/v065/V065_RESULT.md) and [`evidence/v064/EVALUATOR_CORRECTION_NOTE.md`](evidence/v064/EVALUATOR_CORRECTION_NOTE.md).

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
- v0.6.5 does not establish learned equivalence discovery: its successful method uses public model structure and is a generic analytic baseline.
- The pyGSTi circuit family is not a valid remaining test of OARL-specific learned quotient discovery once known analytic transport is admitted.
- v0.6.6 does not test an OARL-specific learner; its mutation matrices establish a target, not a learned advantage.
- Exact equality on development mutant signatures is not safe evidence of held-out equivalence.
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
evidence/v062/            Fisher information-span audit
evidence/v063/            frozen response-level safe-quotient failure
evidence/v064/            frozen task-aligned gate plus evaluator correction
evidence/v065/            structural-baseline and evaluator audit
evidence/v066/            external mutation suitability preregistration and result
external/historical/      Meselson–Stahl and Luria–Delbrück replay
external/mutation/v066/   pinned compact mutant-test kill matrices and provenance
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
python scripts/run_v062_boundary_information_audit.py
python scripts/run_v063_safe_quotient_gate.py
python scripts/run_v064_task_aligned_gate.py
python scripts/run_v065_structural_baseline_audit.py
```

For the external mutation suitability gate:

```bash
pytest -q tests/test_mutation_equivalence.py
python scripts/run_v066_mutation_suitability.py
```

For DREAM4:

```bash
pytest -q external/dream4/v02/tests
python external/dream4/v02/run_dream4_gate.py --root /path/to/DREAM4 --size 100 --out external/dream4/v02/outputs
```

## Research integrity

Negative results are first-class evidence here. Earlier versions are not deleted when a hypothesis fails, and corrections are versioned rather than silently rewriting frozen apparatus. The failed v0.5B pilot, the CSuite benchmark-suitability failure, the failed v0.6.1/v0.6.3/v0.6.4 gates, the v0.6.5 pyGSTi learned-discovery suitability failure and the v0.6.6 four-matrix suitability failure remain documented.

The authoritative claim-by-claim status is in [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md).

## Status

Research prototype. **No external OARL-specific learned-discovery advantage is currently established.** v0.6.6 found a promising black-box target in mutation-test matrices, but its full suitability gate failed and no learner was tested. The next valid step is a new-fault prospective certification gate—not reuse of the inspected held-out columns.
