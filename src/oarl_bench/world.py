from dataclasses import dataclass
import numpy as np
from .config import BenchmarkConfig

@dataclass
class RelationalWorld:
    # Learner likelihood model.
    means: np.ndarray
    # Observation-generating semantics; differs on truly invalid orientations.
    actual_means: np.ndarray
    nominal_sigma: np.ndarray
    stability: np.ndarray
    cost: np.ndarray
    exposure: np.ndarray
    true_h: int
    perturbation_scale: float
    seed: int
    regime: str

    # Declared / classifier-produced structural metadata used by OARL.
    orientation_class: np.ndarray
    class_representative: np.ndarray
    to_canonical_intervention: np.ndarray
    transform_scale: np.ndarray
    transform_offset: np.ndarray
    admissible: np.ndarray

    # Ground-truth structure retained only for evaluation in v0.4.
    true_orientation_class: np.ndarray
    true_class_representative: np.ndarray
    true_to_canonical_intervention: np.ndarray
    true_transform_scale: np.ndarray
    true_transform_offset: np.ndarray
    true_admissible: np.ndarray

    @property
    def n_mechanisms(self) -> int:
        return self.means.shape[0]

    @property
    def n_orientations(self) -> int:
        return self.means.shape[1]

    @property
    def n_interventions(self) -> int:
        return self.means.shape[2]

    @property
    def n_equivalence_classes(self) -> int:
        return len(self.class_representative)

    @property
    def n_true_equivalence_classes(self) -> int:
        return len(self.true_class_representative)

    def observe(self, orientation: int, intervention: int, rng: np.random.Generator) -> float:
        mu = self.actual_means[self.true_h, orientation, intervention]
        sigma = self.nominal_sigma[orientation, intervention]
        if self.perturbation_scale > 0:
            mu = mu + rng.normal(
                0.0,
                self.perturbation_scale * self.stability[orientation] * sigma,
            )
        return float(rng.normal(mu, sigma))

    def canonical_action(self, orientation: int, intervention: int) -> tuple[int, int]:
        cls = int(self.orientation_class[orientation])
        rep = int(self.class_representative[cls])
        ca = int(self.to_canonical_intervention[orientation, intervention])
        return rep, ca

    def transport_observation(
        self, orientation: int, intervention: int, y_raw: float
    ) -> tuple[int, int, float, float]:
        rep, ca = self.canonical_action(orientation, intervention)
        scale = float(self.transform_scale[orientation])
        offset = float(self.transform_offset[orientation])
        y_can = (float(y_raw) - offset) / scale
        sigma_can = float(self.nominal_sigma[orientation, intervention]) / abs(scale)
        return rep, ca, y_can, sigma_can


def _base_components(cfg: BenchmarkConfig, rng: np.random.Generator):
    H, O, A, D = cfg.n_mechanisms, cfg.n_orientations, cfg.n_interventions, cfg.latent_dim
    mech = rng.normal(size=(H, D))
    mech -= mech.mean(axis=0, keepdims=True)
    mech /= mech.std(axis=0, keepdims=True) + 1e-9
    orient_vec = rng.normal(size=(O, D))
    orient_vec /= np.linalg.norm(orient_vec, axis=1, keepdims=True) + 1e-12
    intervention_vec = rng.normal(size=(A, D))
    intervention_vec /= np.linalg.norm(intervention_vec, axis=1, keepdims=True) + 1e-12
    baseline = rng.normal(0.0, 0.5, size=(O, A))
    return mech, orient_vec, intervention_vec, baseline


def _costs(cfg: BenchmarkConfig, rng: np.random.Generator, O: int, A: int):
    orientation_cost = rng.lognormal(mean=0.0, sigma=cfg.cost_spread, size=O)
    intervention_cost = rng.lognormal(mean=-0.2, sigma=0.35, size=A)
    cost = orientation_cost[:, None] * intervention_cost[None, :]
    return cost / np.median(cost)


