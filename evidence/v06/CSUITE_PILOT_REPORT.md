# v0.6 CSuite Pilot Suitability Report

Status: **PILOT / NOT CONFIRMATORY**

Workflow run: `33471891858`

Head commit: `8746ae0ed22ae45e8079115a710fb0b5c7c44746`

Artifact: `v06-csuite-pilot`, artifact ID `9786809506`, artifact ZIP SHA-256 `fd7a8e6854e075309907a3f0b8975821012d2b23a91a85cbbe340217ba9a5034`.

## Purpose

This run was intended to determine whether Microsoft CSuite can serve as the primary third-party **orientation-equivalence discovery** gate for OARL. It was explicitly a pilot/adaptor-development run, not confirmatory evidence.

## Reproducibility

Pinned upstream release: `microsoft/csuite` `v0.1`.

| Dataset | Release ZIP SHA-256 | interventions.json SHA-256 |
|---|---|---|
| `lingauss` | `e788d08a7da7d4d3497b156d10b032ebde2f91f4063a35eaf7b7d5b1003d7f10` | `2fdb719cd2bf1620447f1eed56a66097974317551c7ed071bbbf0c126fbf7d33` |
| `nonlin_simpson` | `dda75c813fb81dc463a274cc454766d1753a96cc13da15b5b3d43e200530cd75` | `bbd2ffda83e91203c4cb00480f8dd3a02383705578cd984ea7aa495f1e9a38cc` |
| `cat_to_cts` | `0266d265feb290a72083a1ca90687bf6167f2be13ac3cb29bfc63c9c3826c403` | `68ce5cfcd5105f1ddc663754e4c640def87e435266678856331ce3f3d250ca23` |

The first successful pilot used the corrected coordinate-preserving response representation and deterministic 50/50 discovery/holdout split. Unit tests: **9 passed**.

## Pilot result

| Dataset | Candidate views | Pair challenges | Exact duplicate calls | Similarity-equivalent calls | Holdout affine NRMSE |
|---|---:|---:|---:|---:|---:|
| `lingauss` | 1 | 0 | 0 | 0 | n/a |
| `nonlin_simpson` | 2 | 1 | 0 | 0 | 0.380515 |
| `cat_to_cts` | 1 | 0 | 0 | 0 | n/a |

For the only available pair (`nonlin_simpson`), holdout response correlation was `0.924775`, but the best positive-affine holdout transport still had normalized RMSE `0.380515`. This is not evidence for a safe quotient.

## Decision

**CSuite is not suitable as the primary OARL equivalence-discovery benchmark in its published v0.1 intervention packaging.**

The decisive reason is structural rather than algorithmic: the pilot systems expose only one or two intervention environments each, yielding zero or one pair challenge per system. That is insufficient to estimate false-merge risk, recall, abstention, quotient compression, or a meaningful safety/efficiency Pareto frontier.

This is a useful negative result. CSuite remains valuable as an independently authored causal mechanism-discrimination / intervention-response stress test, but it should not be forced into a role it was not designed to serve.

## Consequence for v0.6

Do **not** proceed to a CSuite confirmatory equivalence gate by inventing additional views or OARL-defined equivalence labels. That would weaken the external-validity claim.

The next primary external gate should use a third-party domain where observational equivalence classes are independently defined and nontrivial. Gate-set tomography is a strong candidate because gauge-equivalent gate-set representations are formally known to produce identical observable circuit probabilities while differing in representation; a generic OARL method can then be tested against the domain-specific gauge machinery rather than defining its own truth.
