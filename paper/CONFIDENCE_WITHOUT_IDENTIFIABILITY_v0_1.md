# Confidence Without Identifiability

## Repetition, Boundary-Relative Information, and Safe Experimental Equivalence

**Working manuscript v0.1 — September 2026**

### Abstract

More observations usually increase statistical confidence, but they do not necessarily increase what an experiment can distinguish. This paper separates **sampling uncertainty** from **boundary uncertainty**: uncertainty caused by the choice of observation or intervention operator itself. We formalize boundary-relative observational equivalence, show that exact equivalence under a fixed boundary is preserved under arbitrary IID repetition, and restate the corresponding local result that repeated sampling scales Fisher information without changing its rank or null space. Thus information magnitude can increase while informational span does not. We connect this distinction to identifiability, observability and optimal experimental design, and use a sequence of falsification-oriented computational studies to examine its consequences for safe equivalence quotienting. In an external pyGSTi gate-set-tomography benchmark, a preregistered shallow-boundary equivalence certifier reduced false merges relative to a direct probability comparator but failed its own zero-false-merge requirement. On a critical perturbation class, increasing shallow-boundary shot count made the unsafe equivalence conclusion more frequent even though sampling noise decreased. The result motivates a shift from confidence-only certification toward **boundary information audits** that ask whether new measurements add genuinely new distinguishing directions. We explicitly test this next step against classical D- and E-optimal design, sensitivity-rank selection and simple directional-diversity baselines. The proposed contribution is therefore not the classical fact that Fisher-information rank governs local identifiability, nor a new theorem in gate-set tomography, but a risk-oriented framework for distinguishing repeated evidence from expansion of observational support before experimental equivalence is quotiented.

---

## 1. Introduction

A common intuition in inference is that more data should eventually settle a question. This is correct only when the data-generating experiment is capable of exposing the distinction of interest. Repeating a measurement can reduce variance around what that measurement sees. It cannot, by repetition alone, reveal a direction to which the measurement is insensitive.

This distinction matters whenever a latent system can be interrogated through multiple observation, intervention or input/output boundaries. Two mechanisms may be indistinguishable through one boundary and distinguishable through another. If evidence is accumulated only through the first boundary, confidence can become arbitrarily high while the relevant mechanism distinction remains inaccessible.

We call this **confidence without identifiability**.

The central distinction is:

\[
\text{sampling uncertainty}
\;\neq\;
\text{mechanism uncertainty}
\;\neq\;
\text{boundary uncertainty}.
\]

Sampling uncertainty concerns finite evidence under a fixed experiment. Mechanism uncertainty concerns which latent alternative generated the observations. Boundary uncertainty concerns whether the chosen experimental map preserves the mechanism distinctions required for the inferential task.

This paper develops that distinction within the Orientation-Aware Relational Learning (OARL) research programme. Earlier versions of OARL investigated whether experimental orientations could expose hidden distinctions and whether redundant orientations could be quotiented to reduce inference cost. Several early method claims failed under preregistered tests, including the original stability/cost acquisition penalty. Later synthetic work showed that exact structural quotienting can preserve Bayesian inference when equivalence structure is correct, while false merges can be substantially more dangerous than conservative false splits. A precision-first finite-noise certifier subsequently passed a held-out synthetic gate but did not generalize safely to an external finite-shot pyGSTi boundary-extrapolation task.

That external failure motivates the present reformulation.

The question is no longer only:

> Are two experimental views equivalent given the evidence observed so far?

It is also:

> Has the evidence covered the directions in which the candidate mechanisms could differ?

---

## 2. Observation boundaries

Let \(M_\theta\) denote a mechanism indexed by parameter or model label \(\theta\). Let an observational boundary \(b\) specify the experiment, intervention, projection, sensor, circuit family, input/output orientation or other map through which the mechanism is interrogated.

The mechanism and boundary jointly induce an observable distribution

\[
P_b(y\mid\theta).
\]

The boundary is part of the inferential problem rather than a neutral window onto the mechanism.

### Definition 1 — Boundary-relative observational equivalence

Two mechanisms \(\theta_i\) and \(\theta_j\) are observationally equivalent under boundary \(b\), written

\[
\theta_i \sim_b \theta_j,
\]

when

\[
P_b(\cdot\mid\theta_i)=P_b(\cdot\mid\theta_j).
\]

This is explicitly boundary-relative. It is possible that

\[
\theta_i \sim_{b_1} \theta_j
\]

while

\[
\theta_i \not\sim_{b_2} \theta_j.
\]

