# Claims and Evidence Ledger

This file is the authoritative claim boundary for the repository. It intentionally separates conceptual propositions, demonstrated benchmark results, falsified method claims and open hypotheses.

| Claim | Status | Evidence | What would change the status? |
|---|---|---|---|
| A mechanism distinction can be hidden by one observational boundary and exposed by another. | **Supported** in controlled, historical and external executable cases | `evidence/v01/`, `evidence/v02/`, `external/historical/`, `evidence/v061/`, `evidence/v062/` | Broader external failures would narrow domain scope. |
| Orientation/boundary is a legitimate experimental-design variable when multiple admissible views exist. | **Supported conditionally** | synthetic orientation controls; historical replay; pyGSTi shallow-vs-deep boundary case; v0.6.2 rank audit | Additional third-party domains would strengthen scope. |
| `IG - lambda log(1+K) - gamma C` improves generic OED. | **Falsified on the tested benchmark** | `evidence/v02/V02_CONFIRMATORY_REPORT.md` | A materially different formulation must be treated as a new hypothesis, not a rescue of v0.2. |
| Exact orientation equivalence can be quotiented without changing Bayesian mechanism identification. | **Supported in the exact synthetic construction** | `evidence/v03/` and `test_transport_update_matches_raw_update` | Formal generalization and independent reproduction would strengthen it. |
| Exact quotienting can reduce acquisition-score computation. | **Supported** | v0.3: 83.3% at 24→4; 98.4% at 256→4 | End-to-end accounting must include certificate-discovery cost. |
| Exact quotient structure can be discovered from candidate-model likelihood geometry without hidden class labels. | **Supported in the exact synthetic construction** | `evidence/v05/`, `src/oarl_bench/certification.py` | External and less structured model families would strengthen it. |
| Incorrect equivalence declarations are riskier than conservative missed equivalences. | **Supported in controlled stress tests and reinforced externally** | `evidence/v04/`; v0.6.1 sealed false-merge gate; v0.6.3 task-false merges | External downstream studies should quantify decision consequence, not just count merges. |
| Incorrectly admitting semantically invalid high-information orientations can be catastrophic. | **Supported as an adversarial failure mode** | v0.4 false-admissibility-positive control | Do not interpret the synthetic magnitude as a universal real-world percentage. |
| A precision-first certifier can infer a useful subset of exact orientation equivalences from finite noisy predictive evidence. | **Supported in the preregistered affine/permutation synthetic gate only** | `evidence/v05b/`: 72,600 distinct-pair challenges, 0 false equivalences, precision 1.000, recall 0.2757 | External replication with the same safety level is still missing. |
| Accepted finite-noise transports can be recovered accurately enough for the current synthetic quotient. | **Supported in v0.5B.1** | 829 accepted direct certificates; 0 mapping errors; max scale error 3.92%; max offset error 0.0212 sigma | Stress under approximate/non-affine transport and external systems. |
| Gauge-equivalent internal representations can be substantially different while remaining observationally identical. | **Externally confirmed, but not novel to OARL** | `evidence/v061/` pyGSTi smoke; established GST gauge theory | This is a domain fact used as external ground truth, not an OARL discovery claim. |
| Direct shallow probability equivalence can fail when a deeper observational boundary amplifies a mechanism difference. | **Supported in v0.6.1 pyGSTi gate** | `op_noise=0.010`: sealed max difference 0.02926 > epsilon 0.020 while shallow classifiers often merge | Replicate in other dynamical/iterated systems and with other boundary families. |
| The frozen v0.6.1 OARL cross-fit + depth-stability certificate safely extrapolates equivalence to unseen deeper circuits. | **Falsified on the preregistered external gate** | 522 operational false merges; primary zero-false-merge check failed | A materially different prospective method is required. |
| The v0.6.1 OARL certificate improves the shallow safety/precision tradeoff over direct probability equivalence. | **Supported descriptively, not sufficient for the strong gate** | aggregate precision 0.8355 vs 0.7497; false merges 522 vs 1,191 | A safety-valid method must also preserve the task across boundary changes. |
| More finite samples are sufficient to repair an insufficient observational boundary. | **Falsified in the v0.6.1 boundary case** | OARL false merges on `op_noise=0.010` rose from 0/300 at 50k to 282/300 at 500k as shallow uncertainty vanished | A richer boundary or justified extrapolation model is required. |
| Repeating a fixed rank-deficient observation boundary increases local information span. | **Falsified / structurally impossible in the frozen local audit** | v0.6.2: depth-1 Fisher rank stayed 2 and nullity 1 under repetition factors 1, 10, 100 and 1000 | A different boundary can change span; repetition of the same fixed local information operator cannot. |
| A new admissible boundary can expose a local mechanism direction absent from a repeated fixed boundary. | **Supported in v0.6.2 pyGSTi audit** | one depth-2 circuit increased Fisher rank from 2 to 3; all 126 probes jointly had full rank | Replicate on fresh mechanism families and non-quantum systems. |
| OARL's null-space selector is superior to classical optimal experimental design for filling missing information directions. | **Not demonstrated; v0.6.2 tied D-optimality** | null-space coverage and greedy D-optimality both reached rank 3 with one depth-2 circuit at added depth cost 2 | A fresh benchmark must show lower cost or higher safety than D/E-optimal and generic rank methods. |
| The external pyGSTi candidate experiment family contains substantial removable redundancy for the fixed D-optimal task. | **Supported and strengthened by v0.6.3–v0.6.4** | v0.6.3 exact oracle `508→170`; v0.6.4 operational task oracle `508→91`, both preserving RAW D-opt logdet 11.3141815 and depth cost 56 | Replication in other tasks/domains would broaden scope. |
| Finite response-level similarity is a safe certificate of task-relative Fisher/D-optimal equivalence. | **Falsified in v0.6.3 and again by v0.6.4 TV-UCB** | v0.6.3 OARL-XFIT: 555 task-false merges; v0.6.4 TV-UCB: 1,196 false merges and logdet loss 0.2652 | Task-aligned information/decision certification is required. |
| OARL-XFIT safely learns the hidden task-equivalence quotient on the external pyGSTi family. | **Falsified on v0.6.3** | 42.5% compression and preserved D-opt outcome, but 555 accepted task-false merges | Requires a materially different certificate; v0.6.3 cannot be retuned post hoc. |
| Cross-fit + abstention improves the response-compression safety tradeoff over point/UCB baselines. | **Supported descriptively in v0.6.3, not enough for a safety claim** | false task merges: OARL 555 vs UCB 1,032 vs POINT 1,143; OARL preserved RAW D-opt while UCB/POINT changed it | Replicate with useful task-aligned certification. |
| Direct task-aligned Fisher/D-optimal certification can eliminate the v0.6.3 false-merge failure at the frozen v0.6.4 evidence level. | **Supported for safety, but with zero useful coverage** | v0.6.4 FIM-UCB and OARL-TASK-XFIT: 0 false merges and exact RAW D-opt preservation, but 0 accepted equivalences / 0% compression | A new estimator/evidence strategy must retain safety while certifying a useful subset. |
| The frozen v0.6.4 OARL-TASK-XFIT certificate provides useful safe compression. | **Falsified on the preregistered gate** | 508 classes, 0% compression; compression ≥20% gate failed despite 0 false merges | New version required; do not relax v0.6.4 bounds on the same seeds. |
| Finite task-space point estimates contain some safe quotient signal in v0.6.4. | **Supported descriptively, very low coverage** | FIM-POINT accepted 21/2,543 shortlisted pairs, precision 1.0, 3.35% compression, unchanged D-opt result | Replicate prospectively and add uncertainty without eliminating coverage. |
| Conservative finite-Fisher uncertainty bounds are economically useful at the current evidence budget. | **Not supported; v0.6.4 is strongly negative** | 1.9304B Bernoulli shots per learned method; FIM-UCB/OARL saved zero downstream score evaluations; FIM-POINT break-even ~14.2M shot units per score evaluation saved | Sequential/adaptive evidence or structural transport must reduce evidence burden by orders of magnitude. |
| OARL can infer semantic/physical admissibility reliably from raw finite noisy evidence. | **Not demonstrated** | v0.5B.1 treats admissibility as external; later external gates separate observational from task truth | Requires a separate admissibility-certification programme with invalid-as-valid safety gates. |
| Approximate quotienting is safe with useful coverage. | **Not demonstrated generally** | v0.4 downstream sensitivity; v0.6.1 boundary failure; v0.6.3 false merges; v0.6.4 safe-but-zero-coverage certificate | Requires a task-relative certificate that achieves both safety and nontrivial recall/compression. |
| Finite-noise certification is end-to-end cheaper than exhaustive Generic OED. | **Not demonstrated; current external evidence is negative** | v0.6.3 reduced score evals but failed safety; v0.6.4 safe methods gave 0–3.35% compression at 1.9304B evidence shots | Must drastically reduce certificate evidence before economics can be positive. |
| OARL beats generic structural equivalence methods on a third-party executable benchmark. | **Not demonstrated** | v0.6.4 OARL-TASK-XFIT matched generic pooled FIM-UCB at 0% compression; no incremental utility observed | A fresh gate must improve the safety/coverage/cost frontier beyond generic task-space confidence methods. |
| OARL is state of the art in causal discovery / active inference. | **Not claimed** | — | Would require specialist baselines and external benchmarks. |

