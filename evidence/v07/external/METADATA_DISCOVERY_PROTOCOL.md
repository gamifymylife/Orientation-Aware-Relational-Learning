# v0.7 metadata-only candidate expansion protocol

## Status

Frozen before running this v0.7 candidate expansion. This stage may discover historical regression candidates; it may not execute OARL, inspect OARL scores, estimate complementarity, estimate quotientability, or choose cases by expected OARL advantage.

## Repositories

Search only these public software/AI framework repositories for this expansion:

- `openai/openai-agents-python`
- `microsoft/autogen`
- `pydantic/pydantic-ai`
- `langchain-ai/langgraph`
- `crewAIInc/crewAI`
- `huggingface/smolagents`
- `google/adk-python`

Existing registry sources and the five prior OARL-pilot sources are excluded.

## Metadata search

For each repository, consider merged pull requests since 2024-01-01. Candidate discovery uses PR title/body metadata only. It must not inspect code diffs, known witness locations, OARL outputs or Mechanism Diff search outputs.

## Frozen reproducibility score

Each condition is binary; repeated occurrences do not multiply a term.

Positive evidence:

- +8: body contains `regression test` or `regression tests`;
- +7: body contains `fails on main`, `fails on base`, `fails before`, or `fails without`;
- +6: body contains `reproduction`, `reproduce`, or `repro`;
- +4: body contains `test plan`, `pytest`, `unit test`, or `tests/`;
- +4: body contains `deterministic`;
- +3: body contains `mock`, `fake`, `stub`, or `local`;
- +3: title contains `fix`, `bug`, or `regression`;
- +2: body contains both `before` and `after`.

Negative evidence:

- -30: title indicates documentation/readme/typo/formatting/CI/release/dependency-only work;
- -15: body states testing was unavailable or no test could be run, unless it also describes a focused regression test.

## Ranking and retention

Within each repository:

1. exclude existing registry sources and prior OARL-pilot sources;
2. retain candidates with reproducibility score >= 6;
3. sort by descending score, then descending merged/updated timestamp, then descending PR number;
4. retain up to 12 candidates per repository for actual-revision replay review.

The retained candidates are **not admitted cases**. They remain metadata-only candidates until the v0.7 selection protocol independently verifies exact A/B pins, same-interface replay, negative controls, neutral candidate-space construction and all other admission gates.

## Contamination invariant

Every generated expansion artifact must state `oarl_executed=false`. No candidate may be removed or demoted because later OARL performance is poor. Low complementarity or low quotientability is not an admissible rejection reason.
