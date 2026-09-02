# OARL v0.7 External Complementarity Gate — Amendment 002

**Status:** FROZEN BEFORE ANY v0.7 EXTERNAL OARL POLICY OUTCOME

This amendment fixes the Track-R real-regression probe language and the neutral-corpus bridge before any v0.7 external OARL acquisition policy is executed.

It does not weaken or replace the gates in `PREREGISTRATION.md`.

## 1. Neutral source corpus

Track-R candidates may be imported from the evaluator-only historical-regression construction programme in `gamifymylife/adaptive-distinction-engine`, branch `oarl-external-confirmation-v02`, Amendment 005.

The source programme is used only for repository identity, exact pre-fix and post-fix revision pins, proof that a real historical red/green contrast exists under the source evaluator, deterministic source rank/framework balancing, and provenance hashes.

The legacy four-policy OARL-v0.2 confirmation on that branch is not part of this study and must not be run before the v0.7 corpus is consumed.

No v0.7 case may have appeared in the prior five-case OARL pilot. No source case may be replaced because OARL performs poorly.

## 2. Historical regression test remains evaluator-only

The post-fix regression test, changed-test file, PR prose, changed implementation files, known assertion, known failing input and known witness location are curator/evaluator-only material.

They MUST NOT seed the policy experiment set, determine candidate order, determine relation edges, determine quotient classes, determine OARL utility features, or be exposed to any acquisition policy.

A candidate space built by mutating the known post-fix regression test is therefore inadmissible for confirmatory Track R.

## 3. Frozen generic Track-R experiment grammar

For each case, the experiment language is generated from the **pre-fix revision only**.

### 3.1 Seed corpus

The generator recursively enumerates Python tests already present at the pre-fix revision under conventional test roots (`test`, `tests`, and project-declared pytest testpaths where available).

Files or nodes are excluded only for objective reasons fixed in code, including non-Python files, generated snapshots, fixtures-only modules, collection failure, credential/network requirements, unsafe side effects detected by the harness, or inability to execute under the common A/B environment.

Changed-file metadata and post-fix-only tests are not inputs to this enumeration.

### 3.2 Mechanical single-site mutations

The same source-code generator is applied to every admitted repository. It produces deterministic single-site test-input mutations from supported AST primitives, including where type-compatible:

- Boolean flip;
- integer boundary neighbours and canonical boundaries;
- floating-point canonical boundaries;
- empty/non-empty string boundary substitutions;
- list/tuple/set cardinality reductions or one-element expansions;
- optional keyword omission when syntactically legal;
- repeat/count boundary perturbations when represented by supported literals.

Every mutant changes exactly one mechanically identified site. No mutation operator may use PR text, the post-fix regression test, the implementation diff or the known historical output.

Duplicate rendered mutants are removed by exact content hash.

### 3.3 Objective validity filter

Before lock, a mutant may be removed only if it is objectively invalid under the common-interface rules: parse/collection failure, import/setup failure, unsupported dependency/credential/network requirement, nondeterminism beyond the frozen tolerance, unsafe side effect, or failure to execute on one endpoint for reasons unrelated to the A/B behavioural comparison.

Validity filtering is policy-blind and its cost is recorded as `C_structure`/preflight cost. It may not use whether a mutant makes OARL look good or bad.

### 3.4 Deterministic cap and order

After exact duplicate removal and objective validity filtering, candidates are ordered by SHA-256 of their canonical policy-visible manifest representation. If more than **512** valid candidates exist, the first 512 by this hash order are retained. If fewer exist, all are retained.

The hash order is the frozen `fixed` baseline order and is also the only tie-break order available to other policies.

The confirmatory acquisition budget remains **220** probes as preregistered.

## 4. Frozen generic observation/orientation grammar

A probe execution exposes only mechanically normalized runtime observations common to both endpoints. Atomic orientations are generated from:

- pytest/run outcome category;
- process exit status;
- normalized exception class, if any;
- normalized warning count;
- bounded stdout/stderr structural summaries;
- bounded traceback/event-type sequence summaries with repository paths and semantic names anonymized;
- runtime bucket / declared execution cost;
- deterministic tuple combinations of the preceding atomic projections under one case-independent rule.

Policy-visible observations must not contain repository name, PR number, revision SHA, changed path, semantic bug label, evaluator label or known expected value.

## 5. Frozen relation construction

Relations are derived only from policy-visible static mutant structure and accumulated policy-visible observations.

Allowed static relation features include same mutation-operator family, same literal/value category, same anonymized AST call-context shape, same fixture-signature shape, same anonymized test-structure fingerprint, and same mechanically defined observation-projection family.

No relation may be authored from the historical fix.

`oarl_scrambled_relations` preserves every individual candidate, cost, observation and marginal static feature vector while deterministically permuting relation endpoints with the frozen study seed. Candidate order is unchanged. Only relational adjacency is disrupted.

## 6. Quotient safety

Track R does not delete concrete experiments merely because they share static structure.

The OARL quotient may share a planner utility evaluation only when the frozen utility function is mathematically identical for every member of the planner orbit under its policy-visible state. Every concrete experiment remains selectable. Once an observation makes utilities differ, that orbit must split.

This is a planner-utility quotient, not a claim that the underlying software behaviours are semantically or causally equivalent.

Any implementation that physically removes non-identical concrete experiments is outside this amendment and requires a new study version.

## 7. Track-R admission preflight

The policy and probe-language source hashes must be frozen before the first Track-R capability preflight on the fresh corpus.

For each source case, preflight then records:

1. exact A/B source pins and source provenance hash;
2. three-repeat historical red/green source evidence;
3. same-revision negative-control result;
4. generated experiment count and orientation count;
5. objective validity rate;
6. adapter, evaluator, relation-generator and candidate-manifest hashes;
7. whether the bounded pre-fix-derived language contains at least one reproducible A/B behavioural distinction;
8. all preflight construction/runtime cost;
9. `oarl_executed=false`.

The preflight artifact MUST NOT record the identity, rank or relation neighbourhood of the successful witness candidate. Logs must not print it.

A case lacking a reproducible distinction inside this frozen language is rejected as `BOUNDED_LANGUAGE_NO_WITNESS`; the grammar is not expanded for that case.

Cases are considered in the source programme's already-frozen rank order. The first 24 Track-R eligible cases are selected, with a minimum of 20 required to launch. No OARL outcome may affect selection.

## 8. Interpretation boundary

A positive Track-R result supports prospective external generalization only for searching real historical Python software/AI regressions inside this pre-fix-derived bounded mutation language.

It does not establish unrestricted repository-wide bug discovery, cross-language generalization, semantic mechanism identification, arbitrary-order complementarity, or Track-D decision completeness.

Track D remains a separate claim and requires the independently frozen multi-hypothesis contract.
