# v0.6 Complementary Orientation Gate — Frozen Exact Result

## Result

The exact controlled gate **passes its preregistered safety and utility criteria**, with an important limitation: OARL beats one-step active decision learning on the pure complementarity case, but a fair generic two-step lookahead matches OARL's probe count. The surviving claim is therefore narrower than "orientation-aware search beats active learning."

## What was tested

The benchmark uses candidate-mechanism response geometry and task decisions to evaluate six exact conditions: single-view sufficiency, exact redundancy, pure XOR complementarity, misleading similarity, fundamental insufficiency, and higher-order three-view complementarity. The hidden true mechanism is used only to generate the realized observation and score the answer.

Decision completeness is exact: all mechanisms still compatible with the acquired evidence must imply the same task decision. Otherwise the system must continue or return `UNKNOWN` if all nonredundant available orientations are exhausted.

## Frozen headline

Across 32 random-order seeds, four hidden-mechanism positions, six worlds, and nine policies (6,912 policy episodes):

- OARL accuracy on resolvable worlds: **100%**.
- Correct `UNKNOWN` rate on fundamental insufficiency: **100%**.
- Mean OARL probes on resolvable worlds: **1.6**.
- Mean exhaustive probes on the same worlds: **3.6**.
- Probe reduction versus exhaustive: **55.6%**.
- Pure XOR complementarity: OARL **2 probes**, one-step active decision learning **3**, generic two-step lookahead **2**.
- Exact-redundancy planning: OARL **3** unordered pair evaluations versus **6** with the transport quotient ablated.

## Ablations

### Remove complementarity awareness

`oarl_no_synergy` retains exact redundancy quotienting but uses one-step decision utility only. On the pure XOR condition it requires 3 probes rather than OARL's 2. Thus the XOR gain is specifically attributable to modeling joint perspective value rather than to the redundancy quotient.

### Remove structural transport / quotienting

`oarl_no_transport` retains pair-synergy search but does not collapse exact equivalent orientations. On the exact-redundancy condition, planning evaluations increase from 3 to 6 while decision outcome and probe count remain unchanged. Thus the exact transport structure provides a planning/computation benefit, not a decision-accuracy benefit in this gate.

## Strong-baseline result

A fair generic two-step lookahead also solves pure XOR in 2 probes. Therefore this gate **does not establish an independent probe-count advantage over generic lookahead**. The result is instead:

1. explicit complementarity avoids the known failure mode of one-step greedy decision acquisition;
2. exact orientation quotienting reduces redundant planning work;
3. the combination reaches the same probe efficiency as generic two-step lookahead on pairwise synergy while evaluating fewer redundant pairs when exact orientation equivalence is present;
4. exact decision completeness yields calibrated `UNKNOWN` rather than forced convergence.

This is useful, but it is not yet enough to claim a generally superior adaptive orientation algorithm.

## Important higher-order boundary

The three-bit parity world is intentionally not solvable by any pair. OARL does not falsely declare sufficiency after two perspectives and reaches the correct answer after all three. However the current selector explicitly models pairwise synergy only; it does not yet discover higher-order synergy as a primitive. This is a boundary, not a success claim for arbitrary-order complementarity.

## What this proves

In an exact candidate-model setting, decision-relevant information can be non-additive across observational orientations. A one-step decision-value policy can miss a pure complementary pair, while an explicit synergy-aware policy recovers it. Exact equivalence discovery can be composed with that search to remove redundant perspective evaluations, and exact survivor-set decision completeness supports correct abstention when the available views are fundamentally insufficient.

## What this does not prove

It does not prove noisy empirical complementarity discovery, real-world generalization, metaphysical perspectivism, superiority to arbitrary-horizon Bayesian experimental design, or a probe-count advantage over generic two-step lookahead.

## Next decisive gate

Do **not** add more synthetic varieties simply to inflate coverage. The next useful test is a real historical software/agent regression in which candidate test orientations have measurable redundancy and complementarity. Compare conventional adaptive test selection against the same selector augmented with discovered orientation equivalence and synergy. The practical target is whether the orientation-aware structure reduces executions or planning work required to expose the regression while preserving calibrated abstention.