def _identity_structure(O: int, A: int):
    orientation_class = np.arange(O, dtype=int)
    reps = np.arange(O, dtype=int)
    mapping = np.tile(np.arange(A, dtype=int), (O, 1))
    scale = np.ones(O, dtype=float)
    offset = np.zeros(O, dtype=float)
    admissible = np.ones(O, dtype=bool)
    return orientation_class, reps, mapping, scale, offset, admissible


def _apply_equivalence_structure(
    cfg: BenchmarkConfig,
    rng: np.random.Generator,
    means: np.ndarray,
    sigma: np.ndarray,
):
    H, O, A = means.shape
    C = min(cfg.n_equivalence_classes, O)
    orientation_class = np.arange(O, dtype=int) % C
    reps = np.arange(C, dtype=int)
    mapping = np.empty((O, A), dtype=int)
    scale = np.ones(O, dtype=float)
    offset = np.zeros(O, dtype=float)

    canonical_means = means[:, reps, :].copy()
    canonical_sigma = sigma[reps, :].copy()

    for o in range(O):
        c = int(orientation_class[o])
        if o == reps[c]:
            perm = np.arange(A, dtype=int)
            s = 1.0
            b = 0.0
        else:
            perm = rng.permutation(A)
            s = float(rng.lognormal(mean=0.0, sigma=cfg.transform_scale_spread))
            b = float(rng.normal(0.0, cfg.transform_offset_scale))
        mapping[o] = perm
        scale[o] = s
        offset[o] = b
        means[:, o, :] = b + s * canonical_means[:, c, perm]
        sigma[o, :] = abs(s) * canonical_sigma[c, perm]

    admissible = np.ones(O, dtype=bool)
    return orientation_class, reps, mapping, scale, offset, admissible


def _false_split(
    orientation_class: np.ndarray,
    reps: np.ndarray,
    mapping: np.ndarray,
    scale: np.ndarray,
    offset: np.ndarray,
    rate: float,
    rng: np.random.Generator,
):
    if rate <= 0:
        return orientation_class, reps, mapping, scale, offset
    oc = orientation_class.copy()
    reps_list = list(map(int, reps))
    mp = mapping.copy()
    sc = scale.copy()
    off = offset.copy()
    redundant = np.array([o for o in range(len(oc)) if o != reps[oc[o]]], dtype=int)
    n = int(round(rate * len(redundant)))
    if n <= 0:
        return oc, np.asarray(reps_list, dtype=int), mp, sc, off
    chosen = rng.choice(redundant, size=min(n, len(redundant)), replace=False)
    A = mp.shape[1]
    for o in chosen:
        new_c = len(reps_list)
        oc[o] = new_c
        reps_list.append(int(o))
        mp[o] = np.arange(A, dtype=int)
        sc[o] = 1.0
        off[o] = 0.0
    return oc, np.asarray(reps_list, dtype=int), mp, sc, off


def _false_merge(
    orientation_class: np.ndarray,
    reps: np.ndarray,
    rate: float,
    rng: np.random.Generator,
):
    """Incorrectly merge distinct declared classes without repairing transports."""
    C = len(reps)
    if rate <= 0 or C <= 1:
        return orientation_class, reps
    n_sources = min(C - 1, int(round(rate * C)))
    if n_sources <= 0:
        return orientation_class, reps

    sources = rng.choice(np.arange(1, C), size=n_sources, replace=False)
    parent = np.arange(C, dtype=int)
    for src in sources:
        candidates = np.array([c for c in range(C) if c != src and c not in sources], dtype=int)
        if len(candidates) == 0:
            candidates = np.array([0], dtype=int)
        parent[src] = int(rng.choice(candidates))

    roots = sorted(set(int(parent[c]) for c in range(C)))
    new_id = {root: i for i, root in enumerate(roots)}
    new_oc = np.empty_like(orientation_class)
    for o, c in enumerate(orientation_class):
        root = int(parent[int(c)])
        new_oc[o] = new_id[root]
    new_reps = np.asarray([int(reps[root]) for root in roots], dtype=int)
    return new_oc, new_reps