## Current methodological interpretation

The strongest surviving architecture remains a candidate structural safety/compression layer around standard experimental design:

```text
candidate experimental views
    ↓
structural / transport proposal
    ↓
task-aligned certification
    ├── certified equivalent -> quotient/transport permitted
    ├── certified distinct   -> keep separate
    └── unknown              -> abstain; keep separate
    ↓
risk-bounded quotient
    ↓
standard experimental design / inference
```

v0.6.3 showed that a response-level certificate can compress substantially but certify the wrong relation: similar probabilities can hide different local Fisher geometry. v0.6.4 then moved the certificate into the correct task space. That fixed the safety failure—zero operational false merges and exact downstream preservation—but the bootstrap uncertainty envelope accepted no equivalences at all.

The external family itself is not the problem. The evaluator-only v0.6.4 quotient collapses 508 views to 91 operational task classes (82.1% compression) with no D-optimal change, and 1,263 true task-equivalent pairs were present inside the learned shortlist. The bottleneck is **finite-evidence certifiability**. At 100,000 shots per split, local derivative/Fisher uncertainty is too large for the frozen conservative bound; simply scaling IID evidence across all 508×19 probe cells is also economically unattractive.

The immediate burden is therefore no longer to invent another global similarity threshold or another generic OED criterion. The next prospective method should exploit cheap structural/transport hypotheses first, then allocate task-aligned evidence **adaptively and selectively** only to ambiguous candidate equivalences. It must be compared against generic canonicalization/transform matching and generic sequential confidence methods. If those dominate, OARL should be narrowed to the problem formulation rather than an algorithmic advantage claim.