For a family of admissible boundaries \(\mathcal B\), define family-level equivalence by

\[
\theta_i \sim_{\mathcal B} \theta_j
\quad\Longleftrightarrow\quad
\forall b\in\mathcal B:\;\theta_i\sim_b\theta_j.
\]

Equivalence under one boundary therefore does not imply equivalence under a larger boundary family.

---

## 3. Repetition cannot break exact fixed-boundary equivalence

### Proposition 1 — IID repetition invariance

If

\[
\theta_i\sim_b\theta_j,
\]

then for any positive integer \(n\), \(n\) IID observations through the same boundary remain observationally equivalent:

\[
P_b(y_{1:n}\mid\theta_i)
=
P_b(y_{1:n}\mid\theta_j).
\]

### Proof

By IID factorization,

\[
P_b(y_{1:n}\mid\theta)
=
\prod_{k=1}^{n}P_b(y_k\mid\theta).
\]

Boundary-relative equivalence gives

\[
P_b(y_k\mid\theta_i)=P_b(y_k\mid\theta_j)
\]

for every possible observation \(y_k\). Multiplying equal factors preserves equality. Therefore the joint distributions are identical for every \(n\). \(\square\)

### Consequence

No amount of IID repetition can distinguish mechanisms that are exactly observationally equivalent through the repeated boundary.

This statement is stronger than saying that redundant samples are correlated. The samples may be statistically independent conditional on the mechanism and still fail to add a new *distinguishing direction*. Independence of draws is not the same as diversity of observational operators.

---

## 4. Local information magnitude versus information span

For differentiable parametric models, let the per-observation Fisher information under boundary \(b\) be

\[
\mathcal I_b(\theta).
\]

Under the standard regularity conditions for IID observations, \(n\) repetitions give

\[
\mathcal I_{b,n}(\theta)=n\mathcal I_b(\theta).
\]

### Proposition 2 — Fixed-boundary rank invariance

For any \(n>0\),

\[
\operatorname{rank}(\mathcal I_{b,n})
=
\operatorname{rank}(\mathcal I_b),
\]

and

\[
\operatorname{null}(\mathcal I_{b,n})
=
\operatorname{null}(\mathcal I_b).
\]

### Proof

Multiplication of a matrix by a nonzero scalar does not change its rank or null space. \(\square\)

Thus repetition can increase eigenvalue magnitudes and reduce estimator variance in already visible directions while leaving zero-information directions zero.

If \(v\) is a locally invisible mechanism direction,

\[
v^\top \mathcal I_b v=0,
\]

then

\[
v^\top \mathcal I_{b,n}v
=n\,v^\top\mathcal I_bv
=0.
\]

This motivates a distinction between:

- **information magnitude** — how much evidence lies along already observed directions; and
- **information span** — which mechanism directions are represented at all.

The rank connection itself is classical identifiability theory. Rothenberg established under regularity conditions a local equivalence between identifiability and nonsingularity of the information matrix. Sensitivity-matrix and observability methods likewise use rank and null-space structure to diagnose unidentified parameter combinations. We do not claim these results as novel.

---

## 5. Boundary expansion can increase span

Suppose evidence is collected through boundaries \(b_1,\ldots,b_m\). Under conditional independence across experiments, their local Fisher contributions add:

\[
\mathcal I_{\mathrm{total}}
=
\sum_{k=1}^{m}n_k\mathcal I_{b_k}.
\]

Unlike scalar repetition of one matrix, adding a distinct boundary can change the information span:

\[
\operatorname{rank}(\mathcal I_{b_1}+\mathcal I_{b_2})
>
\operatorname{rank}(\mathcal I_{b_1})
\]

when \(b_2\) contributes sensitivity outside the span already covered by \(b_1\).

This is the formal version of the statement:

> More evidence is not necessarily more perspective.

A second measurement is valuable not merely because it is another datum, but potentially because its observation operator intersects the latent mechanism space differently.

---

## 6. Relation to cosine-style redundancy

Let \(s_b\) denote a variance-normalized local sensitivity vector supplied by a candidate probe. If two probes have nearly parallel sensitivities,

\[
\frac{|s_{b_1}^\top s_{b_2}|}
{\|s_{b_1}\|\,\|s_{b_2}\|}
\approx 1,
\]

then they add information in nearly the same local direction. Repeating or adding such probes may substantially increase Fisher eigenvalues along that direction while adding little or no span.