def _corrupt_metadata(
    cfg: BenchmarkConfig,
    rng: np.random.Generator,
    orientation_class: np.ndarray,
    reps: np.ndarray,
    mapping: np.ndarray,
    scale: np.ndarray,
    offset: np.ndarray,
    admissible: np.ndarray,
    true_admissible: np.ndarray,
):
    oc, rp, mp, sc, off = _false_split(
        orientation_class, reps, mapping, scale, offset,
        cfg.metadata_false_split_rate, rng,
    )
    oc, rp = _false_merge(oc, rp, cfg.metadata_false_merge_rate, rng)

    adm = admissible.copy()
    invalid = np.where(~true_admissible)[0]
    valid = np.where(true_admissible)[0]
    if cfg.admissibility_false_positive_rate > 0 and len(invalid):
        n = min(len(invalid), int(round(cfg.admissibility_false_positive_rate * len(invalid))))
        if n > 0:
            chosen = rng.choice(invalid, size=n, replace=False)
            adm[chosen] = True
    if cfg.admissibility_false_negative_rate > 0 and len(valid):
        # Keep orientation 0 available when possible so a total blackout is not a trivial artifact.
        candidates = valid[valid != 0]
        n = min(len(candidates), int(round(cfg.admissibility_false_negative_rate * len(valid))))
        if n > 0 and len(candidates):
            chosen = rng.choice(candidates, size=min(n, len(candidates)), replace=False)
            adm[chosen] = False

    if cfg.transport_metadata_noise > 0:
        nonrep = np.array([o for o in range(len(oc)) if o != rp[oc[o]]], dtype=int)
        if len(nonrep):
            sc[nonrep] *= np.exp(rng.normal(0.0, cfg.transport_metadata_noise, size=len(nonrep)))
            off[nonrep] += rng.normal(0.0, cfg.transport_metadata_noise, size=len(nonrep))

    return oc, rp, mp, sc, off, adm


