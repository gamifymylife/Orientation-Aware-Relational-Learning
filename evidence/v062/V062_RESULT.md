# v0.6.2 Boundary Information Audit — Result

Status: **STRUCTURAL GATE PASSED; NO OARL-SPECIFIC SELECTION ADVANTAGE ESTABLISHED**

External dependency: `pygsti==0.10.2`, model pack `smq1Q_XYI`.

GitHub Actions run: `33508205671`
Artifact: `v062-boundary-information-audit`, artifact ID `9800489097`
Artifact SHA-256: `c69db391b0f68155226f08a1e4b7e118ca4005cfd8d21d57a7f2afeb10bf9d11`

## Primary structural result

The initial depth-1 boundary contains two circuits, `Gxpi2` and `Gypi2`, evaluated against three local coherent-rotation mechanism directions (X, Y, Z).

Its Fisher eigenvalues are approximately:

`[0, 0.999999997, 0.999999997]`

so:

- rank = **2**;
- nullity = **1**.

Repeating exactly the same boundary scales the two nonzero eigenvalues but leaves the zero direction zero:

| repetition factor | eigenvalues (approx.) | rank | nullity |
|---:|---|---:|---:|
| 1 | `[0, 1, 1]` | 2 | 1 |
| 10 | `[0, 10, 10]` | 2 | 1 |
| 100 | `[0, 100, 100]` | 2 | 1 |
| 1000 | `[0, 1000, 1000]` | 2 | 1 |

Therefore 1000x evidence inside the same boundary increases information magnitude by 1000x in the already visible directions while adding **zero new local information span**.

This is the executable version of the `100 A's != a new informational direction` intuition.

## Boundary expansion

The expanded circuit family (depths 1 through 6; 126 probes) reaches full local rank 3, with Fisher eigenvalues:

`[32.4278, 167.5722, 333.99998]`.

At least one circuit outside the initial boundary has nonzero sensitivity projected into the initial Fisher null space. All four preregistered structural checks passed:

- repeat rank invariant: PASS;
- repeat nullity invariant: PASS;
- new boundary has null-space information: PASS;
- full rank reachable with expanded boundary: PASS.

## Selection-policy comparison

All non-repeat policies found a single new circuit that completed rank 3.

| policy | new circuit | depth cost | final rank | positive-spectrum condition |
|---|---|---:|---:|---:|
| D-optimal | `Gxpi2.Gypi2` | **2** | 3 | 6.8541 |
| null-space coverage | `Gxpi2.Gypi2` | **2** | 3 | 6.8541 |
| E-optimal | `Gxpi2.Gypi2.Gypi2` | 3 | 3 | ~1.0000 |
| cosine diversity | `Gxpi2.Gypi2.Gypi2` | 3 | 3 | ~1.0000 |
| random-new-view | depth-6 circuit | 6 | 3 | 358.9972 |
| repeat-only x1000 | none | 1998 added depth cost | **2** | 1.0 over positive subspace |

The OARL-motivated null-space criterion **tied D-optimality on minimum added depth cost**. It did not beat it.

## Scientific interpretation

### Supported

This audit gives an unusually clean executable demonstration of the difference between evidence quantity and observational span:

> Repetition can make already-visible mechanism directions arbitrarily precise while leaving an invisible mechanism direction completely unidentified; a single differently oriented probe can expose the missing direction.

### Not novel to OARL

The fixed-boundary Fisher-rank result and rank-aware measurement selection are classical identifiability / optimal-design ideas. The D-optimal baseline achieved the same minimal added cost as the OARL-motivated null-space selector.

Therefore v0.6.2 **does not establish a superior OARL measurement-selection algorithm**.

### What remains potentially OARL-specific

The surviving novelty burden moves upstream of ordinary optimal design:

1. discover which experimental views are structurally redundant or transport-equivalent;
2. distinguish `EQUIVALENT / DISTINCT / UNKNOWN` with asymmetric false-merge risk;
3. audit whether apparent confidence is confined to an insufficient boundary;
4. quotient only certified redundancy;
5. hand the reduced, safer space to established OED / D-optimal / other inference machinery.

## Next gate

v0.6.3 should be a fresh held-out **active boundary-vs-repetition decision** with finite cost and noise. The comparator set must include at least D-optimality, E-optimality and a generic null-space/rank design method. OARL only earns an incremental-utility claim if its boundary-equivalence/abstention layer improves safety or total cost beyond those methods, not merely if it rediscovers their information geometry.