Cosine diversity is therefore a useful intuitive and computational baseline, but it is not sufficient as a general identifiability criterion. The relevant geometry can be nonlinear, parameter-dependent and likelihood-weighted; classical optimal-design criteria already use the full information matrix rather than pairwise cosine similarity alone.

---

## 7. Classical optimal experimental design is a mandatory baseline

The preceding formalism overlaps directly with established optimal experimental design.

D-optimal design seeks experiments that maximize a determinant criterion on the information matrix, shrinking the volume of the local confidence ellipsoid. E-optimal design targets the smallest eigenvalue. Rank- and sensitivity-based methods explicitly seek measurements that fill information null spaces or improve practical identifiability.

Therefore the following claim would be invalid:

> OARL is novel because it selects measurements that increase Fisher-information rank.

That idea already exists.

The OARL-specific burden is narrower: whether an explicit **boundary-relative equivalence / abstention / safe-quotienting layer** adds value beyond ordinary optimal design, particularly when the system must decide which apparent experimental distinctions can be safely removed before expensive inference.

---

## 8. Evidence trajectory

### 8.1 Synthetic boundary dependence

Early OARL experiments showed controlled examples in which a fixed input/output orientation hid a mechanism distinction that another admissible orientation exposed. The originally proposed stability/cost acquisition penalty did not survive confirmation and is not retained as a supported contribution.

### 8.2 Exact structural quotienting

Later benchmarks showed that when exact orientation equivalence is known correctly, quotienting can remove redundant acquisition-score evaluations while preserving paired Bayesian inference outcomes. Stress tests showed an important asymmetry: conservative false splits mainly lose efficiency, while false merges can corrupt inference.

### 8.3 Finite-noise synthetic certification

A preregistered precision-first certifier recovered a useful subset of exact affine/permutation equivalences from finite noisy predictive evidence with zero observed false equivalences across 72,600 held-out distinct-pair challenges, at the cost of substantial abstention and incomplete recall. This established a synthetic proof of concept, not external generality.

### 8.4 External pyGSTi gauge smoke test

Gate-set tomography provides an independently established equivalence structure: gauge transformations can substantially alter internal gate-set representations while preserving all observable circuit probabilities. A pyGSTi smoke test confirmed that the benchmark apparatus reproduces this property. This is an external domain fact, not an OARL discovery.

### 8.5 v0.6.1 finite-shot external failure

The first preregistered finite-shot external gate compared a direct shallow probability-equivalence test with an OARL cross-fit plus depth-stability certificate. Across 9,600 classifications per method:

- generic shallow probability equivalence: precision 0.7497, recall 0.9908, 1,191 operational false merges;
- OARL cross-fit + depth stability: precision 0.8355, recall 0.7364, 522 operational false merges.

OARL improved the descriptive precision/safety tradeoff but failed the preregistered primary criterion of zero sealed-boundary false merges.

The critical perturbation class had operation noise 0.010. Its deeper sealed circuits reached a maximum probability difference of 0.02926, exceeding the frozen operational equivalence tolerance of 0.020. OARL false merges on this class changed with shot count as follows:

| shots | false merges / 300 |
|---:|---:|
| 50,000 | 0 |
| 100,000 | 58 |
| 250,000 | 182 |
| 500,000 | 282 |

The interpretation is not that more samples intrinsically worsen inference. More shallow samples reduced sampling uncertainty. They made the classifier increasingly willing to certify the equivalence supported by the shallow boundary, while the deeper boundary contained a distinction outside the certification claim.

This is a concrete example of sampling confidence outpacing boundary adequacy.

---

## 9. v0.6.2: Boundary Information Audit

The next experiment asks whether the distinction between repetition and boundary expansion can be measured directly in an external executable system.

Using pyGSTi, we define a local mechanism coordinate system from three small coherent perturbation directions and compute variance-normalized circuit sensitivity vectors. The initial boundary contains all depth-1 circuits. Candidate probes range from depths 2 through 6.

The audit tests:

1. whether multiplying the fixed depth-1 information matrix by increasing repetition factors preserves rank and null space;
2. whether a new circuit contributes information in the initial null space;
3. whether the expanded boundary reaches full local rank;
4. how quickly competing selection policies fill the missing information span.

The competing policies are:

- repeat-only;
- random new views;
- cosine-direction diversity;
- greedy D-optimality;
- greedy E-optimality;
- null-space coverage.

The null-space policy is OARL-motivated but not assumed novel. If classical D- or E-optimality reaches the same identifiable span at equal or lower cost, that is a negative result for an OARL-specific selection claim.

**v0.6.2 result: pending.**

