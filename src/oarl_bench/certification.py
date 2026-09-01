"""Conservative discovery of exact orientation equivalence from likelihood geometry.

v0.5A deliberately solves the exact, model-family case first. It does not infer
physical/semantic admissibility. Given a candidate mechanism likelihood family,
it asks whether two orientations differ only by:

* a permutation of intervention labels; and
* one positive affine readout transform y_target = offset + scale * y_reference.

Anything that cannot be established at the requested tolerance remains distinct
(or UNKNOWN at the pair-certificate level) rather than being merged.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import time

import numpy as np

from .world import RelationalWorld


class CertificateStatus(str, Enum):
    EQUIVALENT = "equivalent"
    DISTINCT = "distinct"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PairCertificate:
    target: int
    reference: int
    status: CertificateStatus
    intervention_map: np.ndarray
    scale: float
    offset: float
    assignment_max_distance: float
    response_rms_z: float
    response_max_z: float
    scale_relative_spread: float
    sigma_log_error: float
    comparisons: int


@dataclass(frozen=True)
class StructureDiscovery:
    orientation_class: np.ndarray
    class_representative: np.ndarray
    to_canonical_intervention: np.ndarray
    transform_scale: np.ndarray
    transform_offset: np.ndarray
    admissible: np.ndarray
    certificates: tuple[PairCertificate, ...]
    comparisons: int
    runtime_s: float

    @property
    def n_classes(self) -> int:
        return len(self.class_representative)


def _unit_signatures(means: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return mechanism-centered unit signatures for each intervention."""
    center = means.mean(axis=0)
    centered = means - center[None, :]
    norms = np.linalg.norm(centered, axis=0)
    unit = np.zeros_like(centered)
    valid = norms > 1e-12
    unit[:, valid] = centered[:, valid] / norms[valid][None, :]
    return unit, norms, center


def certify_pair_exact(
    means_target: np.ndarray,
    sigma_target: np.ndarray,
    means_reference: np.ndarray,
    sigma_reference: np.ndarray,
    *,
    target: int = -1,
    reference: int = -1,
    equivalence_tol: float = 1e-8,
    distinct_tol: float = 5e-3,
) -> PairCertificate:
    """Discover and test a candidate exact transport between two orientations."""
    mt = np.asarray(means_target, dtype=float)
    mr = np.asarray(means_reference, dtype=float)
    st = np.asarray(sigma_target, dtype=float)
    sr = np.asarray(sigma_reference, dtype=float)
    if mt.shape != mr.shape or mt.ndim != 2:
        raise ValueError("means_target and means_reference must have the same H x A shape")
    if st.shape != sr.shape or st.shape != (mt.shape[1],):
        raise ValueError("sigma arrays must both have shape (A,)")

    H, A = mt.shape
    ut, nt, ct = _unit_signatures(mt)
    ur, nr, cr = _unit_signatures(mr)

    dist = np.linalg.norm(ut[:, :, None] - ur[:, None, :], axis=0)
    flat_target = bool(np.all(nt <= 1e-12))
    flat_reference = bool(np.all(nr <= 1e-12))

    if flat_target and flat_reference:
        # A positive affine transform preserves rank ordering, so the deliberately
        # mechanism-flat class can still recover its intervention permutation.
        order_t = np.argsort(ct)
        order_r = np.argsort(cr)
        mapping = np.empty(A, dtype=int)
        mapping[order_t] = order_r
        sigma_ratios = st / np.maximum(sr[mapping], 1e-12)
        scale = float(np.median(sigma_ratios))
        scale_spread = float(
            np.max(np.abs(sigma_ratios - scale)) / max(abs(scale), 1e-12)
        )
        matched_dist = np.abs(
            np.log(np.maximum(st, 1e-12) / np.maximum(scale * sr[mapping], 1e-12))
        )
        bijective = True
    else:
        mapping = np.argmin(dist, axis=1).astype(int)
        matched_dist = dist[np.arange(A), mapping]
        bijective = len(np.unique(mapping)) == A

        valid_scale = (nr[mapping] > 1e-12) & (nt > 1e-12)
        if np.any(valid_scale):
            ratios = nt[valid_scale] / nr[mapping[valid_scale]]
            scale = float(np.median(ratios))
            scale_spread = float(
                np.max(np.abs(ratios - scale)) / max(abs(scale), 1e-12)
            )
        else:
            scale = 1.0
            scale_spread = float("inf")

    offsets = ct - scale * cr[mapping]
    offset = float(np.median(offsets))
    pred = offset + scale * mr[:, mapping]
    sigma_floor = np.maximum(st[None, :], 1e-12)
    z = (mt - pred) / sigma_floor
    response_rms_z = float(np.sqrt(np.mean(z * z)))
    response_max_z = float(np.max(np.abs(z)))

    sigma_pred = abs(scale) * sr[mapping]
    sigma_log_error = float(
        np.max(np.abs(np.log(np.maximum(st, 1e-12) / np.maximum(sigma_pred, 1e-12))))
    )
    assignment_max = float(np.max(matched_dist))

    equivalent = (
        bijective
        and scale > 0.0
        and assignment_max <= equivalence_tol
        and response_max_z <= equivalence_tol
        and scale_spread <= equivalence_tol
        and sigma_log_error <= equivalence_tol
    )

    clearly_distinct = (
        (not bijective and assignment_max > distinct_tol)
        or response_rms_z >= distinct_tol
        or assignment_max >= distinct_tol
        or scale_spread >= distinct_tol
        or sigma_log_error >= distinct_tol
    )

    if equivalent:
        status = CertificateStatus.EQUIVALENT
    elif clearly_distinct:
        status = CertificateStatus.DISTINCT
    else:
        status = CertificateStatus.UNKNOWN

    return PairCertificate(
        target=int(target),
        reference=int(reference),
        status=status,
        intervention_map=mapping,
        scale=scale,
        offset=offset,
        assignment_max_distance=assignment_max,
        response_rms_z=response_rms_z,
        response_max_z=response_max_z,
        scale_relative_spread=scale_spread,
        sigma_log_error=sigma_log_error,
        comparisons=int(A * A * H),
    )


