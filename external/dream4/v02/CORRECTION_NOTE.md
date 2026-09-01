# DREAM4 Harness v0.2 — preregistration alignment correction

The original `v01` harness is preserved unchanged in `../v01/`. During repository consolidation, three implementation mismatches were identified between the frozen runner and `PREREGISTRATION.md`:

1. **Bootstrap unit.** The preregistration requires resampling networks first and modalities within network. v0.1 independently resampled the ten KO/KD effects. v0.2 implements the stated hierarchical bootstrap.
2. **Permutation seed.** The preregistration specifies `20260831 + 1000*network_id + repeat`. v0.1 additionally added a size-dependent term. v0.2 uses the registered formula exactly.
3. **Normalized-AUPRC pass criterion.** The preregistration requires AUPRC/prevalence > 1 on at least 3 of 5 networks for at least one modality. v0.1 counted qualifying KO/KD comparisons across modalities. v0.2 evaluates KO and KD network counts separately and passes this criterion only if either modality reaches 3/5.

No DREAM4 confirmatory result is claimed by this correction. The purpose of v0.2 is to make the executable gate match the written preregistration before the official Size100 run.
