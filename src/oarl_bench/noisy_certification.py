"""Precision-first finite-noise orientation certification for OARL v0.5B.

This module deliberately does not read hidden orientation classes or transport
metadata. It asks whether an affine/permutation transport can be supported by
finite predictive evidence from the candidate likelihood family.

The safety asymmetry is intentional: false merges are substantially more
dangerous than missed compression. Low-signal, assignment-ambiguous, unstable,
or weakly validated pairs therefore return UNKNOWN and are never quotiented.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from statistics import NormalDist
import time

import numpy as np
from scipy.optimize import linear_sum_assignment

from .certification import CertificateStatus
from .world import RelationalWorld


@dataclass(frozen=True)
class PredictiveSummary:
    """Sufficient statistics from n finite Gaussian predictive samples/cell."""

    mean: np.ndarray
    sd: np.ndarray
    n_samples: int


@dataclass(frozen=True)
class NoisyPairCertificate:
    target: int
    reference: int
    status: CertificateStatus
    intervention_map: np.ndarray
    scale: float
    offset: float
    signal_target_z: float
    signal_reference_z: float
    assignment_max_distance: float
    assignment_min_gap: float
    validation_upper_z: float
    validation_lower_z: float
    sigma_upper_log_error: float
    scale_stability: float
    scale_reciprocity_error: float
    offset_stability_z: float
    offset_reciprocity_z: float
    comparisons: int
    reason: str


@dataclass(frozen=True)
class NoisyStructureDiscovery:
    orientation_class: np.ndarray
    class_representative: np.ndarray
    to_canonical_intervention: np.ndarray
    transform_scale: np.ndarray
    transform_offset: np.ndarray
    admissible: np.ndarray
    certificates: tuple[NoisyPairCertificate, ...]
    comparisons: int
    runtime_s: float
    n_samples_per_split: int
    certificate_seed: int

    @property
    def n_classes(self) -> int:
        return len(self.class_representative)

    @property
    def n_equivalent_certificates(self) -> int:
        return sum(c.status is CertificateStatus.EQUIVALENT for c in self.certificates)

    @property
    def n_distinct_certificates(self) -> int:
        return sum(c.status is CertificateStatus.DISTINCT for c in self.certificates)

    @property
    def n_unknown_certificates(self) -> int:
        return sum(c.status is CertificateStatus.UNKNOWN for c in self.certificates)


@dataclass(frozen=True)
class _Proposal:
    mapping: np.ndarray
    scale: float
    offset: float
    signal_target_z: float
    signal_reference_z: float
    assignment_max_distance: float
    assignment_min_gap: float


def draw_predictive_summary(
    world: RelationalWorld,
    n_samples: int,
    rng: np.random.Generator,
) -> PredictiveSummary:
    """Draw exact Gaussian sufficient statistics without materializing all samples.

    For Normal(mu, sigma), sample mean and sample variance are independent with
    known sampling distributions. Drawing those sufficient statistics is
    exactly equivalent, for this certifier, to drawing n_samples IID values and
    reducing them to mean and standard deviation.
    """

    if n_samples < 3:
        raise ValueError("n_samples must be >= 3")
    H, O, A = world.means.shape
    sigma = world.nominal_sigma[None, :, :]
    sample_mean = world.means + rng.normal(size=(H, O, A)) * sigma / np.sqrt(n_samples)
    chi = rng.chisquare(n_samples - 1, size=(H, O, A))
    sample_sd = sigma * np.sqrt(chi / (n_samples - 1))
    return PredictiveSummary(sample_mean, sample_sd, int(n_samples))


def _unit_signatures(means: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    center = means.mean(axis=0)
    centered = means - center[None, :]
    norms = np.linalg.norm(centered, axis=0)
    unit = np.zeros_like(centered)
    valid = norms > 1e-12
    unit[:, valid] = centered[:, valid] / norms[valid][None, :]
    return unit, norms, center


def _proposal(
    means_target: np.ndarray,
    sd_target: np.ndarray,
    means_reference: np.ndarray,
    sd_reference: np.ndarray,
    *,
    min_signal_z: float,
    min_assignment_gap: float,
) -> _Proposal | None:
    mt = np.asarray(means_target, dtype=float)
    mr = np.asarray(means_reference, dtype=float)
    st = np.asarray(sd_target, dtype=float)
    sr = np.asarray(sd_reference, dtype=float)
    if mt.shape != mr.shape or mt.ndim != 2:
        raise ValueError("means must share H x A shape")
    if st.shape != mt.shape or sr.shape != mr.shape:
        raise ValueError("sample standard deviations must share H x A shape")

    _, A = mt.shape
    ut, nt, ct = _unit_signatures(mt)
    ur, nr, cr = _unit_signatures(mr)
    pooled_t = np.sqrt(np.mean(st * st, axis=0))
    pooled_r = np.sqrt(np.mean(sr * sr, axis=0))

    signal_t = float(
        np.sqrt(np.mean((mt - mt.mean(axis=0, keepdims=True)) ** 2))
        / max(float(np.median(pooled_t)), 1e-12)
    )
    signal_r = float(
        np.sqrt(np.mean((mr - mr.mean(axis=0, keepdims=True)) ** 2))
        / max(float(np.median(pooled_r)), 1e-12)
    )
    if min(signal_t, signal_r) < min_signal_z:
        return None

    distance = np.linalg.norm(ut[:, :, None] - ur[:, None, :], axis=0)
    rows, cols = linear_sum_assignment(distance)
    mapping = np.empty(A, dtype=int)
    mapping[rows] = cols

    gaps = []
    for a in range(A):
        matched = float(distance[a, mapping[a]])
        if A == 1:
            gap = float("inf")
        else:
            alternatives = np.delete(distance[a], mapping[a])
            gap = float(np.min(alternatives) - matched)
        gaps.append(gap)
    assignment_min_gap = float(np.min(gaps))
    if assignment_min_gap < min_assignment_gap:
        return None

    valid_scale = (nt > 1e-10) & (nr[mapping] > 1e-10)
    if int(np.sum(valid_scale)) < max(2, A // 2):
        return None
    ratios = nt[valid_scale] / nr[mapping[valid_scale]]
    scale = float(np.median(ratios))
    if not np.isfinite(scale) or scale <= 0.0:
        return None
    offsets = ct - scale * cr[mapping]
    offset = float(np.median(offsets))
    assignment_max = float(np.max(distance[np.arange(A), mapping]))

    return _Proposal(
        mapping=mapping,
        scale=scale,
        offset=offset,
        signal_target_z=signal_t,
        signal_reference_z=signal_r,
        assignment_max_distance=assignment_max,
        assignment_min_gap=assignment_min_gap,
    )


def _empty_certificate(
    target: int,
    reference: int,
    status: CertificateStatus,
    reason: str,
    A: int,
    comparisons: int,
) -> NoisyPairCertificate:
    return NoisyPairCertificate(
        target=int(target),
        reference=int(reference),
        status=status,
        intervention_map=np.arange(A, dtype=int),
        scale=1.0,
        offset=0.0,
        signal_target_z=float("nan"),
        signal_reference_z=float("nan"),
        assignment_max_distance=float("inf"),
        assignment_min_gap=float("-inf"),
        validation_upper_z=float("inf"),
        validation_lower_z=0.0,
        sigma_upper_log_error=float("inf"),
        scale_stability=float("inf"),
        scale_reciprocity_error=float("inf"),
        offset_stability_z=float("inf"),
        offset_reciprocity_z=float("inf"),
        comparisons=int(comparisons),
        reason=reason,
    )


def certify_pair_noisy(
    fit: PredictiveSummary,
    validation: PredictiveSummary,
    target: int,
    reference: int,
    *,
    min_signal_z: float = 0.12,
    min_assignment_gap: float = 0.01,
    equivalence_margin_z: float = 0.55,
    sigma_relative_margin: float = 0.25,
    assignment_margin: float = 0.40,
    scale_stability_margin: float = 0.15,
    offset_stability_margin_z: float = 0.25,
    alpha: float = 1e-3,
    distinct_margin_z: float = 1.0,
) -> NoisyPairCertificate:
    """Cross-fit a conservative finite-noise equivalence certificate.

    EQUIVALENT requires useful mechanism signal, a non-ambiguous intervention
    assignment, replication of the same bijection on an independent validation
    sample, exact inverse recovery in both reverse fits, stable/reciprocal affine
    parameters, simultaneous response confidence bounds inside the equivalence
    envelope, and compatible predictive noise scales.

    Failure of an equivalence condition normally yields UNKNOWN, not DISTINCT.
    DISTINCT is reserved for a stable mapping whose validation residual is
    confidently outside distinct_margin_z.
    """

    if fit.n_samples != validation.n_samples:
        raise ValueError("fit and validation summaries must use the same n_samples")
    if fit.mean.shape != validation.mean.shape or fit.sd.shape != validation.sd.shape:
        raise ValueError("fit and validation summaries must share shapes")
    H, O, A = fit.mean.shape
    if not (0 <= target < O and 0 <= reference < O and target != reference):
        raise ValueError("target/reference must be distinct valid orientations")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")

    n = fit.n_samples
    comparisons = int(4 * H * A * A + H * A)
    proposal_kwargs = {
        "min_signal_z": min_signal_z,
        "min_assignment_gap": min_assignment_gap,
    }
    pf = _proposal(
        fit.mean[:, target, :], fit.sd[:, target, :],
        fit.mean[:, reference, :], fit.sd[:, reference, :],
        **proposal_kwargs,
    )
    pv = _proposal(
        validation.mean[:, target, :], validation.sd[:, target, :],
        validation.mean[:, reference, :], validation.sd[:, reference, :],
        **proposal_kwargs,
    )
    prf = _proposal(
        fit.mean[:, reference, :], fit.sd[:, reference, :],
        fit.mean[:, target, :], fit.sd[:, target, :],
        **proposal_kwargs,
    )
    prv = _proposal(
        validation.mean[:, reference, :], validation.sd[:, reference, :],
        validation.mean[:, target, :], validation.sd[:, target, :],
        **proposal_kwargs,
    )
    if any(p is None for p in (pf, pv, prf, prv)):
        return _empty_certificate(
            target, reference, CertificateStatus.UNKNOWN,
            "insufficient signal, unstable scale, or ambiguous intervention assignment",
            A, comparisons,
        )
    assert pf is not None and pv is not None and prf is not None and prv is not None

    inverse = np.empty(A, dtype=int)
    inverse[pf.mapping] = np.arange(A, dtype=int)
    map_consistent = (
        np.array_equal(pv.mapping, pf.mapping)
        and np.array_equal(prf.mapping, inverse)
        and np.array_equal(prv.mapping, inverse)
    )
    if not map_consistent:
        return _empty_certificate(
            target, reference, CertificateStatus.UNKNOWN,
            "intervention mapping did not replicate bidirectionally", A, comparisons,
        )

    assignment_max = float(max(
        pf.assignment_max_distance,
        pv.assignment_max_distance,
        prf.assignment_max_distance,
        prv.assignment_max_distance,
    ))
    assignment_min_gap_observed = float(min(
        pf.assignment_min_gap,
        pv.assignment_min_gap,
        prf.assignment_min_gap,
        prv.assignment_min_gap,
    ))
    scale_stability = float(abs(pv.scale - pf.scale) / max(abs(pf.scale), 1e-12))
    scale_reciprocity = float(max(
        abs(pf.scale * prf.scale - 1.0),
        abs(pv.scale * prv.scale - 1.0),
    ))

    pooled_val_t = np.sqrt(np.mean(validation.sd[:, target, :] ** 2, axis=0))
    pooled_val_r = np.sqrt(np.mean(validation.sd[:, reference, :] ** 2, axis=0))
    noise_scale = max(float(np.median(pooled_val_t)), 1e-12)
    offset_stability = float(abs(pv.offset - pf.offset) / noise_scale)
    offset_reciprocity = float(max(
        abs(prf.offset + prf.scale * pf.offset),
        abs(prv.offset + prv.scale * pv.offset),
    ) / max(float(np.median(pooled_val_r)), 1e-12))

    mt = validation.mean[:, target, :]
    mr = validation.mean[:, reference, :]
    st = validation.sd[:, target, :]
    sr = validation.sd[:, reference, :]
    predicted = pf.offset + pf.scale * mr[:, pf.mapping]
    delta = mt - predicted
    se = np.sqrt((st * st) / n + (pf.scale * sr[:, pf.mapping]) ** 2 / n)
    zcrit = NormalDist().inv_cdf(1.0 - alpha / (2.0 * H * A))
    upper = (np.abs(delta) + zcrit * se) / np.maximum(st, 1e-12)
    lower = np.maximum(np.abs(delta) - zcrit * se, 0.0) / np.maximum(st, 1e-12)
    validation_upper = float(np.max(upper))
    validation_lower = float(np.max(lower))

    sigma_log_error = np.abs(np.log(
        np.maximum(pooled_val_t, 1e-12)
        / np.maximum(abs(pf.scale) * pooled_val_r[pf.mapping], 1e-12)
    ))
    effective_df = max(1, H * (n - 1))
    sigma_se_log = np.sqrt(1.0 / effective_df)
    zsig = NormalDist().inv_cdf(1.0 - alpha / (2.0 * A))
    sigma_upper = float(np.max(sigma_log_error + zsig * sigma_se_log))

    equivalent = (
        assignment_max <= assignment_margin
        and assignment_min_gap_observed >= min_assignment_gap
        and scale_stability <= scale_stability_margin
        and scale_reciprocity <= scale_stability_margin
        and offset_stability <= offset_stability_margin_z
        and offset_reciprocity <= offset_stability_margin_z
        and validation_upper <= equivalence_margin_z
        and sigma_upper <= np.log1p(sigma_relative_margin)
    )

    if equivalent:
        status = CertificateStatus.EQUIVALENT
        reason = "all cross-fit equivalence gates passed"
    elif validation_lower >= distinct_margin_z:
        status = CertificateStatus.DISTINCT
        reason = "stable mapping but validation residual is confidently distinct"
    else:
        status = CertificateStatus.UNKNOWN
        reason = "equivalence not established at the frozen safety margins"

    return NoisyPairCertificate(
        target=int(target),
        reference=int(reference),
        status=status,
        intervention_map=pf.mapping.copy(),
        scale=float(pf.scale),
        offset=float(pf.offset),
        signal_target_z=float(pf.signal_target_z),
        signal_reference_z=float(pf.signal_reference_z),
        assignment_max_distance=assignment_max,
        assignment_min_gap=assignment_min_gap_observed,
        validation_upper_z=validation_upper,
        validation_lower_z=validation_lower,
        sigma_upper_log_error=sigma_upper,
        scale_stability=scale_stability,
        scale_reciprocity_error=scale_reciprocity,
        offset_stability_z=offset_stability,
        offset_reciprocity_z=offset_reciprocity,
        comparisons=comparisons,
        reason=reason,
    )


def discover_noisy_structure(
    world: RelationalWorld,
    *,
    n_samples: int = 2000,
    certificate_seed: int | None = None,
    admissible: np.ndarray | None = None,
    **certificate_kwargs,
) -> NoisyStructureDiscovery:
    """Discover a quotient from two independent finite predictive samples.

    Only EQUIVALENT certificates cause a merge. DISTINCT and UNKNOWN both retain
    separate orientations, implementing the v0.4 safety asymmetry.
    """

    t0 = time.perf_counter()
    O, A = world.n_orientations, world.n_interventions
    adm = np.asarray(world.admissible if admissible is None else admissible, dtype=bool).copy()
    if adm.shape != (O,):
        raise ValueError("admissible must have shape (n_orientations,)")
    if certificate_seed is None:
        certificate_seed = int(world.seed * 1000003 + 505021)
    rng = np.random.default_rng(certificate_seed)
    fit = draw_predictive_summary(world, n_samples, rng)
    validation = draw_predictive_summary(world, n_samples, rng)

    orientation_class = np.full(O, -1, dtype=int)
    reps: list[int] = []
    mapping = np.tile(np.arange(A, dtype=int), (O, 1))
    scale = np.ones(O, dtype=float)
    offset = np.zeros(O, dtype=float)
    certificates: list[NoisyPairCertificate] = []
    comparisons = 0

    for o in range(O):
        if not adm[o]:
            orientation_class[o] = len(reps)
            reps.append(o)
            continue
        assigned = False
        for c, rep in enumerate(reps):
            if not adm[rep]:
                continue
            cert = certify_pair_noisy(fit, validation, o, rep, **certificate_kwargs)
            certificates.append(cert)
            comparisons += cert.comparisons
            if cert.status is CertificateStatus.EQUIVALENT:
                orientation_class[o] = c
                mapping[o] = cert.intervention_map
                scale[o] = cert.scale
                offset[o] = cert.offset
                assigned = True
                break
        if not assigned:
            orientation_class[o] = len(reps)
            reps.append(o)
            mapping[o] = np.arange(A, dtype=int)
            scale[o] = 1.0
            offset[o] = 0.0

    return NoisyStructureDiscovery(
        orientation_class=orientation_class,
        class_representative=np.asarray(reps, dtype=int),
        to_canonical_intervention=mapping,
        transform_scale=scale,
        transform_offset=offset,
        admissible=adm,
        certificates=tuple(certificates),
        comparisons=int(comparisons),
        runtime_s=float(time.perf_counter() - t0),
        n_samples_per_split=int(n_samples),
        certificate_seed=int(certificate_seed),
    )


def apply_noisy_discovered_structure(
    world: RelationalWorld,
    discovery: NoisyStructureDiscovery,
) -> RelationalWorld:
    return replace(
        world,
        orientation_class=discovery.orientation_class.copy(),
        class_representative=discovery.class_representative.copy(),
        to_canonical_intervention=discovery.to_canonical_intervention.copy(),
        transform_scale=discovery.transform_scale.copy(),
        transform_offset=discovery.transform_offset.copy(),
        admissible=discovery.admissible.copy(),
    )


def noisy_structure_metrics(
    world: RelationalWorld,
    discovery: NoisyStructureDiscovery,
) -> dict[str, float]:
    O = world.n_orientations
    tp = fp = fn = tn = 0
    for i in range(O):
        for j in range(i + 1, O):
            truth = bool(
                world.true_admissible[i]
                and world.true_admissible[j]
                and world.true_orientation_class[i] == world.true_orientation_class[j]
            )
            pred = bool(
                discovery.admissible[i]
                and discovery.admissible[j]
                and discovery.orientation_class[i] == discovery.orientation_class[j]
            )
            if truth and pred:
                tp += 1
            elif (not truth) and pred:
                fp += 1
            elif truth and (not pred):
                fn += 1
            else:
                tn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    return {
        "pair_tp": float(tp),
        "pair_fp": float(fp),
        "pair_fn": float(fn),
        "pair_tn": float(tn),
        "pair_precision": float(precision),
        "pair_recall": float(recall),
        "compression_fraction": float(1.0 - discovery.n_classes / O),
        "equivalent_certificates": float(discovery.n_equivalent_certificates),
        "distinct_certificates": float(discovery.n_distinct_certificates),
        "unknown_certificates": float(discovery.n_unknown_certificates),
    }
