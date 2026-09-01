# Working papers

`Orientation-Aware Relational Learning.pdf` is the August 2026 paper that initiated the experimental programme. It is now historical: its proposed stability-aware acquisition term was falsified by v0.2, and it predates the later quotienting, certification and external-boundary results.

The current manuscript direction is:

- [`CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md`](CONFIDENCE_WITHOUT_IDENTIFIABILITY_v0_1.md) — **Confidence Without Identifiability: Repetition, Boundary-Relative Information, and Safe Experimental Equivalence**.

That manuscript formalizes the distinction between sampling uncertainty and boundary uncertainty, including the fixed-boundary IID repetition and Fisher-rank results. It is intentionally positioned against classical identifiability and optimal experimental design rather than claiming those results as OARL inventions.

The first executable Boundary Information Audit is recorded in [`../evidence/v062/V062_RESULT.md`](../evidence/v062/V062_RESULT.md). Its main result is that 1000x repetition of the same rank-2 boundary leaves rank at 2, while one new depth-2 circuit reaches full local rank 3. The OARL-motivated null-space selector ties D-optimality on minimum added circuit-depth cost, so **v0.6.2 does not establish an OARL-specific measurement-selection advantage**.

Treat [`../docs/CLAIMS_AND_EVIDENCE.md`](../docs/CLAIMS_AND_EVIDENCE.md) as the authoritative claim boundary for the repository.