---

## 10. What OARL can still contribute if optimal design wins

Even if classical optimal design dominates measurement selection, a separate problem remains: **safe structural quotienting**.

Optimal design usually asks which experiment should be performed to estimate parameters or discriminate models efficiently. OARL's strongest surviving architecture asks an upstream structural question:

> Which candidate experimental distinctions are genuinely different for the mechanism-discrimination task, which are safely transport-equivalent, and which are uncertain enough that they must remain separate?

The architecture is:

```text
candidate experimental views
        ↓
boundary information / equivalence audit
        ↓
equivalent | distinct | unknown
        ↓
risk-bounded quotient
        ↓
standard optimal experimental design / inference
```

This formulation makes OARL complementary to, rather than a replacement for, classical design if the structural layer can be shown to add safety or computational value.

---

## 11. Falsifiable claims

The project should now be judged by the following claims separately.

### C1. Boundary-relative equivalence exists in relevant systems

Supported in controlled, historical and external executable examples, but broad scope remains open.

### C2. Repetition alone can repair every apparent equivalence

False in exact boundary equivalence by Proposition 1, and empirically unsupported in the v0.6.1 operational boundary case.

### C3. OARL has a superior rank-aware measurement-selection algorithm

Not established. v0.6.2 must compare directly with D/E-optimality, sensitivity-rank methods and diversity baselines.

### C4. OARL can safely quotient experimental redundancy before ordinary inference

Supported conditionally in exact and synthetic finite-noise constructions. External safe generalization remains unresolved.

### C5. Structural certification plus quotienting is cheaper end-to-end than exhaustive design

Not yet established externally.

---

## 12. Discussion

The central methodological warning is simple:

> Confidence is conditional on an observation operator.

A large sample can establish with high precision what a given boundary implies. It cannot by itself establish that the boundary contains every distinction relevant to the scientific question.

This has consequences beyond the current benchmark. Machine-learning systems can aggregate many examples generated by a shared upstream representation. Agent evaluators can run thousands of scenarios that differ superficially but exercise the same failure direction. Scientific pipelines can repeatedly measure a convenient observable while leaving a structurally unidentified parameter combination untouched. Social evidence can be numerically abundant yet descend from a common upstream source.

In each case the nominal evidence count may grow much faster than the span of independent distinguishing information.

The appropriate response is not to discount repetition indiscriminately. Repetition is essential for reducing sampling noise. The response is to account separately for **how much evidence has been collected** and **which mechanism directions the evidence can interrogate**.

---

## 13. Limitations

1. Fisher rank is a local criterion and can fail to capture global nonlinear identifiability.
2. Numerical rank depends on tolerances and parameterization.
3. The current external demonstration is confined to one pyGSTi model family.
4. Circuit depth is only one example of a changing observational boundary.
5. Operational epsilon-equivalence is task-dependent and should not be confused with physical identity.
6. The current OARL external certifier failed its zero-false-merge gate.
7. The project has not yet demonstrated end-to-end economic advantage over established optimal experimental design.

---

## 14. Research programme

The immediate sequence is:

1. **v0.6.2 Boundary Information Audit** — measure fixed-boundary rank invariance and new-boundary span; compete against classical design baselines.
2. **v0.6.3 Active Boundary Selection** — on fresh held-out systems, decide between additional repetitions and new boundaries under explicit cost.
3. **External replication** — repeat the boundary-relative failure and recovery in a non-quantum dynamical or causal system.
4. **Safe quotient economics** — test whether certification plus quotienting lowers total experimental/search cost without increasing false high-confidence conclusions.
5. **Independent reproduction** — freeze a compact benchmark suite and invite replication.

---

## References / positioning sources

- Rothenberg, T. J. (1971). *Identification in Parametric Models*. Econometrica, 39(3), 577–591.
- Atkinson, A. C., Donev, A. N., & Tobias, R. D. (2007). *Optimum Experimental Designs, with SAS*. Oxford University Press. DOI: 10.1093/oso/9780199296590.001.0001.
- Eisenberg, M. C., & Hayashi, M. A. (2014). Determining identifiable parameter combinations using subset profiling. *Mathematical Biosciences*.
- Chis, O.-T., Banga, J. R., & Balsa-Canto, E. (2011). Structural identifiability of systems biology models: a critical comparison of methods. *PLoS ONE*.
- pyGSTi documentation and Sandia National Laboratories pyGSTi project: gauge freedom, model construction and gate-set tomography.

The final manuscript will require a systematic literature review before novelty claims are fixed.
