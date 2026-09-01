# v0.6 Preregistration — Complementary Orientation Gate

## Question

Can explicit orientation structure identify a cheapest decision-complete perspective set, including pure complementarity, without falsely forcing a decision when the available orientations are insufficient?

## Claim boundary

This gate is an exact candidate-model benchmark. It does not establish noisy empirical complementarity discovery, physical perspectivism, or general superiority to active learning. The hidden true mechanism is used only to generate observations and score the final decision. Selection operates on candidate response geometry and accumulated evidence.

## Frozen conditions

1. single-view sufficiency;
2. exact redundancy after transport/equivalence;
3. pure pairwise complementarity (XOR: each view has zero one-step decision information, the pair is sufficient);
4. misleading marginal similarity with relationally different partitions;
5. fundamental insufficiency, requiring `UNKNOWN`;
6. higher-order complementarity where no pair suffices but three views do.

Decision completeness is exact: for survivor set M_S, all surviving mechanisms must imply the same task decision. If no available orientation set reaches that state, the correct output is `UNKNOWN`.

## Policies

- fixed orientation order;
- random orientation order;
- exhaustive all-view evaluation;
- greedy mechanism-information feature selection;
- one-step cost-aware active decision learning;
- generic two-step decision lookahead (strong anti-strawman baseline);
- OARL: exact redundancy quotient plus explicit positive pair-synergy edges.

## Primary safety gates

- zero false declarations of decision completeness in exact cases;
- correct `UNKNOWN` on every fundamental-insufficiency case;
- pure XOR complementarity recovered in two probes;
- higher-order case is not declared complete after only two views;
- OARL never has lower decision accuracy than generic two-step lookahead.

## Utility gates

- at matched decision correctness/abstention, OARL uses at least 25% fewer probes than exhaustive on the resolvable controlled cases;
- exact redundancy reduces OARL planning evaluations relative to unquotiented two-step lookahead;
- compare OARL directly with one-step active decision learning and generic two-step lookahead. If generic two-step matches OARL in probe efficiency, do not claim an independent probe-count advantage from orientation awareness; retain only any verified structural/planning advantage.

## Kill conditions

Any false sufficiency declaration, any incorrect non-UNKNOWN result in the insufficiency condition, failure on the XOR complementarity condition, or lower decision accuracy than generic two-step lookahead kills the adaptive orientation claim for this gate.