def discover_exact_structure(
    world: RelationalWorld,
    *,
    equivalence_tol: float = 1e-8,
    distinct_tol: float = 5e-3,
    admissible: np.ndarray | None = None,
) -> StructureDiscovery:
    """Discover a conservative exact quotient without reading hidden truth metadata.

    Semantic/physical admissibility is not inferred here. Callers must provide a
    declared admissibility mask or accept the world's declared mask.
    """
    t0 = time.perf_counter()
    O, A = world.n_orientations, world.n_interventions
    adm = np.asarray(world.admissible if admissible is None else admissible, dtype=bool).copy()
    if adm.shape != (O,):
        raise ValueError("admissible must have shape (n_orientations,)")

    orientation_class = np.full(O, -1, dtype=int)
    reps: list[int] = []
    mapping = np.tile(np.arange(A, dtype=int), (O, 1))
    scale = np.ones(O, dtype=float)
    offset = np.zeros(O, dtype=float)
    certificates: list[PairCertificate] = []
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
            cert = certify_pair_exact(
                world.means[:, o, :],
                world.nominal_sigma[o, :],
                world.means[:, rep, :],
                world.nominal_sigma[rep, :],
                target=o,
                reference=rep,
                equivalence_tol=equivalence_tol,
                distinct_tol=distinct_tol,
            )
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

    elapsed = time.perf_counter() - t0
    return StructureDiscovery(
        orientation_class=orientation_class,
        class_representative=np.asarray(reps, dtype=int),
        to_canonical_intervention=mapping,
        transform_scale=scale,
        transform_offset=offset,
        admissible=adm,
        certificates=tuple(certificates),
        comparisons=int(comparisons),
        runtime_s=float(elapsed),
    )


def apply_discovered_structure(world: RelationalWorld, discovery: StructureDiscovery) -> RelationalWorld:
    """Return a world whose declared structure is the discovered structure."""
    return replace(
        world,
        orientation_class=discovery.orientation_class.copy(),
        class_representative=discovery.class_representative.copy(),
        to_canonical_intervention=discovery.to_canonical_intervention.copy(),
        transform_scale=discovery.transform_scale.copy(),
        transform_offset=discovery.transform_offset.copy(),
        admissible=discovery.admissible.copy(),
    )


def pairwise_structure_metrics(world: RelationalWorld, discovery: StructureDiscovery) -> dict[str, float]:
    """Evaluate discovered pairwise equivalence against hidden benchmark truth."""
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
    }
