# Boundary / Experiment Literature Positioning

Status: working novelty boundary after v0.6.2.

## The important correction

The statement “more samples are not necessarily more perspective” is useful, but its mathematical core is not new. Several mature literatures already cover major parts of it.

OARL must therefore separate:

1. **established theory used by the project**;
2. **empirical phenomena reproduced by the project**;
3. **the remaining algorithmic novelty burden**.

## 1. Identifiability and Fisher information

Classical identifiability theory relates local identifiability to nonsingularity / rank of the Fisher information matrix under regularity conditions. Sensitivity and observability methods use rank and null spaces to identify parameter combinations that an experiment cannot distinguish.

For IID repetitions of a fixed experiment,

`I_n(theta) = n I_1(theta)`.

Therefore nonzero eigenvalues can grow while rank and null space remain unchanged.

This is an established result and must not be claimed as OARL novelty.

Key reference:

- Rothenberg, T. J. (1971), *Identification in Parametric Models*, Econometrica 39(3), 577–591.

## 2. Optimal experimental design

D-, A-, E- and related optimality criteria already choose experiments using the Fisher information matrix. D-optimality maximizes a determinant / confidence-volume criterion. E-optimality targets the weakest information eigen-direction. Rank- and null-space-oriented experimental-design methods explicitly seek measurements that make previously unidentified parameter combinations identifiable.

v0.6.2 confirms this is not a theoretical footnote: greedy D-optimality tied the OARL-motivated null-space selector at the minimum added depth cost.

Key reference:

- Atkinson, A. C., Donev, A. N., & Tobias, R. D. (2007), *Optimum Experimental Designs, with SAS*, Oxford University Press.

## 3. Blackwell comparison of experiments

Blackwell's comparison of statistical experiments asks whether one experiment is at least as informative as another for decision making. A more informative experiment can simulate a less informative one through an appropriate stochastic transformation / garbling. Blackwell equivalence therefore already provides a rigorous notion of experiments carrying the same decision-relevant information.

This directly overlaps any broad claim that OARL invented “equivalence between experiments” or “which perspective is more informative.”

Key reference:

- Blackwell, D. (1953), *Equivalent Comparisons of Experiments*, Annals of Mathematical Statistics 24(2), 265–272.

## 4. Le Cam deficiency and comparison of experiments

Le Cam theory generalizes comparison from exact domination/equivalence to approximate comparison. Deficiency quantifies how much is lost when using one statistical experiment instead of another, with interpretations in terms of decision risk and randomization. Torgersen's monograph explicitly treats comparison, equivalence, representations, deficiency, and accumulation of information under repeated experiments.

This is extremely close to OARL's approximate-equivalence ambition.

Key references:

- Le Cam, L. (1964), *Sufficiency and Approximate Sufficiency*.
- Torgersen, E. (1991), *Comparison of Statistical Experiments*, Cambridge University Press.

## 5. What OARL therefore cannot claim

Do **not** claim novelty for any of the following in isolation:

- experiments can differ in informativeness;
- two experiments can be statistically equivalent;
- repeated observations increase information quantity;
- fixed-design repetition cannot repair structural non-identifiability;
- Fisher-information rank diagnoses local identifiability;
- selecting new measurements can increase information rank;
- D/E-optimal design can prefer complementary measurements;
- approximate equivalence/comparison of statistical experiments is a new concept.

## 6. The remaining plausible OARL contribution

The potentially distinctive layer is more operational and algorithmic:

> Given a large candidate experimental/action space whose equivalence structure and admissible transports are not supplied, can a benchmark-neutral system infer from finite evidence which experiments are safely interchangeable for a specified mechanism-discrimination task, explicitly abstain when that conclusion is unsupported, quotient only certified redundancy, and thereby improve safety or total search cost when handed to an ordinary optimal-design algorithm?

This differs from simply *defining* experiment equivalence.

The key burdens are:

### A. Structure discovery rather than known comparison

Blackwell/Le Cam theory generally starts with statistical experiments whose distribution families are mathematically specified. OARL aims to discover useful equivalence/transport structure from finite predictive or empirical evidence when the grouping itself is not supplied.

### B. Task-conditioned mechanism discrimination

OARL's practical equivalence can be restricted to preserving distinctions among a candidate mechanism family and a specified intervention/output task, rather than demanding universal equivalence for every decision problem.

This may make OARL weaker than Blackwell equivalence mathematically but more computationally usable for a specific active-learning/search problem.

### C. Three-way certification

OARL treats `EQUIVALENT`, `DISTINCT`, and `UNKNOWN` as materially different outputs. `UNKNOWN` is not merely an estimator state: it blocks quotienting. This gives a direct operational role to uncertainty about the equivalence relation itself.

### D. Asymmetric structural risk

A missed equivalence usually costs computation; a false equivalence can remove a mechanism-distinguishing experiment and corrupt downstream inference. OARL explicitly optimizes around that asymmetry.

### E. Quotient as a preprocessing/compiler layer

The intended architecture is:

```text
large candidate experiment space
        ↓
learn / certify experiment relations
        ↓
equivalent | distinct | unknown
        ↓
risk-bounded quotient
        ↓
standard OED / Bayesian design / active learning
```

The contribution, if demonstrated, is therefore an upstream **experimental-search compiler**, not a replacement theory of statistical experiments.

## 7. What v0.6.2 established

v0.6.2 is conceptually clean but not a novelty result:

- depth-1 pyGSTi boundary: Fisher rank 2 of 3;
- 1000x repetition: eigenvalue magnitude scaled, rank remained 2;
- one depth-2 circuit raised rank to 3;
- null-space selection and D-optimality both reached full rank at added depth cost 2.

This gives a compact executable teaching/example case for information magnitude vs information span, while simultaneously showing why classical optimal design must be treated as a strong baseline.

## 8. v0.6.3 must now be harder

The next benchmark should not ask whether OARL can find a new information direction. D-optimality can.

It should ask whether the **structural certification layer** adds value before ordinary design.

Candidate benchmark:

1. construct a large candidate probe set with many transformation-related redundancies plus a smaller number of genuinely distinction-changing probes;
2. hide the grouping/transforms from all learned methods;
3. provide finite noisy evidence;
4. compare:
   - exhaustive D-optimal / Bayesian design;
   - generic canonicalization/similarity compression + D-optimal design;
   - approximate Blackwell/Le Cam-inspired experiment comparison where tractable;
   - behavioral/bisimulation-style equivalence;
   - OARL `EQUIVALENT/DISTINCT/UNKNOWN` certification + quotient + the same D-optimal downstream selector;
5. score total cost including certification, false merges, mechanism correctness and experiment count.

The downstream optimizer must be held constant when testing the quotient layer. Otherwise a win cannot be attributed to OARL's structural contribution.

## 9. Strongest defensible paper thesis after this review

A safer thesis is:

> Statistical confidence is conditional on an experimental boundary. Classical theory already characterizes identifiability and comparison of known experiments; the unresolved computational problem addressed here is whether the equivalence structure of a large experimental search space can itself be learned conservatively from finite evidence and used to compress active inference without deleting distinctions that matter.

That is narrower than the original framing, but scientifically much stronger.