def generate_world(cfg: BenchmarkConfig, seed: int) -> RelationalWorld:
    cfg.validate()
    rng = np.random.default_rng(seed)
    H, O, A = cfg.n_mechanisms, cfg.n_orientations, cfg.n_interventions
    mech, orient_vec, intervention_vec, baseline = _base_components(cfg, rng)

    raw_exposure = rng.beta(1.4, 1.4, size=O)
    raw_exposure[0] = 0.0
    exposure = cfg.exposure_scale * raw_exposure
    means = np.empty((H, O, A), dtype=float)

    for o in range(O):
        for a in range(A):
            probe = orient_vec[o] * (0.35 + 0.65 * np.abs(intervention_vec[a]))
            means[:, o, a] = baseline[o, a] + exposure[o] * (mech @ probe)

    exp_norm = exposure / (exposure.max() + 1e-12)
    independent = rng.lognormal(mean=-0.3, sigma=0.55, size=O)
    stability = (
        cfg.exposure_instability_correlation * (0.2 + 2.2 * exp_norm)
        + (1.0 - cfg.exposure_instability_correlation) * independent
    )
    stability = np.clip(stability, 0.05, None)
    nominal_sigma = np.full((O, A), cfg.base_noise, dtype=float)
    cost = _costs(cfg, rng, O, A)

    orientation_class, reps, mapping, scale, offset, admissible = _identity_structure(O, A)

    if cfg.world_regime == "standard":
        means[:, 0, :] = baseline[0, :][None, :]
        stability[0] = min(stability[0], 0.25)

    elif cfg.world_regime == "no_orientation_value":
        template = means[:, 1 if O > 1 else 0, :].copy()
        for o in range(O):
            means[:, o, :] = template
        exposure[:] = float(np.mean(exposure[1:])) if O > 1 else 1.0
        stability[:] = 1.0
        cost[:] = 1.0

    elif cfg.world_regime == "informative_unstable":
        means[:, 0, :] = baseline[0, :][None, :]
        stability[0] = 0.2
        if O > 1:
            center = means[:, 1, :].mean(axis=0, keepdims=True)
            means[:, 1, :] = center + 3.5 * (means[:, 1, :] - center)
            exposure[1] = max(exposure.max(), cfg.exposure_scale * 2.5)
            stability[1] = 8.0
        if O > 2:
            stability[2:] = np.clip(stability[2:], 0.2, 1.4)

    elif cfg.world_regime == "orientation_exclusive":
        groups = np.arange(H) // 2
        group_signal = rng.normal(size=(groups.max() + 1, A))
        means[:, 0, :] = group_signal[groups]
        exposure[0] = 0.5
        stability[0] = 0.3
        if O > 1:
            pair_sign = np.where(np.arange(H) % 2 == 0, -1.0, 1.0)[:, None]
            group_base = rng.normal(0.0, 0.4, size=(groups.max() + 1, A))[groups]
            sep = (1.25 + 0.25 * np.arange(A)[None, :] / max(1, A - 1))
            means[:, 1, :] = group_base + pair_sign * sep
            exposure[1] = max(exposure[1], cfg.exposure_scale)
            stability[1] = min(stability[1], 0.8)

    elif cfg.world_regime == "equivalent_redundancy":
        means[:, 0, :] = baseline[0, :][None, :]
        orientation_class, reps, mapping, scale, offset, admissible = _apply_equivalence_structure(
            cfg, rng, means, nominal_sigma
        )

    elif cfg.world_regime == "asymmetric_invalid":
        means[:, 0, :] = baseline[0, :][None, :]
        n_invalid = max(1, int(round(O * cfg.invalid_orientation_fraction)))
        invalid_idx = np.arange(1, min(O, n_invalid + 1), dtype=int)
        admissible[invalid_idx] = False
        for o in invalid_idx:
            center = means[:, o, :].mean(axis=0, keepdims=True)
            means[:, o, :] = center + 5.0 * (means[:, o, :] - center)
            nominal_sigma[o, :] *= 0.7
            stability[o] = max(stability[o], 5.0)

    actual_means = means.copy()
    if cfg.world_regime == "asymmetric_invalid":
        invalid_idx = np.where(~admissible)[0]
        wrong_map = (np.arange(H) + 1) % H
        for o in invalid_idx:
            actual_means[:, o, :] = means[wrong_map, o, :]

    # Freeze true structure before injecting classifier error.
    true_oc = orientation_class.copy()
    true_reps = reps.copy()
    true_mapping = mapping.copy()
    true_scale = scale.copy()
    true_offset = offset.copy()
    true_admissible = admissible.copy()

    # Freeze the hidden mechanism before metadata corruption so corruption-rate
    # sweeps are paired on the exact same underlying world.
    true_h = int(rng.integers(H))
    corruption_rng = np.random.default_rng(seed * 1000003 + 77031)
    orientation_class, reps, mapping, scale, offset, admissible = _corrupt_metadata(
        cfg, corruption_rng,
        orientation_class, reps, mapping, scale, offset, admissible, true_admissible,
    )

    return RelationalWorld(
        means=means,
        actual_means=actual_means,
        nominal_sigma=nominal_sigma,
        stability=stability,
        cost=cost,
        exposure=exposure,
        true_h=true_h,
        perturbation_scale=cfg.perturbation_scale,
        seed=seed,
        regime=cfg.world_regime,
        orientation_class=orientation_class,
        class_representative=reps,
        to_canonical_intervention=mapping,
        transform_scale=scale,
        transform_offset=offset,
        admissible=admissible,
        true_orientation_class=true_oc,
        true_class_representative=true_reps,
        true_to_canonical_intervention=true_mapping,
        true_transform_scale=true_scale,
        true_transform_offset=true_offset,
        true_admissible=true_admissible,
    )
