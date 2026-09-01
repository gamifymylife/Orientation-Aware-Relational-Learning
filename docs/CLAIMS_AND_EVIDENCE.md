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
| The external pyGSTi candidate experiment family contains substantial removable redundancy for the fixed D-optimal task. | **Supported in v0.6.3** | oracle quotient `508 → 170` classes (66.5% compression) with exactly the RAW D-opt logdet 11.3141815 and selected depth cost 56 | Replication in other tasks/domains would broaden scope. |
| Finite response-level similarity is a safe certificate of exact task-relative Fisher/D-optimal equivalence. | **Falsified in v0.6.3** | OARL-XFIT accepted 555 task-false merges; POINT 1,143; UCB 1,032 | A new task-aligned certificate must bound information/decision distortion directly. |
| OARL-XFIT safely learns the hidden task-equivalence quotient on the external pyGSTi family. | **Falsified on the preregistered v0.6.3 gate** | 42.5% compression and preserved D-opt outcome, but 555 accepted task-false merges; zero-false-merge gate failed | Requires a new prospective method/version; do not retune v0.6.3 thresholds on the same data. |
| Cross-fit + abstention improves the response-compression safety tradeoff over point/UCB baselines. | **Supported descriptively in v0.6.3, not enough for a safety claim** | false task merges: OARL 555 vs UCB 1,032 vs POINT 1,143; OARL preserved RAW D-opt while UCB/POINT changed it | Replicate with task-aligned certification and fresh data. |
| OARL can infer semantic/physical admissibility reliably from raw finite noisy evidence. | **Not demonstrated** | v0.5B.1 treats admissibility as external; later external gates separate observational from task truth | Requires a separate admissibility-certification programme with invalid-as-valid safety gates. |
| Approximate quotienting is safe with useful coverage. | **Not demonstrated generally** | v0.4 downstream sensitivity; v0.6.1 boundary failure; v0.6.3 task-equivalence failure | Requires calibrated task-/decision-relative distortion bounds plus abstention. |
| Finite-noise certification is end-to-end cheaper than exhaustive Generic OED. | **Not demonstrated** | v0.6.3 OARL reduced D-opt score evals 4,064→2,336 but failed safety; structural-work break-even was ~1,511 probability-cell ops per score evaluation | Must pass safety first, then show total acquisition/compute advantage. |
| OARL beats generic structural equivalence methods on a third-party executable benchmark. | **Not demonstrated** | v0.6.3 OARL was not strictly dominated by POINT/UCB but failed its own safety gate; v0.6.2 tied D-optimality | A fresh task-aligned gate must pass safety and improve a useful frontier over generic/decision-theoretic baselines. |
| OARL is state of the art in causal discovery / active inference. | **Not claimed** | — | Would require specialist baselines and external benchmarks. |

## Current methodological interpretation

The strongest surviving architecture is not a replacement for ordinary Bayesian or Fisher-optimal experimental design. It is a candidate **structural safety/compression layer** around it:

```text
candidate experimental views
    ↓
task-aligned structural certification
    ├── certified equivalent -> quotient/transport permitted
    ├── certified distinct   -> keep separate
    └── unknown              -> abstain; keep separate
    ↓
risk-bounded quotient
    ↓
standard experimental design / inference
```

v0.5B.1 showed that finite-noise structural certification can work in the synthetic affine/permutation family when the evidence representation matches the equivalence structure being certified. v0.6.1 exposed **boundary extrapolation uncertainty**: confidence can become high inside a shallow boundary while remaining wrong about an unseen deeper boundary.

v0.6.2 then separated information magnitude from information span in an external executable model. The initial depth-1 pyGSTi boundary had Fisher rank 2 of 3. Repetition by 1000 scaled the visible eigenvalues but left rank at 2. One new depth-2 circuit raised rank to 3. The OARL-motivated null-space selector tied greedy D-optimality, so this was conceptually supportive but not an OARL algorithmic advantage.

v0.6.3 held the downstream D-optimal optimizer fixed and tested the structural layer directly. The oracle established a large real opportunity: 508 candidate views collapse to 170 task-equivalent classes with no downstream change. OARL-XFIT found a 292-class quotient and preserved the RAW D-optimal result, but its accepted pair relation had only 0.262 precision against the frozen exact Fisher-task oracle and included 555 false task merges. Cross-fit/abstention was safer than POINT/UCB, but the primary safety gate failed.

The immediate burden is therefore **not another generic response-similarity threshold**. The next prospective method must certify the object that downstream inference actually requires preserving: Fisher-information geometry, decision risk, acquisition value, or an explicit Blackwell/Le Cam-style task deficiency bound. Only after such a task-aligned certificate passes on fresh evidence should end-to-end compression economics be treated as an OARL utility claim.
