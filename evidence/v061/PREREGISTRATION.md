# v0.6.1 pyGSTi Gauge-Equivalence Gate — Preregistration

Status: **PROSPECTIVE / NO v0.6.1 RESULT YET**

## Why this replaces CSuite as the primary equivalence gate

The v0.6 CSuite pilot was successful as an adapter run but failed a more basic suitability test: published CSuite v0.1 systems expose only one or two interventional environments in the tested systems, yielding zero or one pair challenge per system. That is insufficient for a serious equivalence-discovery safety gate.

v0.6.1 therefore moves to a domain in which nontrivial observational equivalence is independently defined: **gate-set tomography (GST)**.

In GST, gauge transformations alter the internal representation of states, measurements and gate matrices while leaving every observable circuit-outcome probability invariant. This is an established domain fact and is implemented independently by pyGSTi. OARL does not define the equivalence relation.

## Scientific question

> Can a benchmark-neutral OARL certification layer identify that substantially different representations belong to the same observational equivalence class, while refusing to merge physically distinct models, without being given the domain-specific gauge transformation that generated the pair?

A second question is deliberately competitive:

> Does OARL add anything beyond simpler comparison of observable circuit predictions and pyGSTi's domain-specific gauge machinery?

A negative answer to the second question narrows the utility claim even if the first question passes.

## External dependency

- package: `pygsti`
- frozen pilot version: `0.10.2`
- upstream: `sandialabs/pyGSTi`
- model pack: `smq1Q_XYI`

pyGSTi is treated as the external domain implementation. Its gauge transformation machinery is evaluator/oracle information and is not supplied to the benchmark-neutral OARL comparator.

## Ground truth

### Equivalent pairs

Start from an independently implemented pyGSTi one-qubit model and apply an invertible `FullGaugeGroupElement` to the complete gate set. The resulting model is labelled **equivalent** because pyGSTi/GST gauge theory guarantees unchanged observable circuit probabilities.

### Distinct pairs

Create physically distinct controls by modifying the data-generating gate set outside a pure gauge transformation, beginning with nonzero operation depolarization. A pair is retained as a distinct control only when a sealed evaluator circuit set confirms a nonzero observable probability difference above numerical tolerance.

The evaluator never labels a pair distinct merely because its raw parameter vector differs.

## Pilot circuit split

The pilot uses deterministic circuits over the `Gxpi2` and `Gypi2` operations.

- discovery circuits: sequences of length 0 through 3;
- sealed evaluator circuits: sequences of length 4 through 6.

The exact circuit construction and ordering are frozen in the runner before pilot results are interpreted.

## Competitors

1. raw parameter-vector distance — intentionally gauge-naive negative baseline;
2. exact observable-probability comparison;
3. generic probability-space similarity threshold;
4. pyGSTi gauge-aware oracle/domain baseline;
5. OARL precision-first `EQUIVALENT / DISTINCT / UNKNOWN` certification using only discovery-circuit evidence.

The pyGSTi oracle is not a learnable competitor. The important competitive comparison is OARL versus generic observable-probability comparison.

## Pilot purpose

The first executable smoke gate establishes only that:

1. the external pyGSTi dependency and pinned API work in CI;
2. gauge transformation materially changes internal representation;
3. gauge transformation preserves discovery and sealed circuit probabilities;
4. a physical perturbation changes sealed circuit probabilities;
5. the benchmark can produce many equivalent and distinct pair challenges without inventing an OARL-specific truth definition.

This smoke gate is **not** evidence of distinctive OARL utility.

## Confirmatory safety endpoints

Before a later confirmatory run, freeze finite-shot sampling, OARL thresholds and generic-baseline thresholds on pilot-only instances.

Primary endpoint:

- false-merge rate on physically distinct pairs.

Secondary endpoints:

- equivalence precision;
- equivalence recall;
- abstention rate;
- sealed-circuit probability preservation;
- quotient compression;
- acquisition/circuit-evaluation reduction;
- total certification + search cost.

## Incremental-utility criterion

OARL only earns a distinctive-method claim if, at matched false-merge risk, it improves at least one useful frontier over generic probability-space comparison without degrading sealed-circuit predictions.

If direct probability comparison matches or dominates OARL, the correct conclusion is:

> OARL recovers a known quotient structure, but this benchmark does not demonstrate incremental utility beyond simpler observable-space equivalence testing.

## Kill / narrowing criteria

Narrow or reject the strong utility claim if:

- any accepted OARL merge crosses a pyGSTi-verified observable distinction;
- OARL requires access to the hidden gauge matrix;
- generic probability comparison matches or dominates OARL on safety, recall and cost;
- OARL's abstention eliminates useful compression;
- certification cost erases all acquisition savings;
- results depend on gauge-specific code embedded in the OARL method rather than benchmark-neutral evidence.

## Claim boundary

A successful v0.6.1 gate would show transfer to an independently established equivalence structure in quantum characterization. It would **not** establish a new result in quantum tomography, because gauge freedom and gauge optimization are already standard in GST and pyGSTi.

The potentially novel result would be cross-domain generality of a benchmark-neutral certification/quotient architecture, not discovery of gauge freedom itself.
